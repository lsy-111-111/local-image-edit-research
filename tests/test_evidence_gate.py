from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run_audit(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "scripts/audit_evidence.py", str(path)], capture_output=True, text=True)


def test_a_label_requires_complete_evidence(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text(json.dumps({"candidate_name": "example", "candidate_label": "A0"}) + "\n", encoding="utf-8")
    result = run_audit(path)
    assert result.returncode != 0
    assert "missing evidence" in result.stderr


def test_a_label_with_evidence_passes(tmp_path: Path) -> None:
    path = tmp_path / "good.jsonl"
    path.write_text(
        json.dumps(
            {
                "candidate_name": "example",
                "candidate_label": "A1",
                "source_url": "https://example.test",
                "evidence_quote": "official statement",
                "evidence_level": "E1",
                "last_verified_date": "2026-05-31",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_audit(path)
    assert result.returncode == 0, result.stderr
