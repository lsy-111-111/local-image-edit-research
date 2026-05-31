from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_a_label_requires_evidence_quote_context(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence.jsonl"
    evidence.write_text(
        json.dumps(
            {
                "candidate_name": "example",
                "candidate_label": "A2",
                "record_type": "model_version",
                "source_type": "official_docs",
                "source_url": "https://example.test",
                "evidence_quote": "official quote",
                "evidence_level": "E0",
                "last_verified_date": "2026-05-31",
                "review_status": "needs_review",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run([sys.executable, "scripts/audit_evidence.py", str(evidence)], capture_output=True, text=True)

    assert result.returncode != 0
    assert "evidence_quote_context" in result.stderr

