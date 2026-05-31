from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) != sys.path[0]:
    while str(ROOT) in sys.path:
        sys.path.remove(str(ROOT))
    sys.path.insert(0, str(ROOT))

from scripts.common import ALLOWED_SOURCE_TYPES, fail_with_errors, is_missing, read_jsonl, sha256_file, valid_iso_date


REQUIRED_FIELDS = ["page_id", "source_url", "source_type", "retrieved_at", "title", "content_sha256"]


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(read_jsonl(path), start=1):
        for field in REQUIRED_FIELDS:
            if is_missing(row.get(field)):
                errors.append(f"{path}:{index}: missing {field}")
        if is_missing(row.get("text")) and is_missing(row.get("saved_path")):
            errors.append(f"{path}:{index}: missing text_or_saved_path")
        page_id = str(row.get("page_id", "")).strip()
        if page_id in seen:
            errors.append(f"{path}:{index}: duplicate page_id {page_id}")
        seen.add(page_id)
        source_type = str(row.get("source_type", "")).strip()
        if source_type not in ALLOWED_SOURCE_TYPES:
            errors.append(f"{path}:{index}: invalid source_type {source_type}")
        if not valid_iso_date(row.get("retrieved_at")):
            errors.append(f"{path}:{index}: invalid retrieved_at")
        content_sha256 = str(row.get("content_sha256", "")).strip()
        if not is_missing(row.get("text")):
            digest = hashlib.sha256(str(row.get("text", "")).encode("utf-8")).hexdigest()
            if content_sha256 and content_sha256 != digest:
                errors.append(f"{path}:{index}: content_sha256 mismatch")
        elif not is_missing(row.get("saved_path")):
            saved_path = Path(str(row.get("saved_path", "")))
            if not saved_path.exists():
                errors.append(f"{path}:{index}: saved_path does not exist")
            elif content_sha256 and content_sha256 != sha256_file(saved_path):
                errors.append(f"{path}:{index}: content_sha256 mismatch")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="data/raw/pages.jsonl")
    args = parser.parse_args()
    fail_with_errors(validate(Path(args.input)))


if __name__ == "__main__":
    main()
