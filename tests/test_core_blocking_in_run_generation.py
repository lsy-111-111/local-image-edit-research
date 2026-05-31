from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_generation(tmp_path: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "scripts/run_generation.py",
            "--cases",
            str(tmp_path / "missing_cases.csv"),
            "--models",
            str(tmp_path / "missing_models.csv"),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--metadata",
            str(tmp_path / "metadata.jsonl"),
            *extra,
        ],
        capture_output=True,
        text=True,
    )


def test_core_smoke_requires_go_pilot_gate(tmp_path: Path) -> None:
    result = run_generation(tmp_path, "--phase", "core_smoke")

    assert result.returncode != 0
    assert "--pilot-gate is required" in result.stderr


def test_core_smoke_rejects_no_go_pilot_gate(tmp_path: Path) -> None:
    pilot_gate = tmp_path / "pilot_gate.md"
    pilot_gate.write_text("gate_decision: no_go\n", encoding="utf-8")

    result = run_generation(tmp_path, "--phase", "core_smoke", "--pilot-gate", str(pilot_gate))

    assert result.returncode != 0
    assert "requires pilot-gate with gate_decision: go" in result.stderr


def test_core_full_requires_go_core_smoke_gate(tmp_path: Path) -> None:
    pilot_gate = tmp_path / "pilot_gate.md"
    core_gate = tmp_path / "core_gate.md"
    pilot_gate.write_text("gate_decision: go\n", encoding="utf-8")
    core_gate.write_text("gate_decision: no_go\n", encoding="utf-8")

    result = run_generation(
        tmp_path,
        "--phase",
        "core_full",
        "--pilot-gate",
        str(pilot_gate),
        "--core-smoke-gate",
        str(core_gate),
    )

    assert result.returncode != 0
    assert "requires core-smoke-gate with gate_decision: go" in result.stderr
