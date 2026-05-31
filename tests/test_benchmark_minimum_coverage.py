from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HEADER = (
    "case_id,image_path,image_sha256,mask_path,mask_sha256,task_id,image_type,target_size,mask_quality,language,"
    "difficulty,copyright_status,prompt_en,prompt_zh,expected_change,preserve_requirements,safety_notes\n"
)


def test_minimum_case_count_is_enforced(tmp_path: Path) -> None:
    cases = tmp_path / "cases.csv"
    cases.write_text(HEADER, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/validate_benchmark_cases.py", str(cases), "--min-cases", "80"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "expected at least 80 cases" in result.stderr


def test_api_assets_must_be_png_jpeg_or_webp(tmp_path: Path) -> None:
    image = tmp_path / "image.svg"
    image.write_text("<svg />", encoding="utf-8")
    import hashlib

    digest = hashlib.sha256(image.read_bytes()).hexdigest()
    cases = tmp_path / "cases.csv"
    cases.write_text(
        HEADER
        + f"c1,{image.as_posix()},{digest},,,T01,synthetic,512,none,en,easy,synthetic,prompt,提示,change,preserve,safe\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "scripts/validate_benchmark_cases.py", str(cases), "--require-api-assets"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "image_path must be PNG/JPEG/WebP" in result.stderr
