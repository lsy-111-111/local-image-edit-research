from __future__ import annotations

import json
import time
from pathlib import Path

from scripts.adapters.base import ImageEditRequest, ImageEditResult
from scripts.common import ensure_parent


class MockImageEditAdapter:
    adapter_name = "mock"

    def generate(self, request: ImageEditRequest) -> ImageEditResult:
        started = time.perf_counter()
        output_path = Path(str(request.config["output_path"]))
        raw_response_path = Path(str(request.config["raw_response_path"]))
        ensure_parent(output_path)
        ensure_parent(raw_response_path)

        if not output_path.exists():
            output_path.write_text(
                "\n".join(
                    [
                        "MOCK_IMAGE_EDIT_OUTPUT",
                        f"source_image={request.source_image}",
                        f"mask={request.mask}",
                        f"prompt={request.prompt}",
                        f"seed={request.seed}",
                        f"dry_run={request.config.get('dry_run', False)}",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
        if not raw_response_path.exists():
            raw_response_path.write_text(
                json.dumps(
                    {
                        "adapter": self.adapter_name,
                        "dry_run": bool(request.config.get("dry_run", False)),
                        "status": "success",
                        "note": "mock adapter; no real model call performed",
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
            adapter_kind="mock",
            provider_request_id="",
            version_risk="mock_adapter_no_model_capability_claim",
            cost_estimate_status="dry_run_or_mock",
        )
