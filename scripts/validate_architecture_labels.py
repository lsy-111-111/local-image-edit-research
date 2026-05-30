from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import fail_with_errors, is_missing, read_jsonl, split_values, valid_iso_date


BASE = {f"G{i}" for i in range(10)} | {"unknown"}
CONTROL = {"C_mask", "C_auto_mask", "C_box", "C_scribble", "C_reference", "C_text_edit", "C_multiturn", "unknown"}
TRAINING = {"T_finetuned", "T_instruction", "T_inversion", "T_training_free", "T_composite", "T_closed", "unknown"}
DEPLOYMENT = {"D_local", "D_weights", "D_api", "D_web", "D_seed", "D_no_seed", "D_versioned", "D_unversioned", "unknown"}
ARCH_PUBLIC = {"public", "partial", "unknown"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    for index, record in enumerate(read_jsonl(path), start=1):
        for value in split_values(record.get("base_architecture")):
            if value not in BASE:
                errors.append(f"{path}:{index}: invalid base_architecture {value}")
        for value in split_values(record.get("control_mechanism")):
            if value not in CONTROL:
                errors.append(f"{path}:{index}: invalid control_mechanism {value}")
        for value in split_values(record.get("training_or_inference")):
            if value not in TRAINING:
                errors.append(f"{path}:{index}: invalid training_or_inference {value}")
        for value in split_values(record.get("deployment")):
            if value not in DEPLOYMENT:
                errors.append(f"{path}:{index}: invalid deployment {value}")
        arch_public = str(record.get("architecture_public", "unknown")).strip() or "unknown"
        if arch_public not in ARCH_PUBLIC:
            errors.append(f"{path}:{index}: invalid architecture_public {arch_public}")
        non_unknown = []
        for field in ["base_architecture", "control_mechanism", "training_or_inference", "deployment"]:
            non_unknown.extend([value for value in split_values(record.get(field)) if value != "unknown"])
        if non_unknown and is_missing(record.get("evidence_quote")):
            errors.append(f"{path}:{index}: non-unknown labels requires evidence_quote")
        if not is_missing(record.get("last_verified_date")) and not valid_iso_date(record.get("last_verified_date")):
            errors.append(f"{path}:{index}: invalid last_verified_date")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="data/registry/architecture_labels.jsonl")
    args = parser.parse_args()
    fail_with_errors(validate(Path(args.input)))


if __name__ == "__main__":
    main()
