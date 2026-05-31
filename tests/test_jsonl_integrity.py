from __future__ import annotations

import pytest
from pathlib import Path

from scripts.common import read_jsonl


def test_jsonl_line_must_be_object(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text('["not", "an", "object"]\n', encoding="utf-8")

    with pytest.raises(ValueError, match="JSONL record must be an object"):
        read_jsonl(path)


def test_jsonl_parse_error_fails(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text('{"ok": true}\n{"broken": \n', encoding="utf-8")

    with pytest.raises(ValueError, match="invalid JSON"):
        read_jsonl(path)
