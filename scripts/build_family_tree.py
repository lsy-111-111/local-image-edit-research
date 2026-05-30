from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import ensure_parent, read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-md", required=True)
    args = parser.parse_args()

    records = read_jsonl(Path(args.input))
    lines = ["# Family Tree", ""]
    if not records:
        lines.append("No family tree has been generated from evidence yet.")
    else:
        lines.append("All entries below require human review before being treated as independent families.")
        lines.append("")
        for record in records:
            name = record.get("candidate_name", "unknown")
            reason = record.get("duplicate_reason", "needs_review")
            lines.append(f"- `{name}`: {reason}")
    out = Path(args.out_md)
    ensure_parent(out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
