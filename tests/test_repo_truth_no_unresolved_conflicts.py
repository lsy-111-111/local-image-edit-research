from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_repo_truth_audit_has_no_unresolved_claim_conflicts(tmp_path: Path) -> None:
    output = tmp_path / "repo_truth_audit.md"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/audit_repo_truth.py",
            "--pilot-metadata",
            "data/runs/pilot_RUN_001.jsonl",
            "--pilot-gate",
            "reports/pilot_RUN_001_gate.md",
            "--claim-manifest",
            "reports/claim_manifest.csv",
            "--benchmark",
            "data/benchmark/benchmark_cases.csv",
            "--final-report",
            "reports/final_report_draft.md",
            "--output",
            str(output),
            "--allow-no-go",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    text = output.read_text(encoding="utf-8")
    assert "repo_truth_decision: no_go" in text
    assert "claim_conflicts:\n- none" in text

