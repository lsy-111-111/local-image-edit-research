from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


def test_run_generation_resume_does_not_duplicate_metadata(tmp_path: Path) -> None:
    image = tmp_path / "image.bin"
    image.write_bytes(b"image")
    digest = hashlib.sha256(b"image").hexdigest()
    cases = tmp_path / "cases.csv"
    cases.write_text(
        "case_id,image_path,image_sha256,mask_path,mask_sha256,task_id,image_type,target_size,mask_quality,language,difficulty,copyright_status,prompt_en,prompt_zh,expected_change,preserve_requirements,safety_notes\n"
        + f"c1,{image.as_posix()},{digest},,,T01,synthetic,512,none,en,easy,licensed,replace object,替换对象,replace,keep,safe\n",
        encoding="utf-8",
    )
    models = tmp_path / "models.csv"
    models.write_text(
        "model_id,model_name,family_id,adapter,version_lock,architecture_bucket,risk_flags,source_url,evidence_quote,evidence_level,last_verified_date\n"
        "m1,Mock,f1,mock,D_versioned,,,,,,\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "outputs"
    metadata = tmp_path / "metadata.jsonl"
    cmd = [
        sys.executable,
        "scripts/run_generation.py",
        "--cases",
        str(cases),
        "--models",
        str(models),
        "--output-dir",
        str(output_dir),
        "--metadata",
        str(metadata),
        "--dry-run",
        "--resume",
    ]
    first = subprocess.run(cmd, capture_output=True, text=True)
    second = subprocess.run(cmd, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    lines = [line for line in metadata.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1
