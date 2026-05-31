from __future__ import annotations

import argparse
import re
from pathlib import Path

from scripts.common import A_LABELS, read_jsonl, write_csv_rows, write_jsonl


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
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
    "review_status",
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
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
    "review_status",
    "notes",
]
VERSION_FIELDS = [
    "version_id",
    "family_id",
    "version_name",
    "version_lock",
    "release_date",
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
    "review_status",
    "notes",
]
IMPLEMENTATION_FIELDS = [
    "implementation_id",
    "family_id",
    "implementation_type",
    "parent_implementation_id",
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
    "review_status",
    "notes",
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


def blocked_record_type(record_type: str) -> bool:
    return record_type.strip().lower() in BLOCKED_FAMILY_TYPES


def build(input_path: Path) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    registry: list[dict[str, object]] = []
    family_by_id: dict[str, dict[str, object]] = {}
    versions: list[dict[str, object]] = []
    implementations: list[dict[str, object]] = []
    uncertain: list[dict[str, object]] = []

    for record in read_jsonl(input_path):
        candidate_id = str(record.get("candidate_id") or safe_id(record.get("candidate_name"), "candidate"))
        record_type = str(record.get("record_type", "")).strip()
        family_name = str(record.get("model_family") or record.get("candidate_name") or "unknown").strip()
        family_id = safe_id(family_name, "family")
        is_blocked = blocked_record_type(record_type)
        is_a_label = str(record.get("candidate_label", "")).strip() in A_LABELS
        review_status = str(record.get("review_status") or "needs_review")
        requires_review = "yes" if review_status == "needs_review" or is_blocked else "no"

        if is_blocked:
            decision = "not_model_family"
            decision_reason = f"{record_type} must not be counted as an independent model family"
            is_model_family = "false"
        elif not is_a_label:
            decision = "not_promoted"
            decision_reason = "candidate label is not A0/A1/A2"
            is_model_family = "false"
        else:
            decision = "registry_draft"
            decision_reason = "source-backed candidate; human review required before factual use"
            is_model_family = "true" if record_type == "model_family" else "false"

        registry_row = {
            "model_id": candidate_id,
            "model_name": record.get("candidate_name", ""),
            "family_id": "" if is_blocked else family_id,
            "family_name": family_name,
            "record_type": record_type,
            "candidate_label": record.get("candidate_label", ""),
            "is_model_family": is_model_family,
            "parent_family_id": "",
            "implementation_type": "",
            "adapter": "mock",
            "version_lock": "D_unversioned",
            "source_url": record.get("source_url", ""),
            "evidence_quote": record.get("evidence_quote", ""),
            "evidence_level": record.get("evidence_level", ""),
            "last_verified_date": record.get("last_verified_date", ""),
            "review_status": review_status,
            "decision": decision,
            "decision_reason": decision_reason,
            "requires_human_review": requires_review,
            "risk_flags": "version_unlocked;human_review_required",
        }
        registry.append(registry_row)

        if is_blocked or review_status == "needs_review" or not is_a_label:
            uncertain.append(
                {
                    "case_id": candidate_id,
                    "source_path": input_path.as_posix(),
                    "record_type": record_type,
                    "issue": "classification_or_evidence_needs_review",
                    "decision": decision,
                    "decision_reason": decision_reason,
                    "requires_human_review": "yes",
                }
            )

        if is_blocked or not is_a_label:
            continue

        if family_id not in family_by_id:
            family_by_id[family_id] = {
                "family_id": family_id,
                "family_name": family_name,
                "family_type": "model_family",
                "parent_family_id": "",
                "source_url": record.get("source_url", ""),
                "evidence_quote": record.get("evidence_quote", ""),
                "evidence_level": record.get("evidence_level", ""),
                "last_verified_date": record.get("last_verified_date", ""),
                "review_status": "needs_review",
                "notes": "Draft family row generated from evidence; human factual review required.",
            }

        if record_type == "model_version":
            versions.append(
                {
                    "version_id": candidate_id,
                    "family_id": family_id,
                    "version_name": record.get("candidate_name", ""),
                    "version_lock": "D_unversioned",
                    "release_date": "",
                    "source_url": record.get("source_url", ""),
                    "evidence_quote": record.get("evidence_quote", ""),
                    "evidence_level": record.get("evidence_level", ""),
                    "last_verified_date": record.get("last_verified_date", ""),
                    "review_status": "needs_review",
                    "notes": "Version lock unresolved; do not use for core until reviewed.",
                }
            )

    return registry, list(family_by_id.values()), versions, implementations, uncertain


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/evidence/extracted_entries.jsonl")
    parser.add_argument("--registry", default="data/registry/model_registry.jsonl")
    parser.add_argument("--families", default="data/registry/model_family.csv")
    parser.add_argument("--versions", default="data/registry/model_version.csv")
    parser.add_argument("--implementations", default="data/registry/implementation.csv")
    parser.add_argument("--uncertain", default="data/registry/uncertain_cases.csv")
    args = parser.parse_args()

    registry, families, versions, implementations, uncertain = build(Path(args.input))
    write_jsonl(Path(args.registry), registry)
    write_csv_rows(Path(args.families), families, FAMILY_FIELDS)
    write_csv_rows(Path(args.versions), versions, VERSION_FIELDS)
    write_csv_rows(Path(args.implementations), implementations, IMPLEMENTATION_FIELDS)
    write_csv_rows(Path(args.uncertain), uncertain, UNCERTAIN_FIELDS)
    print(f"registry={len(registry)} families={len(families)} versions={len(versions)} uncertain={len(uncertain)}")


if __name__ == "__main__":
    main()
