from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


HEADER = (
    "case_id,image_path,image_sha256,mask_path,mask_sha256,task_id,image_type,target_size,mask_quality,language,"
    "difficulty,copyright_status,prompt_en,prompt_zh,expected_change,preserve_requirements,safety_notes\n"
)


def test_duplicate_row_content_is_rejected(tmp_path: Path) -> None:
    image = tmp_path / "image.png"
    image.write_bytes(b"image")
    digest = hashlib.sha256(b"image").hexdigest()
    row = f"{image.as_posix()},{digest},,,T01,synthetic,512,none,en,easy,synthetic,prompt,提示,change,preserve,safe\n"
    cases = tmp_path / "cases.csv"
    cases.write_text(HEADER + "c1," + row + "c2," + row, encoding="utf-8")

    result = subprocess.run([sys.executable, "scripts/validate_benchmark_cases.py", str(cases)], capture_output=True, text=True)

    assert result.returncode != 0
    assert "duplicate benchmark row content" in result.stderr
