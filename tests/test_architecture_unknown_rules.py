from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_non_unknown_architecture_requires_evidence_quote(tmp_path: Path) -> None:
    path = tmp_path / "architecture.jsonl"
    path.write_text(
        json.dumps(
            {
                "model_id": "m1",
                "base_architecture": "G1",
                "control_mechanism": "unknown",
                "training_or_inference": "unknown",
                "deployment": "unknown",
                "architecture_public": "partial",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    result = subprocess.run([sys.executable, "scripts/validate_architecture_labels.py", str(path)], capture_output=True, text=True)
    assert result.returncode != 0
    assert "requires evidence_quote" in result.stderr


def test_unknown_architecture_passes_without_evidence(tmp_path: Path) -> None:
    path = tmp_path / "architecture.jsonl"
    path.write_text(
        json.dumps(
            {
                "model_id": "m1",
                "base_architecture": "unknown",
                "control_mechanism": "unknown",
                "training_or_inference": "unknown",
                "deployment": "unknown",
                "architecture_public": "unknown",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    result = subprocess.run([sys.executable, "scripts/validate_architecture_labels.py", str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
