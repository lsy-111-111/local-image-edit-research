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


def run_truth(tmp_path: Path, metadata: Path, gate: Path, manifest: Path, benchmark: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
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
            str(tmp_path / "repo_truth_audit.md"),
            "--root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )


def write_benchmark(path: Path, count: int) -> None:
    rows = []
    for index in range(count):
        rows.append(
            f"c{index:03d},image.png,sha,,,T01,synthetic,512,none,en,easy,synthetic,prompt,提示,change,preserve,safe\n"
        )
    path.write_text(CASE_HEADER + "".join(rows), encoding="utf-8")


def test_mock_only_pilot_is_repo_truth_no_go(tmp_path: Path) -> None:
    metadata = tmp_path / "pilot.jsonl"
    gate = tmp_path / "gate.md"
    manifest = tmp_path / "claim_manifest.csv"
    benchmark = tmp_path / "benchmark.csv"
    metadata.write_text('{"run_id":"r","model_id":"m","case_id":"c","adapter":"mock"}\n', encoding="utf-8")
    gate.write_text("gate_decision: go\n", encoding="utf-8")
    manifest.write_text(CLAIM_HEADER, encoding="utf-8")
    write_benchmark(benchmark, 80)

    result = run_truth(tmp_path, metadata, gate, manifest, benchmark)

    assert result.returncode != 0
    audit = (tmp_path / "repo_truth_audit.md").read_text(encoding="utf-8")
    assert "mock adapter records cannot unlock real pilot/core" in audit


def test_benchmark_under_80_is_repo_truth_no_go(tmp_path: Path) -> None:
    metadata = tmp_path / "pilot.jsonl"
    gate = tmp_path / "gate.md"
    manifest = tmp_path / "claim_manifest.csv"
    benchmark = tmp_path / "benchmark.csv"
    metadata.write_text('{"run_id":"r","model_id":"m","case_id":"c","adapter":"openai_images"}\n', encoding="utf-8")
    gate.write_text("gate_decision: go\n", encoding="utf-8")
    manifest.write_text(CLAIM_HEADER, encoding="utf-8")
    write_benchmark(benchmark, 79)

    result = run_truth(tmp_path, metadata, gate, manifest, benchmark)

    assert result.returncode != 0
    assert "fewer than 80" in (tmp_path / "repo_truth_audit.md").read_text(encoding="utf-8")
