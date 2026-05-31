from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HEADER = (
    "case_id,image_path,image_sha256,mask_path,mask_sha256,task_id,image_type,target_size,mask_quality,language,"
    "difficulty,copyright_status,prompt_en,prompt_zh,expected_change,preserve_requirements,safety_notes\n"
)


def test_missing_image_asset_is_rejected(tmp_path: Path) -> None:
    cases = tmp_path / "cases.csv"
    missing = tmp_path / "missing.png"
    cases.write_text(
        HEADER
        + f"c1,{missing.as_posix()},sha,,,T01,synthetic,512,none,en,easy,synthetic,prompt,提示,change,preserve,safe\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "scripts/validate_benchmark_cases.py", str(cases)],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "image_path does not exist" in result.stderr

