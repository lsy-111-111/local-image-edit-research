from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


def test_canary_metadata_contract_requires_version_risk(tmp_path: Path) -> None:
    image = tmp_path / "image.png"
    image.write_bytes(b"image")
    image_digest = hashlib.sha256(b"image").hexdigest()
    output = tmp_path / "output.png"
    raw = tmp_path / "raw.json"
    output.write_bytes(b"output")
    raw.write_text("{}", encoding="utf-8")
    metadata = tmp_path / "metadata.jsonl"
    metadata.write_text(
        json.dumps(
            {
                "run_id": "canary_REAL_001",
                "phase": "pilot",
                "model_id": "m1",
                "case_id": "c1",
                "source_image": image.as_posix(),
                "source_image_sha256": image_digest,
                "mask": "",
                "mask_sha256": "",
                "prompt": "edit",
                "seed_requested": 0,
                "seed_effective": 0,
                "output_path": output.as_posix(),
                "runtime_seconds": 1.0,
                "cost_usd": 0.01,
                "raw_response_path": raw.as_posix(),
                "status": "success",
                "version_lock": "D_unversioned",
                "version_risk": "version_unlocked",
                "adapter": "openai_images",
                "adapter_name": "openai_images",
                "adapter_kind": "api",
                "provider_request_id": "req_1",
                "cost_estimate_status": "pricing_applied",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run([sys.executable, "scripts/audit_run_metadata.py", str(metadata)], capture_output=True, text=True)

    assert result.returncode == 0, result.stderr


def test_canary_selection_blocks_without_human_approved_provider(tmp_path: Path) -> None:
    provider_map = tmp_path / "provider_model_map.csv"
    canary_model = tmp_path / "canary_model.csv"
    summary = tmp_path / "summary.md"
    provider_map.write_text(
        "provider,adapter_name,model_id,public_model_name,underlying_model,record_type,version_lock,version_risk,evidence_entry_id,human_review_status,adapter,provider_model_ref,input_schema_ref,source_url,evidence_quote,evidence_level,last_verified_date,review_status,notes\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/select_canary_model.py",
            "--provider-model-map",
            str(provider_map),
            "--output",
            str(canary_model),
            "--summary",
            str(summary),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "adapter_canary_gate: blocked" in summary.read_text(encoding="utf-8")
    assert canary_model.read_text(encoding="utf-8").startswith("model_id,model_name,adapter")

