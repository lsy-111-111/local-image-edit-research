from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from scripts.common import ensure_parent, is_missing, read_csv_rows


AUDIT_FIELDS = ["line_no", "claim", "status", "evidence_ref", "notes"]
STRONG_CLAIM_RE = re.compile(r"\b(best|better|supports|outperforms|recommend|conclusion)\b", re.IGNORECASE)
WEAK_EVIDENCE_LEVELS = {"E4", "E5"}


def normalize_claim(value: str) -> str:
    return " ".join(value.strip().lower().split())


def has_inline_evidence(text: str) -> bool:
    return ("source_url=" in text and "evidence_quote=" in text) or "run_metadata=" in text or "eval_metadata=" in text


def manifest_trace(row: dict[str, str]) -> str:
    if not is_missing(row.get("run_metadata_ref")):
        return "run_metadata_ref"
    if not is_missing(row.get("eval_metadata_ref")):
        return "eval_metadata_ref"
    if not is_missing(row.get("source_path")):
        return "source_path"
    if not is_missing(row.get("source_url")) and not is_missing(row.get("evidence_quote")):
        return "source_url+evidence_quote"
    return ""


def load_manifest(path: Path) -> dict[str, dict[str, str]]:
    rows = read_csv_rows(path)
    manifest: dict[str, dict[str, str]] = {}
    for index, row in enumerate(rows, start=2):
        claim_text = row.get("claim_text", "")
        if is_missing(claim_text):
            raise ValueError(f"{path}:{index}: missing claim_text")
        manifest[normalize_claim(claim_text)] = row
    return manifest


def report_claims(report_path: Path) -> list[dict[str, str]]:
    claims: list[dict[str, str]] = []
    in_code_block = False
    for line_no, line in enumerate(report_path.read_text(encoding="utf-8").splitlines(), start=1):
        text = line.strip()
        if text.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not text:
            continue
        if text.startswith("CLAIM:"):
            claims.append(
                {
                    "line_no": str(line_no),
                    "claim": text.removeprefix("CLAIM:").strip(),
                    "raw_text": text,
                    "source": "explicit_claim",
                }
            )
            continue
        match = STRONG_CLAIM_RE.search(text)
        if match:
            claims.append(
                {
                    "line_no": str(line_no),
                    "claim": text,
                    "raw_text": text,
                    "source": f"strong_term:{match.group(1).lower()}",
                }
            )
    return claims


def audit(report_path: Path, claim_manifest: Path | None = None) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    audit_rows: list[dict[str, str]] = []
    missing_rows: list[dict[str, str]] = []
    if not report_path.exists():
        missing_rows.append({"line_no": "0", "claim": "report_missing", "status": "missing", "evidence_ref": "", "notes": str(report_path)})
        return audit_rows, missing_rows

    manifest: dict[str, dict[str, str]] | None = None
    if claim_manifest is not None:
        if not claim_manifest.exists():
            missing_rows.append(
                {
                    "line_no": "0",
                    "claim": "claim_manifest_missing",
                    "status": "missing",
                    "evidence_ref": "",
                    "notes": str(claim_manifest),
                }
            )
            return audit_rows, missing_rows
        manifest = load_manifest(claim_manifest)

    for claim in report_claims(report_path):
        text = claim["raw_text"]
        claim_text = claim["claim"]
        status = "pass"
        evidence_ref = ""
        notes = claim["source"]

        if manifest is None:
            if claim["source"] == "explicit_claim" and has_inline_evidence(text):
                evidence_ref = "inline"
            else:
                status = "missing"
                notes = f"{notes}; claim_manifest_required"
        else:
            manifest_row = manifest.get(normalize_claim(claim_text))
            if manifest_row is None:
                status = "missing"
                notes = f"{notes}; claim_not_in_manifest"
            elif manifest_row.get("allowed_in_report", "").strip().lower() != "yes":
                status = "missing"
                notes = f"{notes}; allowed_in_report_not_yes"
            else:
                evidence_ref = manifest_trace(manifest_row)
                if not evidence_ref:
                    status = "missing"
                    notes = f"{notes}; missing_manifest_evidence_ref"
                evidence_level = manifest_row.get("evidence_level", "").strip()
                strength = manifest_row.get("strength", "").strip().lower()
                is_strong = claim["source"].startswith("strong_term:") or strength == "strong"
                if is_strong and evidence_level in WEAK_EVIDENCE_LEVELS:
                    status = "missing"
                    evidence_ref = ""
                    notes = f"{notes}; weak_evidence_cannot_support_strong_claim"

        row = {
            "line_no": claim["line_no"],
            "claim": claim_text,
            "status": status,
            "evidence_ref": evidence_ref,
            "notes": notes,
        }
        audit_rows.append(row)
        if status != "pass":
            missing_rows.append(row)
    return audit_rows, missing_rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--claim-manifest")
    parser.add_argument("--output", required=True)
    parser.add_argument("--missing", required=True)
    args = parser.parse_args()
    audit_rows, missing_rows = audit(Path(args.report), Path(args.claim_manifest) if args.claim_manifest else None)
    write_rows(Path(args.output), audit_rows)
    write_rows(Path(args.missing), missing_rows)
    if missing_rows:
        raise SystemExit(f"missing evidence for {len(missing_rows)} report claims")
    print("OK")


if __name__ == "__main__":
    main()
