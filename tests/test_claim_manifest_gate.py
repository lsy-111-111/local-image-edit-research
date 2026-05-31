from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HEADER = "claim_id,claim_text,claim_type,strength,source_type,source_path,source_url,evidence_quote,evidence_level,run_metadata_ref,eval_metadata_ref,allowed_in_report,reviewer,review_status\n"


def test_render_report_requires_claim_manifest(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "scripts/render_report.py", "--output", str(tmp_path / "report.md")],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "--claim-manifest" in result.stderr


def test_render_report_includes_only_allowed_claims(tmp_path: Path) -> None:
    manifest = tmp_path / "claim_manifest.csv"
    report = tmp_path / "report.md"
    manifest.write_text(
        HEADER
        + 'c1,"Allowed claim.",summary,moderate,run_metadata,,,,,data/runs/pilot_RUN_001.jsonl,,yes,Codex,approved\n'
        + 'c2,"Blocked claim.",summary,moderate,run_metadata,,,,,data/runs/pilot_RUN_001.jsonl,,no,Codex,needs_review\n',
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "scripts/render_report.py", "--claim-manifest", str(manifest), "--output", str(report)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    text = report.read_text(encoding="utf-8")
    assert "CLAIM: Allowed claim." in text
    assert "Blocked claim." not in text


def test_audit_blocks_weak_evidence_for_strong_manifest_claim(tmp_path: Path) -> None:
    claim = "This conclusion recommends a model."
    report = tmp_path / "report.md"
    manifest = tmp_path / "claim_manifest.csv"
    report.write_text(f"CLAIM: {claim}\n", encoding="utf-8")
    manifest.write_text(
        HEADER
        + f'c1,"{claim}",summary,strong,evidence,,https://example.test,weak quote,E4,,,yes,Codex,approved\n',
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/audit_report_claims.py",
            "--report",
            str(report),
            "--claim-manifest",
            str(manifest),
            "--output",
            str(tmp_path / "audit.csv"),
            "--missing",
            str(tmp_path / "missing.csv"),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "weak_evidence_cannot_support_strong_claim" in (tmp_path / "missing.csv").read_text(encoding="utf-8")
