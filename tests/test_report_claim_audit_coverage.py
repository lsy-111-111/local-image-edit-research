from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def audit_claims(tmp_path: Path, report: Path, manifest: Path | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [
        sys.executable,
        "scripts/audit_report_claims.py",
        "--report",
        str(report),
        "--output",
        str(tmp_path / "audit.csv"),
        "--missing",
        str(tmp_path / "missing.csv"),
    ]
    if manifest is not None:
        cmd.extend(["--claim-manifest", str(manifest)])
    return subprocess.run(cmd, capture_output=True, text=True)


def test_strong_claim_without_manifest_is_blocked(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text("This report recommends Model A as the best option.\n", encoding="utf-8")

    result = audit_claims(tmp_path, report)

    assert result.returncode != 0
    missing = (tmp_path / "missing.csv").read_text(encoding="utf-8")
    assert "claim_manifest_required" in missing


def test_manifest_allowed_claim_passes(tmp_path: Path) -> None:
    claim = "This report recommends Model A as the best option."
    report = tmp_path / "report.md"
    manifest = tmp_path / "claim_manifest.csv"
    report.write_text(claim + "\n", encoding="utf-8")
    manifest.write_text(
        "claim_id,claim_text,claim_type,strength,source_type,source_path,source_url,evidence_quote,evidence_level,run_metadata_ref,eval_metadata_ref,allowed_in_report,reviewer,review_status\n"
        f"c1,{claim},summary,strong,evidence,,https://example.test/source,official quote,E0,,,yes,human,approved\n",
        encoding="utf-8",
    )

    result = audit_claims(tmp_path, report, manifest)

    assert result.returncode == 0, result.stderr


def test_manifest_disallowed_claim_is_blocked(tmp_path: Path) -> None:
    claim = "This report recommends Model A as the best option."
    report = tmp_path / "report.md"
    manifest = tmp_path / "claim_manifest.csv"
    report.write_text(claim + "\n", encoding="utf-8")
    manifest.write_text(
        "claim_id,claim_text,claim_type,strength,source_type,source_path,source_url,evidence_quote,evidence_level,run_metadata_ref,eval_metadata_ref,allowed_in_report,reviewer,review_status\n"
        f"c1,{claim},summary,strong,evidence,,https://example.test/source,official quote,E0,,,no,human,needs_review\n",
        encoding="utf-8",
    )

    result = audit_claims(tmp_path, report, manifest)

    assert result.returncode != 0
    missing = (tmp_path / "missing.csv").read_text(encoding="utf-8")
    assert "allowed_in_report_not_yes" in missing
