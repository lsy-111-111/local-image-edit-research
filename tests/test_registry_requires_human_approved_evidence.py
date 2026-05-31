from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


EVIDENCE = {
    "entry_id": "e1",
    "candidate_id": "m1",
    "candidate_name": "Model One",
    "candidate_label": "A1",
    "record_type": "model_version",
    "model_family": "Family One",
    "source_type": "official_docs",
    "source_url": "https://example.test",
    "evidence_quote": "official quote",
    "evidence_quote_context": "official quote with context",
    "evidence_level": "E1",
    "last_verified_date": "2026-05-31",
    "review_status": "needs_review",
}


def run_builder(tmp_path: Path, review_row: str) -> tuple[Path, Path]:
    evidence = tmp_path / "evidence.jsonl"
    human_review = tmp_path / "human_review.csv"
    provider_map = tmp_path / "provider_map.csv"
    registry = tmp_path / "registry.jsonl"
    uncertain = tmp_path / "uncertain.csv"
    evidence.write_text(json.dumps(EVIDENCE) + "\n", encoding="utf-8")
    human_review.write_text(
        "entry_id,reviewer,review_status,decision,decision_reason,reviewed_at,allowed_for_registry\n" + review_row,
        encoding="utf-8",
    )
    provider_map.write_text(
        "model_id,adapter,provider_model_ref,input_schema_ref,version_lock,source_url,evidence_quote,evidence_level,last_verified_date,review_status,notes\n"
        "m1,replicate,owner/model,replicate_image_prompt,D_unversioned,https://example.test,quote,E2,2026-05-31,approved,note\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_registry_from_evidence.py",
            "--evidence",
            str(evidence),
            "--human-review",
            str(human_review),
            "--existing-provider-map",
            str(provider_map),
            "--output",
            str(registry),
            "--families",
            str(tmp_path / "families.csv"),
            "--versions",
            str(tmp_path / "versions.csv"),
            "--implementations",
            str(tmp_path / "implementations.csv"),
            "--provider-model-map",
            str(tmp_path / "generated_provider_map.csv"),
            "--pilot-candidates",
            str(tmp_path / "pilot_candidates.csv"),
            "--uncertain",
            str(uncertain),
            "--family-tree",
            str(tmp_path / "family_tree.md"),
            "--decision-log",
            str(tmp_path / "decision_log.md"),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    return registry, uncertain


def test_registry_rows_require_human_approved_evidence(tmp_path: Path) -> None:
    registry, uncertain = run_builder(tmp_path, "e1,,needs_review,pending,,,no\n")

    assert registry.read_text(encoding="utf-8") == ""
    assert "human_review_not_approved" in uncertain.read_text(encoding="utf-8")


def test_human_approved_evidence_can_enter_registry(tmp_path: Path) -> None:
    registry, uncertain = run_builder(tmp_path, "e1,human,approved,approved,checked,2026-05-31,yes\n")

    assert '"model_id": "m1"' in registry.read_text(encoding="utf-8")
    assert "human_review_not_approved" not in uncertain.read_text(encoding="utf-8")

