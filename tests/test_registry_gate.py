from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_wrapper_cannot_be_model_family(tmp_path: Path) -> None:
    family = tmp_path / "model_family.csv"
    family.write_text(
        "family_id,family_name,family_type,parent_family_id,source_url,evidence_quote,evidence_level,last_verified_date,review_status,notes\n"
        "f1,WrapperX,wrapper,,,,,,needs_review,\n",
        encoding="utf-8",
    )
    registry = tmp_path / "model_registry.jsonl"
    registry.write_text("", encoding="utf-8")
    architecture = tmp_path / "architecture.jsonl"
    architecture.write_text("", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "scripts/validate_registry_consistency.py",
            "--model-family",
            str(family),
            "--model-registry",
            str(registry),
            "--architecture",
            str(architecture),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "must not be registered" in result.stderr
