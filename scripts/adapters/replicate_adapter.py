from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from scripts.adapters.base import ImageEditRequest, ImageEditResult
from scripts.adapters.openai_images_adapter import PNG_1X1, data_url
from scripts.common import ensure_parent


API_ROOT = "https://api.replicate.com/v1"


def status_from_error(exc: BaseException) -> tuple[str, str]:
    if isinstance(exc, urllib.error.HTTPError):
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 429:
            return "rate_limited", body
        if exc.code in {400, 422}:
            return "invalid_input", body
        if exc.code in {408, 504}:
            return "timeout", body
        return "failed", body
    if isinstance(exc, TimeoutError):
        return "timeout", str(exc)
    return "failed", str(exc)


def prediction_url(provider_model_ref: str) -> str:
    if "/" in provider_model_ref and ":" not in provider_model_ref:
        owner, name = provider_model_ref.split("/", 1)
        return f"{API_ROOT}/models/{owner}/{name}/predictions"
    return f"{API_ROOT}/predictions"


def prediction_payload(request: ImageEditRequest) -> dict[str, Any]:
    provider_model_ref = str(request.config.get("provider_model_ref") or request.config.get("model_id") or "")
    schema = str(request.config.get("input_schema_ref") or "replicate_image_prompt")
    image = data_url(request.source_image)
    input_payload: dict[str, Any] = {"prompt": request.prompt, "image": image}
    if schema == "replicate_image_mask_prompt" and request.mask:
        input_payload["mask"] = data_url(request.mask)
    if schema not in {"replicate_image_prompt", "replicate_image_mask_prompt"}:
        raise ValueError(f"unsupported Replicate input_schema_ref: {schema}")
    payload: dict[str, Any] = {"input": input_payload}
    if ":" in provider_model_ref:
        payload["version"] = provider_model_ref.split(":", 1)[1]
    return payload


def first_output_url(output: Any) -> str:
    if isinstance(output, str):
        return output
    if isinstance(output, list) and output:
        return first_output_url(output[0])
    if isinstance(output, dict):
        for key in ["url", "image", "output"]:
            if isinstance(output.get(key), str):
                return str(output[key])
    return ""


class ReplicateAdapter:
    adapter_name = "replicate"

    def generate(self, request: ImageEditRequest) -> ImageEditResult:
        started = time.perf_counter()
        output_path = Path(str(request.config["output_path"]))
        raw_response_path = Path(str(request.config["raw_response_path"]))
        ensure_parent(output_path)
        ensure_parent(raw_response_path)
        provider_model_ref = str(request.config.get("provider_model_ref") or request.config.get("model_id") or "")
        dry_run = bool(request.config.get("dry_run", False))
        version_risk = str(request.config.get("version_risk") or "D_unversioned;provider_version_review_required")

        if dry_run:
            output_path.write_bytes(PNG_1X1)
            raw_response_path.write_text(
                json.dumps(
                    {
                        "adapter": self.adapter_name,
                        "provider_model_ref": provider_model_ref,
                        "dry_run": True,
                        "status": "succeeded",
                        "note": "no Replicate API call performed",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            return ImageEditResult(
                output_path=output_path.as_posix(),
                raw_response_path=raw_response_path.as_posix(),
                status="success",
                runtime_seconds=max(time.perf_counter() - started, 0.0),
                cost_usd=0.0,
                seed_effective=request.seed,
                adapter_kind="api",
                version_risk=version_risk,
                cost_estimate_status="dry_run",
            )

        token = os.environ.get("REPLICATE_API_TOKEN")
        if not token:
            raw_response_path.write_text('{"status":"failed","error":"REPLICATE_API_TOKEN is not set"}\n', encoding="utf-8")
            return ImageEditResult(
                output_path=output_path.as_posix(),
                raw_response_path=raw_response_path.as_posix(),
                status="failed",
                runtime_seconds=max(time.perf_counter() - started, 0.0),
                cost_usd=0.0,
                seed_effective=request.seed,
                error="REPLICATE_API_TOKEN is not set",
                adapter_kind="api",
                version_risk=version_risk,
                cost_estimate_status="not_available",
            )

        try:
            payload = prediction_payload(request)
            http_request = urllib.request.Request(
                prediction_url(provider_model_ref),
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Token {token}",
                    "Content-Type": "application/json",
                    "Prefer": "wait=60",
                },
                method="POST",
            )
            with urllib.request.urlopen(http_request, timeout=180) as response:
                response_body = response.read().decode("utf-8")
            parsed = json.loads(response_body)
            raw_response_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            provider_status = str(parsed.get("status", "")).lower()
            if provider_status in {"failed", "canceled"}:
                raise RuntimeError(json.dumps(parsed.get("error") or parsed, ensure_ascii=False))
            if provider_status not in {"succeeded", "success", ""}:
                return ImageEditResult(
                    output_path=output_path.as_posix(),
                    raw_response_path=raw_response_path.as_posix(),
                    status="timeout",
                    runtime_seconds=max(time.perf_counter() - started, 0.0),
                    cost_usd=0.0,
                    seed_effective=request.seed,
                    error=f"prediction did not complete: {provider_status}",
                    adapter_kind="api",
                    provider_request_id=str(parsed.get("id") or ""),
                    version_risk=version_risk,
                    cost_estimate_status="not_available",
                )
            out_url = first_output_url(parsed.get("output"))
            if out_url.startswith("data:image/"):
                output_path.write_bytes(base64.b64decode(out_url.split(",", 1)[1]))
            elif out_url:
                with urllib.request.urlopen(out_url, timeout=120) as response:
                    output_path.write_bytes(response.read())
            else:
                raise ValueError("Replicate response did not include a downloadable output")
            metrics = parsed.get("metrics") or {}
            cost = float(metrics.get("predict_time", 0.0) or 0.0) * 0.0
            return ImageEditResult(
                output_path=output_path.as_posix(),
                raw_response_path=raw_response_path.as_posix(),
                status="success",
                runtime_seconds=max(time.perf_counter() - started, 0.0),
                cost_usd=cost,
                seed_effective=request.seed,
                adapter_kind="api",
                provider_request_id=str(parsed.get("id") or ""),
                version_risk=version_risk,
                cost_estimate_status="no_pricing_applied",
            )
        except BaseException as exc:  # noqa: BLE001 - adapter converts external failures into structured statuses.
            status, error = status_from_error(exc)
            raw_response_path.write_text(
                json.dumps({"status": status, "error": error}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return ImageEditResult(
                output_path=output_path.as_posix(),
                raw_response_path=raw_response_path.as_posix(),
                status=status,
                runtime_seconds=max(time.perf_counter() - started, 0.0),
                cost_usd=0.0,
                seed_effective=request.seed,
                error=error,
                adapter_kind="api",
                version_risk=version_risk,
                cost_estimate_status="not_available",
            )
