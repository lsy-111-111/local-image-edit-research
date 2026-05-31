from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


def test_run_generation_uses_explicit_mock_adapter(tmp_path: Path) -> None:
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
        "m1,Mock,f1,mock,D_unversioned,,version_unlocked,,,E0,2026-05-31\n",
        encoding="utf-8",
    )
    metadata = tmp_path / "metadata.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_generation.py",
            "--phase",
            "pilot",
            "--adapter",
            "mock",
            "--cases",
            str(cases),
            "--models",
            str(models),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--metadata",
            str(metadata),
            "--dry-run",
            "--resume",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert '"adapter": "mock"' in metadata.read_text(encoding="utf-8")
    assert '"adapter_name": "mock"' in metadata.read_text(encoding="utf-8")


def test_run_generation_auto_routes_to_model_adapter(tmp_path: Path) -> None:
    from scripts.adapters.openai_images_adapter import PNG_1X1

    image = tmp_path / "image.png"
    image.write_bytes(PNG_1X1)
    digest = hashlib.sha256(PNG_1X1).hexdigest()
    cases = tmp_path / "cases.csv"
    cases.write_text(
        "case_id,image_path,image_sha256,mask_path,mask_sha256,task_id,image_type,target_size,mask_quality,language,difficulty,copyright_status,prompt_en,prompt_zh,expected_change,preserve_requirements,safety_notes\n"
        + f"c1,{image.as_posix()},{digest},,,T01,synthetic,512,none,en,easy,licensed,replace object,替换对象,replace,keep,safe\n",
        encoding="utf-8",
    )
    models = tmp_path / "models.csv"
    models.write_text(
        "model_id,model_name,family_id,adapter,version_lock,architecture_bucket,risk_flags,source_url,evidence_quote,evidence_level,last_verified_date,provider_model_ref,input_schema_ref\n"
        "m1,OpenAI,f1,openai_images,D_unversioned,,version_unlocked,,,E0,2026-05-31,gpt-image-1,openai_images_edit_json\n",
        encoding="utf-8",
    )
    metadata = tmp_path / "metadata.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_generation.py",
            "--phase",
            "pilot",
            "--adapter",
            "auto",
            "--cases",
            str(cases),
            "--models",
            str(models),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--metadata",
            str(metadata),
            "--dry-run",
            "--resume",
        ],
        capture_output=True,
        text=True,
    )

    text = metadata.read_text(encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert '"adapter": "openai_images"' in text
    assert '"output_path":' in text and ".png" in text
