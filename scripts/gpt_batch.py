from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import read_jsonl, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input)
    prompt_path = Path(args.prompt)
    if not prompt_path.exists():
        raise SystemExit(f"missing prompt: {prompt_path}")

    pages = read_jsonl(input_path)
    if args.dry_run:
        write_jsonl(Path(args.output), [])
        print(f"dry-run: {len(pages)} pages checked; no model records generated")
        return

    raise SystemExit("gpt_batch.py requires an explicit model extraction backend; use --dry-run in this scaffold")


if __name__ == "__main__":
    main()
