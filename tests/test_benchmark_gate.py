from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CASE_HEADER = (
    "case_id,image_path,image_sha256,mask_path,mask_sha256,task_id,image_type,target_size,mask_quality,language,"
    "difficulty,copyright_status,prompt_en,prompt_zh,expected_change,preserve_requirements,safety_notes\n"
)


def write_cases(path: Path, count: int) -> None:
    rows = [
        f"c{index:03d},image.png,sha,,,T01,synthetic,512,none,en,easy,synthetic,prompt {index},prompt zh {index},change {index},preserve,safe\n"
        for index in range(count)
    ]
    path.write_text(CASE_HEADER + "".join(rows), encoding="utf-8")


def test_benchmark_gate_marks_valid_data_ready(tmp_path: Path) -> None:
    cases = tmp_path / "cases.csv"
    output = tmp_path / "benchmark_gate.md"
    write_cases(cases, 100)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/benchmark_gate_decision.py",
            "--cases",
            str(cases),
            "--output",
            str(output),
            "--min-cases",
            "100",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    text = output.read_text(encoding="utf-8")
    assert "benchmark_gate_decision: go" in text
    assert "does not support model ranking or capability claims" in text
