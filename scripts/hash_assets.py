from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import sha256_file, write_csv_rows


FIELDNAMES = ["path", "sha256", "size_bytes"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    rows = []
    if root.exists():
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            if path.name == ".gitkeep":
                continue
            rows.append(
                {
                    "path": path.as_posix(),
                    "sha256": sha256_file(path),
                    "size_bytes": path.stat().st_size,
                }
            )
    write_csv_rows(Path(args.output), rows, FIELDNAMES)
    print(f"hashed {len(rows)} files")


if __name__ == "__main__":
    main()
