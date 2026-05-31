from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_raw_pages_require_source_type_enum(tmp_path: Path) -> None:
    pages = tmp_path / "pages.jsonl"
    pages.write_text(
        json.dumps(
            {
                "page_id": "p1",
                "source_url": "https://example.test",
                "source_type": "blog",
                "retrieved_at": "2026-05-31",
                "title": "Example",
                "text": "body",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run([sys.executable, "scripts/validate_raw_pages.py", str(pages)], capture_output=True, text=True)

    assert result.returncode != 0
    assert "invalid source_type" in result.stderr


def test_evidence_readiness_allows_needs_review_report(tmp_path: Path) -> None:
    pages = tmp_path / "pages.jsonl"
    evidence = tmp_path / "evidence.jsonl"
    registry = tmp_path / "registry.jsonl"
    output = tmp_path / "readiness.md"
    base = {
        "source_type": "official_documentation",
        "source_url": "https://example.test",
        "evidence_quote": "official quote",
        "evidence_level": "E1",
        "last_verified_date": "2026-05-31",
        "review_status": "needs_review",
    }
    pages.write_text(
        json.dumps(
            {
                "page_id": "p1",
                "source_url": "https://example.test",
                "source_type": "official_documentation",
                "retrieved_at": "2026-05-31",
                "title": "Example",
                "text": "body",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    evidence.write_text(
        json.dumps({"candidate_name": "example", "candidate_label": "A1", "record_type": "model_version", **base}) + "\n",
        encoding="utf-8",
    )
    registry.write_text(json.dumps({"model_id": "m1", **base}) + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evidence_pilot_readiness.py",
            "--pages",
            str(pages),
            "--evidence",
            str(evidence),
            "--registry",
            str(registry),
            "--output",
            str(output),
            "--allow-needs-review",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "evidence_readiness_decision: needs_review" in output.read_text(encoding="utf-8")
