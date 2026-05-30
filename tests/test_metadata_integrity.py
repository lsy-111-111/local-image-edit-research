from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_metadata_missing_required_field_fails(tmp_path: Path) -> None:
    metadata = tmp_path / "metadata.jsonl"
    metadata.write_text(json.dumps({"run_id": "r1"}) + "\n", encoding="utf-8")
    result = subprocess.run([sys.executable, "scripts/audit_run_metadata.py", str(metadata)], capture_output=True, text=True)
    assert result.returncode != 0
    assert "missing model_id" in result.stderr
