from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CASE_HEADER = (
    "case_id,image_path,image_sha256,mask_path,mask_sha256,task_id,image_type,target_size,mask_quality,language,"
    "difficulty,copyright_status,prompt_en,prompt_zh,expected_change,preserve_requirements,safety_notes\n"
)
CLAIM_HEADER = (
    "claim_id,claim_text,claim_type,strength,source_type,source_path,source_url,evidence_quote,evidence_level,"
    "run_metadata_ref,eval_metadata_ref,allowed_in_report,invalid_reason,reviewer,review_status\n"
)


def write_benchmark(path: Path, count: int = 80) -> None:
    rows = [
        f"c{index:03d},image.png,sha,,,T01,synthetic,512,none,en,easy,synthetic,prompt,提示,change,preserve,safe\n"
        for index in range(count)
    ]
    path.write_text(CASE_HEADER + "".join(rows), encoding="utf-8")


def run_truth(tmp_path: Path, manifest_text: str) -> str:
    metadata = tmp_path / "pilot.jsonl"
    gate = tmp_path / "pilot_gate.md"
    manifest = tmp_path / "claim_manifest.csv"
    benchmark = tmp_path / "benchmark.csv"
    output = tmp_path / "repo_truth_audit.md"
    metadata.write_text('{"run_id":"r","model_id":"m","case_id":"c","adapter":"mock"}\n', encoding="utf-8")
    gate.write_text("gate_decision: no_go\n", encoding="utf-8")
    manifest.write_text(CLAIM_HEADER + manifest_text, encoding="utf-8")
    write_benchmark(benchmark)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/audit_repo_truth.py",
            "--pilot-metadata",
            str(metadata),
            "--pilot-gate",
            str(gate),
            "--claim-manifest",
            str(manifest),
            "--benchmark",
            str(benchmark),
            "--output",
            str(output),
            "--root",
            str(tmp_path),
            "--allow-no-go",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    return output.read_text(encoding="utf-8")


def test_allowed_mock_ranking_claim_is_unresolved_conflict(tmp_path: Path) -> None:
    audit = run_truth(
        tmp_path,
        'c1,"The mock pilot leaderboard ranks models.",eval,strong,eval_metadata,,,,,pilot.jsonl,,yes,,Codex,review\n',
    )

    assert "claim_id: c1" in audit
    assert "mock-only metadata cannot support real/result/core/ranking claim" in audit


def test_blocked_mock_ranking_claim_is_not_unresolved_conflict(tmp_path: Path) -> None:
    audit = run_truth(
        tmp_path,
        'c1,"The mock pilot leaderboard ranks models.",eval,strong,eval_metadata,,,,,pilot.jsonl,,no,'
        '"mock metadata cannot support capability or ranking claims",Codex,blocked\n',
    )

    assert "claim_conflicts:\n- none" in audit

