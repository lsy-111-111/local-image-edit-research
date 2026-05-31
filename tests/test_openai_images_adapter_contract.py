from __future__ import annotations

import base64
import io
import json
import urllib.error
from pathlib import Path

from scripts.adapters.base import ImageEditRequest
from scripts.adapters.openai_images_adapter import OpenAIImagesAdapter, PNG_1X1


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
            "model_id": "gpt-image-1",
            "provider_model_ref": "gpt-image-1",
        },
    )


def test_openai_images_dry_run_writes_png(tmp_path: Path) -> None:
    result = OpenAIImagesAdapter().generate(request(tmp_path))

    assert result.status == "success"
    assert result.adapter_kind == "api"
    assert result.cost_estimate_status == "dry_run"
    assert (tmp_path / "out.png").exists()
    assert (tmp_path / "raw.json").exists()


def test_openai_images_missing_key_is_structured_failure(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = OpenAIImagesAdapter().generate(request(tmp_path, dry_run=False))

    assert result.status == "failed"
    assert "OPENAI_API_KEY" in result.error
    assert result.cost_estimate_status == "not_available"


def test_openai_images_mocked_success(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self) -> bytes:
            return json.dumps({"id": "req_1", "data": [{"b64_json": base64.b64encode(PNG_1X1).decode("ascii")}]}).encode()

    monkeypatch.setattr("scripts.adapters.openai_images_adapter.urllib.request.urlopen", lambda *args, **kwargs: Response())

    result = OpenAIImagesAdapter().generate(request(tmp_path, dry_run=False))

    assert result.status == "success"
    assert result.provider_request_id == "req_1"
    assert (tmp_path / "out.png").read_bytes() == PNG_1X1


def test_openai_images_rate_limit_maps_status(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test")

    def raise_rate_limit(*args, **kwargs):
        raise urllib.error.HTTPError("url", 429, "rate limited", {}, io.BytesIO(b"too many requests"))

    monkeypatch.setattr("scripts.adapters.openai_images_adapter.urllib.request.urlopen", raise_rate_limit)

    result = OpenAIImagesAdapter().generate(request(tmp_path, dry_run=False))

    assert result.status == "rate_limited"
