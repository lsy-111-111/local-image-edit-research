from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_record_count_claim_must_match_actual_metadata(tmp_path: Path) -> None:
    metadata = tmp_path / "pilot.jsonl"
    gate = tmp_path / "gate.md"
    manifest = tmp_path / "claim_manifest.csv"
    benchmark = tmp_path / "benchmark.csv"
    output = tmp_path / "repo_truth_audit.md"
    metadata.write_text(
        '{"run_id":"r","model_id":"m","case_id":"c1","adapter":"openai_images"}\n'
        '{"run_id":"r","model_id":"m","case_id":"c2","adapter":"openai_images"}\n',
        encoding="utf-8",
    )
    gate.write_text("gate_decision: go\n", encoding="utf-8")
    manifest.write_text(
        "claim_id,claim_text,claim_type,strength,source_type,source_path,source_url,evidence_quote,evidence_level,"
        "run_metadata_ref,eval_metadata_ref,allowed_in_report,invalid_reason,reviewer,review_status\n"
        'c1,"Pilot metadata includes 700 records.",metadata_summary,moderate,run_metadata,,,,,pilot.jsonl,,yes,,Codex,review\n',
        encoding="utf-8",
    )
    rows = [
        f"c{index},image.png,sha,,,T01,synthetic,512,none,en,easy,synthetic,prompt,提示,change,preserve,safe\n"
        for index in range(80)
    ]
    benchmark.write_text(
        "case_id,image_path,image_sha256,mask_path,mask_sha256,task_id,image_type,target_size,mask_quality,language,"
        "difficulty,copyright_status,prompt_en,prompt_zh,expected_change,preserve_requirements,safety_notes\n"
        + "".join(rows),
        encoding="utf-8",
    )

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
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "metadata count claim 700 != actual pilot records 2" in output.read_text(encoding="utf-8")
