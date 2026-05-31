from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_empty_pilot_metadata_generates_no_go(tmp_path: Path) -> None:
    metadata = tmp_path / "empty.jsonl"
    output = tmp_path / "gate.md"
    metadata.write_text("", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/pilot_gate_decision.py", "--metadata", str(metadata), "--output", str(output)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    gate = output.read_text(encoding="utf-8")
    assert "gate_decision: no_go" in gate
    assert "no pilot metadata records" in gate


def test_mock_only_pilot_metadata_generates_no_go(tmp_path: Path) -> None:
    metadata = tmp_path / "mock.jsonl"
    output = tmp_path / "gate.md"
    rows = []
    for model in range(5):
        for case in range(100):
            rows.append(
                '{"run_id":"r","model_id":"m%s","case_id":"c%s","source_image":"i.png",'
                '"prompt":"p","output_path":"o.png","raw_response_path":"r.json","status":"success",'
                '"adapter":"mock","version_lock":"D_unversioned"}\n' % (model, case)
            )
    metadata.write_text("".join(rows), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/pilot_gate_decision.py", "--metadata", str(metadata), "--output", str(output)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    gate = output.read_text(encoding="utf-8")
    assert "gate_decision: no_go" in gate
    assert "mock adapter records cannot unlock real pilot/core" in gate
