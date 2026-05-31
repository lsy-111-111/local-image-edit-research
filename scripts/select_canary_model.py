from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import ensure_parent, read_csv_rows, write_csv_rows


CANARY_FIELDS = [
    "model_id",
    "model_name",
    "adapter",
    "version_lock",
    "version_risk",
    "provider_model_ref",
    "input_schema_ref",
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
    "human_review_status",
    "evidence_entry_id",
]


def approved_rows(path: Path) -> list[dict[str, str]]:
    return [
        row
        for row in read_csv_rows(path)
        if row.get("human_review_status", "").strip().lower() == "approved"
        and row.get("review_status", "").strip().lower() == "approved"
    ]


def canary_row(row: dict[str, str]) -> dict[str, str]:
    return {
        "model_id": row.get("model_id", ""),
        "model_name": row.get("public_model_name", row.get("model_id", "")),
        "adapter": row.get("adapter") or row.get("adapter_name", ""),
        "version_lock": row.get("version_lock", "") or "D_unversioned",
        "version_risk": row.get("version_risk", "") or "version_unlocked",
        "provider_model_ref": row.get("provider_model_ref", ""),
        "input_schema_ref": row.get("input_schema_ref", ""),
        "source_url": row.get("source_url", ""),
        "evidence_quote": row.get("evidence_quote", ""),
        "evidence_level": row.get("evidence_level", ""),
        "last_verified_date": row.get("last_verified_date", ""),
        "human_review_status": row.get("human_review_status", ""),
        "evidence_entry_id": row.get("evidence_entry_id", ""),
    }


def write_summary(path: Path, selected: list[dict[str, str]], provider_map: Path) -> None:
    ensure_parent(path)
    if selected:
        lines = [
            "# Adapter Canary REAL_001 Summary",
            "",
            "adapter_canary_gate: ready",
            "",
            "summary:",
            "- approved provider/model selected for one-adapter canary",
            f"- adapter_name: {selected[0].get('adapter', '')}",
            f"- model_id: {selected[0].get('model_id', '')}",
            "- scope: contract, metadata, structured failures, runtime, and cost recording only",
            "",
            "model_quality_conclusion: none",
        ]
    else:
        lines = [
            "# Adapter Canary REAL_001 Summary",
            "",
            "adapter_canary_gate: blocked",
            "",
            "blocking_reasons:",
            f"- no human-approved provider/model rows in {provider_map.as_posix()}",
            "- API credentials and cost authorization must be confirmed before real adapter execution",
            "",
            "metadata_status: not_run",
            "model_quality_conclusion: none",
        ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider-model-map", default="data/registry/provider_model_map.csv")
    parser.add_argument("--output", default="data/registry/canary_model.csv")
    parser.add_argument("--summary", default="reports/adapter_canary_REAL_001_summary.md")
    args = parser.parse_args()

    provider_map = Path(args.provider_model_map)
    selected = [canary_row(row) for row in approved_rows(provider_map)[:1]]
    write_csv_rows(Path(args.output), selected, CANARY_FIELDS)
    write_summary(Path(args.summary), selected, provider_map)
    if not selected:
        print("canary selection blocked: no human-approved provider/model rows")
    else:
        print(f"selected canary model: {selected[0]['model_id']}")


if __name__ == "__main__":
    main()
