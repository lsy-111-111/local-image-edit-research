from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from scripts.adapters.base import ImageEditRequest, ImageEditResult
from scripts.common import ensure_parent


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/axvXy8AAAAASUVORK5CYII="
)
API_URL = "https://api.openai.com/v1/images/edits"


def media_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "image/png"
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    raise ValueError(f"OpenAI image edits require PNG/JPEG/WebP assets: {path}")


def data_url(path_value: str) -> str:
    path = Path(path_value)
    if not path.is_file():
        raise ValueError(f"image file does not exist: {path}")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{media_type(path)};base64,{encoded}"


def status_from_error(exc: BaseException) -> tuple[str, str]:
    if isinstance(exc, urllib.error.HTTPError):
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 429:
            return "rate_limited", body
        if exc.code in {400, 422}:
            return "invalid_input", body
        if exc.code in {408, 504}:
            return "timeout", body
        if exc.code in {401, 403}:
            return "failed", body
        return "failed", body
    if isinstance(exc, TimeoutError):
        return "timeout", str(exc)
    return "failed", str(exc)


class OpenAIImagesAdapter:
    adapter_name = "openai_images"

    def generate(self, request: ImageEditRequest) -> ImageEditResult:
        started = time.perf_counter()
        output_path = Path(str(request.config["output_path"]))
        raw_response_path = Path(str(request.config["raw_response_path"]))
        ensure_parent(output_path)
        ensure_parent(raw_response_path)
        model = str(request.config.get("provider_model_ref") or request.config.get("model_id") or "gpt-image-1")
        dry_run = bool(request.config.get("dry_run", False))
        version_risk = str(request.config.get("version_risk") or "D_unversioned;provider_version_review_required")

        if dry_run:
            output_path.write_bytes(PNG_1X1)
            raw_response_path.write_text(
                json.dumps(
                    {
                        "adapter": self.adapter_name,
                        "model": model,
                        "dry_run": True,
                        "status": "success",
                        "note": "no OpenAI API call performed",
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

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raw_response_path.write_text('{"status":"failed","error":"OPENAI_API_KEY is not set"}\n', encoding="utf-8")
            return ImageEditResult(
                output_path=output_path.as_posix(),
                raw_response_path=raw_response_path.as_posix(),
                status="failed",
                runtime_seconds=max(time.perf_counter() - started, 0.0),
                cost_usd=0.0,
                seed_effective=request.seed,
                error="OPENAI_API_KEY is not set",
                adapter_kind="api",
                version_risk=version_risk,
                cost_estimate_status="not_available",
            )

        try:
            payload: dict[str, object] = {
                "model": model,
                "prompt": request.prompt,
                "images": [{"image_url": data_url(request.source_image)}],
                "n": 1,
                "output_format": "png",
            }
            if request.mask:
                payload["mask"] = {"image_url": data_url(request.mask)}
            http_request = urllib.request.Request(
                API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(http_request, timeout=120) as response:
                response_body = response.read().decode("utf-8")
            raw_response_path.write_text(response_body + "\n", encoding="utf-8")
            parsed = json.loads(response_body)
            image_b64 = (parsed.get("data") or [{}])[0].get("b64_json", "")
            if not image_b64:
                raise ValueError("OpenAI response did not include data[0].b64_json")
            output_path.write_bytes(base64.b64decode(image_b64))
            request_id = str(parsed.get("id") or "")
            cost_status = "usage_present_no_pricing_applied" if parsed.get("usage") else "no_pricing_applied"
            return ImageEditResult(
                output_path=output_path.as_posix(),
                raw_response_path=raw_response_path.as_posix(),
                status="success",
                runtime_seconds=max(time.perf_counter() - started, 0.0),
                cost_usd=0.0,
                seed_effective=request.seed,
                adapter_kind="api",
                provider_request_id=request_id,
                version_risk=version_risk,
                cost_estimate_status=cost_status,
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
