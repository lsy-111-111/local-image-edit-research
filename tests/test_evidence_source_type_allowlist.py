from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


def test_old_source_type_is_rejected_for_raw_pages(tmp_path: Path) -> None:
    pages = tmp_path / "pages.jsonl"
    text = "body"
    pages.write_text(
        json.dumps(
            {
                "page_id": "p1",
                "source_url": "https://example.test",
                "source_type": "official_documentation",
                "retrieved_at": "2026-05-31",
                "title": "Example",
                "text": text,
                "content_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run([sys.executable, "scripts/validate_raw_pages.py", str(pages)], capture_output=True, text=True)

    assert result.returncode != 0
    assert "invalid source_type official_documentation" in result.stderr


def test_allowed_source_type_passes_for_evidence(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence.jsonl"
    evidence.write_text(
        json.dumps(
            {
                "candidate_name": "example",
                "candidate_label": "A1",
                "record_type": "model_version",
                "source_type": "official_model_card",
                "source_url": "https://example.test",
                "evidence_quote": "official quote",
                "evidence_quote_context": "official quote with surrounding context",
                "evidence_level": "E0",
                "last_verified_date": "2026-05-31",
                "review_status": "needs_review",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run([sys.executable, "scripts/audit_evidence.py", str(evidence)], capture_output=True, text=True)

    assert result.returncode == 0, result.stderr

