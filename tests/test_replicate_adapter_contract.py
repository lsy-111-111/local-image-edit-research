from __future__ import annotations

import base64
import json
from pathlib import Path

from scripts.adapters.base import ImageEditRequest
from scripts.adapters.openai_images_adapter import PNG_1X1
from scripts.adapters.replicate_adapter import ReplicateAdapter


def request(tmp_path: Path, dry_run: bool = True) -> ImageEditRequest:
    source = tmp_path / "source.png"
    source.write_bytes(PNG_1X1)
    return ImageEditRequest(
        source_image=source.as_posix(),
        mask="",
        prompt="edit",
        seed=0,
        config={
            "output_path": (tmp_path / "out.png").as_posix(),
            "raw_response_path": (tmp_path / "raw.json").as_posix(),
            "dry_run": dry_run,
            "model_id": "m1",
            "provider_model_ref": "owner/model",
            "input_schema_ref": "replicate_image_prompt",
        },
    )


def test_replicate_dry_run_writes_png(tmp_path: Path) -> None:
    result = ReplicateAdapter().generate(request(tmp_path))

    assert result.status == "success"
    assert result.adapter_kind == "api"
    assert result.cost_estimate_status == "dry_run"
    assert (tmp_path / "out.png").exists()


def test_replicate_missing_token_is_structured_failure(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)

    result = ReplicateAdapter().generate(request(tmp_path, dry_run=False))

    assert result.status == "failed"
    assert "REPLICATE_API_TOKEN" in result.error


def test_replicate_mocked_success(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self) -> bytes:
            return json.dumps(
                {
                    "id": "pred_1",
                    "status": "succeeded",
                    "output": "data:image/png;base64," + base64.b64encode(PNG_1X1).decode("ascii"),
                    "metrics": {"predict_time": 1.0},
                }
            ).encode()

    monkeypatch.setattr("scripts.adapters.replicate_adapter.urllib.request.urlopen", lambda *args, **kwargs: Response())

    result = ReplicateAdapter().generate(request(tmp_path, dry_run=False))

    assert result.status == "success"
    assert result.provider_request_id == "pred_1"
    assert (tmp_path / "out.png").read_bytes() == PNG_1X1
