from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


HEADER = (
    "case_id,image_path,image_sha256,mask_path,mask_sha256,task_id,image_type,target_size,mask_quality,language,"
    "difficulty,copyright_status,prompt_en,prompt_zh,expected_change,preserve_requirements,safety_notes\n"
)


def write_cases(path: Path, image: Path, count: int) -> None:
    image.write_bytes(b"image")
    digest = hashlib.sha256(b"image").hexdigest()
    rows = [
        f"c{index},{image.as_posix()},{digest},,,T01,synthetic,512,none,en,easy,synthetic,prompt {index},提示 {index},change,preserve,safe\n"
        for index in range(count)
    ]
    path.write_text(HEADER + "".join(rows), encoding="utf-8")


def test_run_generation_case_limit_caps_metadata_records(tmp_path: Path) -> None:
    cases = tmp_path / "cases.csv"
    write_cases(cases, tmp_path / "image.png", 3)
    models = tmp_path / "models.csv"
    models.write_text(
        "model_id,model_name,family_id,adapter,version_lock,version_risk,source_url,evidence_quote,evidence_level,last_verified_date\n"
        "m1,Mock,f1,mock,D_versioned,,https://example.test,quote,E0,2026-05-31\n",
        encoding="utf-8",
    )
    metadata = tmp_path / "metadata.jsonl"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_generation.py",
            "--cases",
            str(cases),
            "--models",
            str(models),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--metadata",
            str(metadata),
            "--dry-run",
            "--case-limit",
            "2",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert len([line for line in metadata.read_text(encoding="utf-8").splitlines() if line.strip()]) == 2


def test_run_generation_case_sample_file_selects_cases(tmp_path: Path) -> None:
    cases = tmp_path / "cases.csv"
    write_cases(cases, tmp_path / "image.png", 3)
    sample = tmp_path / "sample.txt"
    sample.write_text("c1\n", encoding="utf-8")
    models = tmp_path / "models.csv"
    models.write_text(
        "model_id,model_name,family_id,adapter,version_lock,version_risk,source_url,evidence_quote,evidence_level,last_verified_date\n"
        "m1,Mock,f1,mock,D_versioned,,https://example.test,quote,E0,2026-05-31\n",
        encoding="utf-8",
    )
    metadata = tmp_path / "metadata.jsonl"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_generation.py",
            "--cases",
            str(cases),
            "--models",
            str(models),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--metadata",
            str(metadata),
            "--dry-run",
            "--case-sample-file",
            str(sample),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert '"case_id": "c1"' in metadata.read_text(encoding="utf-8")

