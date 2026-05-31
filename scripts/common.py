from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Iterable


A_LABELS = {"A0", "A1", "A2"}
ALLOWED_CANDIDATE_LABELS = {"A0", "A1", "A2", "B", "C", "D", "X"}
ALLOWED_EVIDENCE_LEVELS = {"E0", "E1", "E2", "E3", "E4", "E5", ""}
ALLOWED_SOURCE_TYPES = {
    "official_docs",
    "official_api_docs",
    "official_model_card",
    "official_github",
    "paper",
    "release_note",
}
REQUIRED_EVIDENCE_FIELDS = [
    "source_type",
    "source_url",
    "evidence_quote",
    "evidence_level",
    "last_verified_date",
]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def is_missing(value: object) -> bool:
    return value is None or str(value).strip() == ""


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def write_csv_rows(path: Path, rows: Iterable[dict[str, object]], fieldnames: list[str]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                value = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_no}: JSONL record must be an object")
            records.append(value)
    return records


def write_jsonl(path: Path, records: Iterable[dict[str, object]]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def valid_iso_date(value: object) -> bool:
    if is_missing(value):
        return False
    text = str(value).strip()
    if DATE_RE.match(text) is None:
        return False
    year, month, day = [int(part) for part in text.split("-")]
    if not (1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2100):
        return False
    return True


def evidence_missing(record: dict[str, object]) -> list[str]:
    missing = [field for field in REQUIRED_EVIDENCE_FIELDS if is_missing(record.get(field))]
    if not is_missing(record.get("last_verified_date")) and not valid_iso_date(record.get("last_verified_date")):
        missing.append("last_verified_date_format")
    if str(record.get("evidence_level", "")).strip() not in ALLOWED_EVIDENCE_LEVELS:
        missing.append("evidence_level_allowed")
    if str(record.get("source_type", "")).strip() not in ALLOWED_SOURCE_TYPES:
        missing.append("source_type_allowed")
    return missing


def split_values(value: object) -> list[str]:
    if is_missing(value):
        return ["unknown"]
    text = str(value).strip()
    parts = re.split(r"[;,|]", text)
    cleaned = [part.strip() for part in parts if part.strip()]
    return cleaned or ["unknown"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail_with_errors(errors: list[str]) -> None:
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit(1)
    print("OK")
