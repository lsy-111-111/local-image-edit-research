from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HEADER = (
    "provider,adapter_name,model_id,public_model_name,underlying_model,record_type,version_lock,version_risk,"
    "evidence_entry_id,human_review_status,adapter,provider_model_ref,input_schema_ref,source_url,evidence_quote,"
    "evidence_level,last_verified_date,review_status,notes\n"
)


def test_provider_model_map_requires_evidence_and_schema(tmp_path: Path) -> None:
    path = tmp_path / "provider_model_map.csv"
    path.write_text(
        HEADER
        + "replicate,replicate,m1,Model One,f1,model_version,D_unversioned,version_unlocked,e1,approved,replicate,owner/model,replicate_image_prompt,https://example.test,quote,E2,2026-05-31,approved,note\n",
        encoding="utf-8",
    )

    result = subprocess.run([sys.executable, "scripts/validate_provider_model_map.py", str(path)], capture_output=True, text=True)

    assert result.returncode == 0, result.stderr


def test_provider_model_map_rejects_unknown_adapter(tmp_path: Path) -> None:
    path = tmp_path / "provider_model_map.csv"
    path.write_text(
        HEADER
        + "unknown,unknown,m1,Model One,f1,model_version,D_unversioned,version_unlocked,e1,approved,unknown,owner/model,replicate_image_prompt,https://example.test,quote,E2,2026-05-31,approved,note\n",
        encoding="utf-8",
    )

    result = subprocess.run([sys.executable, "scripts/validate_provider_model_map.py", str(path)], capture_output=True, text=True)

    assert result.returncode != 0
    assert "invalid adapter" in result.stderr
