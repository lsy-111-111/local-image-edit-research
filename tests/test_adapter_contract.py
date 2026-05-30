from __future__ import annotations

from pathlib import Path

from scripts.adapters.base import ImageEditRequest
from scripts.adapters.mock_adapter import MockImageEditAdapter


def test_mock_adapter_contract(tmp_path: Path) -> None:
    output = tmp_path / "out.txt"
    raw = tmp_path / "raw.json"
    adapter = MockImageEditAdapter()
    result = adapter.generate(
        ImageEditRequest(
            source_image="source.png",
            mask="mask.png",
            prompt="edit locally",
            seed=7,
            config={"output_path": output.as_posix(), "raw_response_path": raw.as_posix(), "dry_run": True},
        )
    )
    assert result.status == "success"
    assert result.cost_usd == 0.0
    assert output.exists()
    assert raw.exists()
