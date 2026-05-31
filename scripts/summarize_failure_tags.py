from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from scripts.common import ensure_parent, read_csv_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--human")
    parser.add_argument("--input")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    human_path = args.human or args.input
    if not human_path:
        raise SystemExit("--human or --input is required")
    counter: Counter[str] = Counter()
    for row in read_csv_rows(Path(human_path)):
        for tag in str(row.get("failure_tags", "")).split(";"):
            tag = tag.strip()
            if tag:
                counter[tag] += 1
    lines = ["# Failure Tag Summary", ""]
    if not counter:
        lines.append("No failure tags have been merged yet.")
    else:
        for tag, count in counter.most_common():
            lines.append(f"- {tag}: {count}")
    out = Path(args.output)
    ensure_parent(out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
