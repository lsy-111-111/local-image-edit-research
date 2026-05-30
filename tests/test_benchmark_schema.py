from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


HEADER = (
    "case_id,image_path,image_sha256,mask_path,mask_sha256,task_id,image_type,target_size,mask_quality,language,"
    "difficulty,copyright_status,prompt_en,prompt_zh,expected_change,preserve_requirements,safety_notes\n"
)


def test_valid_benchmark_case_passes(tmp_path: Path) -> None:
    image = tmp_path / "image.bin"
    image.write_bytes(b"image")
    digest = hashlib.sha256(b"image").hexdigest()
    cases = tmp_path / "cases.csv"
    cases.write_text(
        HEADER
        + f"c1,{image.as_posix()},{digest},,,T01,synthetic,512,none,en,easy,licensed,replace object,替换对象,replace the object,keep background,safe\n",
        encoding="utf-8",
    )
    result = subprocess.run([sys.executable, "scripts/validate_benchmark_cases.py", str(cases)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_missing_preserve_requirements_fails(tmp_path: Path) -> None:
    image = tmp_path / "image.bin"
    image.write_bytes(b"image")
    digest = hashlib.sha256(b"image").hexdigest()
    cases = tmp_path / "cases.csv"
    cases.write_text(
        HEADER
        + f"c1,{image.as_posix()},{digest},,,T01,synthetic,512,none,en,easy,licensed,replace object,替换对象,replace the object,,safe\n",
        encoding="utf-8",
    )
    result = subprocess.run([sys.executable, "scripts/validate_benchmark_cases.py", str(cases)], capture_output=True, text=True)
    assert result.returncode != 0
    assert "missing preserve_requirements" in result.stderr
