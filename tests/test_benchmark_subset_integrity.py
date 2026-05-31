from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


HEADER = (
    "case_id,image_path,image_sha256,mask_path,mask_sha256,task_id,image_type,target_size,mask_quality,language,"
    "difficulty,copyright_status,prompt_en,prompt_zh,expected_change,preserve_requirements,safety_notes\n"
)


def write_cases(path: Path, image: Path, count: int, prefix: str = "c") -> None:
    image.write_bytes(b"image")
    digest = hashlib.sha256(b"image").hexdigest()
    rows = [
        f"{prefix}{index:03d},{image.as_posix()},{digest},,,T01,synthetic,512,none,en,easy,synthetic,prompt {index},提示 {index},change {index},preserve,safe\n"
        for index in range(count)
    ]
    path.write_text(HEADER + "".join(rows), encoding="utf-8")


def test_subset_case_ids_must_come_from_main_benchmark(tmp_path: Path) -> None:
    image = tmp_path / "image.png"
    main_cases = tmp_path / "benchmark.csv"
    pilot_cases = tmp_path / "pilot.csv"
    output = tmp_path / "gate.md"
    write_cases(main_cases, image, 100, "main")
    write_cases(pilot_cases, image, 100, "pilot")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/benchmark_gate_decision.py",
            "--cases",
            str(main_cases),
            "--pilot-cases",
            str(pilot_cases),
            "--output",
            str(output),
            "--allow-no-go",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    text = output.read_text(encoding="utf-8")
    assert "benchmark_gate_decision: no_go" in text
    assert "is not present" in text

