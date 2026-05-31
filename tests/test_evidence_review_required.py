from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_a_label_evidence_defaults_to_needs_review(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence.jsonl"
    evidence.write_text(
        json.dumps(
            {
                "candidate_name": "example",
                "candidate_label": "A1",
                "record_type": "model_version",
                "source_type": "official_docs",
                "source_url": "https://example.test",
                "evidence_quote": "official quote",
                "evidence_quote_context": "official quote with surrounding context",
                "evidence_level": "E1",
                "last_verified_date": "2026-05-31",
                "review_status": "approved",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run([sys.executable, "scripts/audit_evidence.py", str(evidence)], capture_output=True, text=True)

    assert result.returncode != 0
    assert "must default to review_status=needs_review" in result.stderr


def test_export_human_review_template_blocks_registry_by_default(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence.jsonl"
    needs_review = tmp_path / "needs_review.csv"
    human_review = tmp_path / "human_review.csv"
    evidence.write_text(
        json.dumps(
            {
                "candidate_id": "example",
                "candidate_name": "example",
                "candidate_label": "A1",
                "record_type": "model_version",
                "source_type": "official_docs",
                "source_url": "https://example.test",
                "evidence_quote": "official quote",
                "evidence_quote_context": "official quote with surrounding context",
                "evidence_level": "E1",
                "last_verified_date": "2026-05-31",
                "review_status": "needs_review",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/export_needs_review.py",
            "--input",
            str(evidence),
            "--output",
            str(needs_review),
            "--human-review",
            str(human_review),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "allowed_for_registry" in human_review.read_text(encoding="utf-8")
    assert ",no" in human_review.read_text(encoding="utf-8")

