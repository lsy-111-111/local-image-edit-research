from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import ensure_parent, read_csv_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = read_csv_rows(Path(args.input))
    lines = ["# Monthly Company/API Reverify Checklist", ""]
    if not rows:
        lines.append("No company/API rows are present yet.")
    else:
        for row in rows:
            company = row.get("company", "unknown")
            product = row.get("product", "unknown")
            lines.append(f"- [ ] Reverify `{company}` / `{product}` evidence, pricing, rate limit, API availability, and version lock.")
    out = Path(args.output)
    ensure_parent(out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
