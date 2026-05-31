from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HEADER = (
    "model_id,adapter,provider_model_ref,input_schema_ref,version_lock,source_url,evidence_quote,"
    "evidence_level,last_verified_date,review_status,notes\n"
)


def test_provider_model_map_requires_evidence_and_schema(tmp_path: Path) -> None:
    path = tmp_path / "provider_model_map.csv"
    path.write_text(
        HEADER
        + "m1,replicate,owner/model,replicate_image_prompt,D_unversioned,https://example.test,quote,E2,2026-05-31,needs_review,note\n",
        encoding="utf-8",
    )

    result = subprocess.run([sys.executable, "scripts/validate_provider_model_map.py", str(path)], capture_output=True, text=True)

    assert result.returncode == 0, result.stderr


def test_provider_model_map_rejects_unknown_adapter(tmp_path: Path) -> None:
    path = tmp_path / "provider_model_map.csv"
    path.write_text(
        HEADER
        + "m1,unknown,owner/model,replicate_image_prompt,D_unversioned,https://example.test,quote,E2,2026-05-31,needs_review,note\n",
        encoding="utf-8",
    )

    result = subprocess.run([sys.executable, "scripts/validate_provider_model_map.py", str(path)], capture_output=True, text=True)

    assert result.returncode != 0
    assert "invalid adapter" in result.stderr
