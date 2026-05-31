from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_invalid_candidate_label_fails(tmp_path: Path) -> None:
    path = tmp_path / "bad_label.jsonl"
    path.write_text(json.dumps({"candidate_name": "example", "candidate_label": "Z"}) + "\n", encoding="utf-8")
    result = subprocess.run([sys.executable, "scripts/audit_evidence.py", str(path)], capture_output=True, text=True)
    assert result.returncode != 0
    assert "invalid candidate_label" in result.stderr


def test_bad_date_format_fails_for_a_label(tmp_path: Path) -> None:
    path = tmp_path / "bad_date.jsonl"
    path.write_text(
        json.dumps(
            {
                "candidate_name": "example",
                "candidate_label": "A2",
                "source_type": "official_documentation",
                "source_url": "https://example.test",
                "evidence_quote": "quote",
                "evidence_level": "E2",
                "last_verified_date": "31-05-2026",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    result = subprocess.run([sys.executable, "scripts/audit_evidence.py", str(path)], capture_output=True, text=True)
    assert result.returncode != 0
    assert "last_verified_date_format" in result.stderr


def test_gpt_batch_dry_run_writes_no_records(tmp_path: Path) -> None:
    pages = tmp_path / "pages.jsonl"
    pages.write_text(json.dumps({"page_id": "p1", "source_url": "https://example.test", "retrieved_at": "2026-05-31", "text": "hello"}) + "\n", encoding="utf-8")
    prompt = tmp_path / "prompt.md"
    prompt.write_text("extract", encoding="utf-8")
    output = tmp_path / "out.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/gpt_batch.py",
            "--input",
            str(pages),
            "--prompt",
            str(prompt),
            "--output",
            str(output),
            "--dry-run",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert output.read_text(encoding="utf-8") == ""
