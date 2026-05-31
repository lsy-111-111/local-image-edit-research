from __future__ import annotations

import argparse
import re
from pathlib import Path

from scripts.common import A_LABELS, ensure_parent, evidence_missing, read_csv_rows, read_jsonl, write_csv_rows, write_jsonl


BLOCKED_FAMILY_TYPES = {"wrapper", "api_wrapper", "product_feature", "product", "demo", "implementation"}

REGISTRY_FIELDS = [
    "model_id",
    "model_name",
    "family_id",
    "family_name",
    "record_type",
    "candidate_label",
    "is_model_family",
    "parent_family_id",
    "implementation_type",
    "adapter",
    "version_lock",
    "version_risk",
    "source_type",
    "source_url",
    "evidence_quote",
    "evidence_quote_context",
    "evidence_level",
    "last_verified_date",
    "review_status",
    "evidence_entry_id",
    "decision",
    "decision_reason",
    "requires_human_review",
    "risk_flags",
]
FAMILY_FIELDS = [
    "family_id",
    "family_name",
    "family_type",
    "parent_family_id",
    "source_type",
    "source_url",
    "evidence_quote",
    "evidence_quote_context",
    "evidence_level",
    "last_verified_date",
    "review_status",
    "decision_reason",
    "notes",
]
VERSION_FIELDS = [
    "version_id",
    "family_id",
    "version_name",
    "version_lock",
    "version_risk",
    "release_date",
    "source_type",
    "source_url",
    "evidence_quote",
    "evidence_quote_context",
    "evidence_level",
    "last_verified_date",
    "review_status",
    "decision_reason",
    "notes",
]
IMPLEMENTATION_FIELDS = [
    "implementation_id",
    "family_id",
    "implementation_type",
    "parent_implementation_id",
    "source_type",
    "source_url",
    "evidence_quote",
    "evidence_quote_context",
    "evidence_level",
    "last_verified_date",
    "review_status",
    "decision_reason",
    "notes",
]
PROVIDER_FIELDS = [
    "provider",
    "adapter_name",
    "model_id",
    "public_model_name",
    "underlying_model",
    "record_type",
    "version_lock",
    "version_risk",
    "evidence_entry_id",
    "human_review_status",
    "adapter",
    "provider_model_ref",
    "input_schema_ref",
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
    "review_status",
    "notes",
]
PILOT_FIELDS = [
    "model_id",
    "model_name",
    "family_id",
    "record_type",
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
    "review_status",
    "evidence_entry_id",
    "version_lock",
    "version_risk",
]
UNCERTAIN_FIELDS = [
    "case_id",
    "source_path",
    "record_type",
    "issue",
    "decision",
    "decision_reason",
    "requires_human_review",
]


def safe_id(value: object, prefix: str) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or prefix


def entry_id(record: dict[str, object], index: int) -> str:
    return str(record.get("entry_id") or record.get("candidate_id") or f"entry_{index:04d}")


def blocked_record_type(record_type: str) -> bool:
    return record_type.strip().lower() in BLOCKED_FAMILY_TYPES


def human_review_by_entry(path: Path) -> dict[str, dict[str, str]]:
    return {row.get("entry_id", ""): row for row in read_csv_rows(path)}


def is_registry_approved(review: dict[str, str] | None) -> bool:
    if not review:
        return False
    return (
        review.get("allowed_for_registry", "").strip().lower() == "yes"
        and review.get("review_status", "").strip().lower() == "approved"
        and review.get("decision", "").strip().lower() in {"approved", "accept", "allow", "registry_approved"}
    )


def review_decision_reason(review: dict[str, str] | None) -> str:
    if not review:
        return "missing human review row"
    return review.get("decision_reason", "").strip() or "human review has not approved registry use"


def provider_rows_by_model(path: Path) -> dict[str, dict[str, str]]:
    return {row.get("model_id", ""): row for row in read_csv_rows(path)}


def build(
    evidence_path: Path,
    human_review_path: Path,
    existing_provider_map_path: Path,
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    registry: list[dict[str, object]] = []
    family_by_id: dict[str, dict[str, object]] = {}
    versions: list[dict[str, object]] = []
    implementations: list[dict[str, object]] = []
    provider_map: list[dict[str, object]] = []
    pilot_candidates: list[dict[str, object]] = []
    uncertain: list[dict[str, object]] = []

    reviews = human_review_by_entry(human_review_path)
    provider_candidates = provider_rows_by_model(existing_provider_map_path)

    for index, record in enumerate(read_jsonl(evidence_path), start=1):
        current_entry_id = entry_id(record, index)
        candidate_id = str(record.get("candidate_id") or safe_id(record.get("candidate_name"), "candidate"))
        record_type = str(record.get("record_type", "")).strip()
        review = reviews.get(current_entry_id)
        approved = is_registry_approved(review)
        missing = evidence_missing(record)
        if not str(record.get("evidence_quote_context", "")).strip():
            missing.append("evidence_quote_context")
        if str(record.get("candidate_label", "")).strip() not in A_LABELS:
            missing.append("candidate_label_not_A0_A1_A2")
        is_blocked = blocked_record_type(record_type)

        if not approved or missing or is_blocked:
            issue_parts = []
            if not approved:
                issue_parts.append("human_review_not_approved")
            if missing:
                issue_parts.append("evidence_not_registry_ready:" + "|".join(missing))
            if is_blocked:
                issue_parts.append("record_type_not_independent_family")
            uncertain.append(
                {
                    "case_id": candidate_id,
                    "source_path": evidence_path.as_posix(),
                    "record_type": record_type,
                    "issue": ";".join(issue_parts),
                    "decision": "blocked_from_registry",
                    "decision_reason": review_decision_reason(review),
                    "requires_human_review": "yes",
                }
            )
            continue

        family_name = str(record.get("model_family") or record.get("candidate_name") or "unknown").strip()
        family_id = safe_id(family_name, "family")
        version_lock = str(record.get("version_lock") or "D_unversioned")
        version_risk = str(record.get("version_risk") or ("version_unlocked" if version_lock == "D_unversioned" else ""))
        is_model_family = "true" if record_type == "model_family" else "false"
        decision_reason = review_decision_reason(review)
        registry_row = {
            "model_id": candidate_id,
            "model_name": record.get("candidate_name", ""),
            "family_id": family_id,
            "family_name": family_name,
            "record_type": record_type,
            "candidate_label": record.get("candidate_label", ""),
            "is_model_family": is_model_family,
            "parent_family_id": "",
            "implementation_type": "",
            "adapter": provider_candidates.get(candidate_id, {}).get("adapter", ""),
            "version_lock": version_lock,
            "version_risk": version_risk,
            "source_type": record.get("source_type", ""),
            "source_url": record.get("source_url", ""),
            "evidence_quote": record.get("evidence_quote", ""),
            "evidence_quote_context": record.get("evidence_quote_context", ""),
            "evidence_level": record.get("evidence_level", ""),
            "last_verified_date": record.get("last_verified_date", ""),
            "review_status": "approved",
            "evidence_entry_id": current_entry_id,
            "decision": "registry_approved",
            "decision_reason": decision_reason,
            "requires_human_review": "no",
            "risk_flags": "version_unlocked" if version_lock == "D_unversioned" else "",
        }
        registry.append(registry_row)

        if family_id not in family_by_id:
            family_by_id[family_id] = {
                "family_id": family_id,
                "family_name": family_name,
                "family_type": "model_family",
                "parent_family_id": "",
                "source_type": record.get("source_type", ""),
                "source_url": record.get("source_url", ""),
                "evidence_quote": record.get("evidence_quote", ""),
                "evidence_quote_context": record.get("evidence_quote_context", ""),
                "evidence_level": record.get("evidence_level", ""),
                "last_verified_date": record.get("last_verified_date", ""),
                "review_status": "approved",
                "decision_reason": decision_reason,
                "notes": "Human-approved family row generated from evidence.",
            }
        if record_type == "model_version":
            versions.append(
                {
                    "version_id": candidate_id,
                    "family_id": family_id,
                    "version_name": record.get("candidate_name", ""),
                    "version_lock": version_lock,
                    "version_risk": version_risk,
                    "release_date": "",
                    "source_type": record.get("source_type", ""),
                    "source_url": record.get("source_url", ""),
                    "evidence_quote": record.get("evidence_quote", ""),
                    "evidence_quote_context": record.get("evidence_quote_context", ""),
                    "evidence_level": record.get("evidence_level", ""),
                    "last_verified_date": record.get("last_verified_date", ""),
                    "review_status": "approved",
                    "decision_reason": decision_reason,
                    "notes": "Human-approved version row generated from evidence.",
                }
            )
        if record_type == "implementation":
            implementations.append(
                {
                    "implementation_id": candidate_id,
                    "family_id": family_id,
                    "implementation_type": "implementation",
                    "parent_implementation_id": "",
                    "source_type": record.get("source_type", ""),
                    "source_url": record.get("source_url", ""),
                    "evidence_quote": record.get("evidence_quote", ""),
                    "evidence_quote_context": record.get("evidence_quote_context", ""),
                    "evidence_level": record.get("evidence_level", ""),
                    "last_verified_date": record.get("last_verified_date", ""),
                    "review_status": "approved",
                    "decision_reason": decision_reason,
                    "notes": "Human-approved implementation row generated from evidence.",
                }
            )
        pilot_candidates.append(
            {
                "model_id": candidate_id,
                "model_name": record.get("candidate_name", ""),
                "family_id": family_id,
                "record_type": record_type,
                "source_url": record.get("source_url", ""),
                "evidence_quote": record.get("evidence_quote", ""),
                "evidence_level": record.get("evidence_level", ""),
                "last_verified_date": record.get("last_verified_date", ""),
                "review_status": "approved",
                "evidence_entry_id": current_entry_id,
                "version_lock": version_lock,
                "version_risk": version_risk,
            }
        )
        provider = provider_candidates.get(candidate_id)
        if provider:
            provider_map.append(
                {
                    "provider": provider.get("adapter", ""),
                    "adapter_name": provider.get("adapter", ""),
                    "model_id": candidate_id,
                    "public_model_name": record.get("candidate_name", ""),
                    "underlying_model": family_id,
                    "record_type": record_type,
                    "version_lock": version_lock,
                    "version_risk": version_risk,
                    "evidence_entry_id": current_entry_id,
                    "human_review_status": "approved",
                    "adapter": provider.get("adapter", ""),
                    "provider_model_ref": provider.get("provider_model_ref", ""),
                    "input_schema_ref": provider.get("input_schema_ref", ""),
                    "source_url": provider.get("source_url", record.get("source_url", "")),
                    "evidence_quote": provider.get("evidence_quote", record.get("evidence_quote", "")),
                    "evidence_level": provider.get("evidence_level", record.get("evidence_level", "")),
                    "last_verified_date": provider.get("last_verified_date", record.get("last_verified_date", "")),
                    "review_status": "approved",
                    "notes": provider.get("notes", ""),
                }
            )

    return registry, list(family_by_id.values()), versions, implementations, provider_map, pilot_candidates, uncertain


def write_docs(family_tree: Path, decision_log: Path, registry_count: int, uncertain_count: int) -> None:
    ensure_parent(family_tree)
    family_tree.write_text(
        "\n".join(
            [
                "# Family Tree",
                "",
                "Generated from human-approved evidence only.",
                "",
                f"- approved_registry_records: {registry_count}",
                f"- uncertain_records: {uncertain_count}",
                "",
                "No unreviewed evidence is promoted into the family tree.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    ensure_parent(decision_log)
    decision_log.write_text(
        "\n".join(
            [
                "# Decision Log",
                "",
                "Step 03 registry generation uses `allowed_for_registry=yes` and approved human review rows only.",
                "",
                f"- approved_registry_records: {registry_count}",
                f"- uncertain_records: {uncertain_count}",
                "- wrapper/product/demo/API records are blocked from independent model_family promotion.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", "--input", default="data/evidence/extracted_entries.jsonl")
    parser.add_argument("--human-review", default="data/evidence/evidence_human_review.csv")
    parser.add_argument("--existing-provider-map", default="data/registry/provider_model_map.csv")
    parser.add_argument("--output", "--registry", default="data/registry/model_registry.jsonl")
    parser.add_argument("--families", default="data/registry/model_family.csv")
    parser.add_argument("--versions", default="data/registry/model_version.csv")
    parser.add_argument("--implementations", default="data/registry/implementation.csv")
    parser.add_argument("--provider-model-map", default="data/registry/provider_model_map.csv")
    parser.add_argument("--pilot-candidates", default="data/registry/pilot_candidates.csv")
    parser.add_argument("--uncertain", default="data/registry/uncertain_cases.csv")
    parser.add_argument("--family-tree", default="docs/family_tree.md")
    parser.add_argument("--decision-log", default="docs/decision_log.md")
    args = parser.parse_args()

    registry, families, versions, implementations, provider_map, pilot_candidates, uncertain = build(
        Path(args.evidence),
        Path(args.human_review),
        Path(args.existing_provider_map),
    )
    write_jsonl(Path(args.output), registry)
    write_csv_rows(Path(args.families), families, FAMILY_FIELDS)
    write_csv_rows(Path(args.versions), versions, VERSION_FIELDS)
    write_csv_rows(Path(args.implementations), implementations, IMPLEMENTATION_FIELDS)
    write_csv_rows(Path(args.provider_model_map), provider_map, PROVIDER_FIELDS)
    write_csv_rows(Path(args.pilot_candidates), pilot_candidates, PILOT_FIELDS)
    write_csv_rows(Path(args.uncertain), uncertain, UNCERTAIN_FIELDS)
    write_docs(Path(args.family_tree), Path(args.decision_log), len(registry), len(uncertain))
    print(
        "registry="
        f"{len(registry)} families={len(families)} versions={len(versions)} "
        f"provider_map={len(provider_map)} pilot_candidates={len(pilot_candidates)} uncertain={len(uncertain)}"
    )


if __name__ == "__main__":
    main()
