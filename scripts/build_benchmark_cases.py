from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import read_csv_rows, sha256_file, write_csv_rows


FIELDNAMES = [
    "case_id",
    "image_path",
    "image_sha256",
    "mask_path",
    "mask_sha256",
    "task_id",
    "image_type",
    "target_size",
    "mask_quality",
    "language",
    "difficulty",
    "copyright_status",
    "prompt_en",
    "prompt_zh",
    "expected_change",
    "preserve_requirements",
    "safety_notes",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", required=True)
    parser.add_argument("--masks", required=True)
    parser.add_argument("--prompts", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    images_root = Path(args.images)
    prompts = read_csv_rows(Path(args.prompts))
    images = sorted(path for path in images_root.rglob("*") if path.is_file()) if images_root.exists() else []
    rows = []
    for index, (image, prompt) in enumerate(zip(images, prompts), start=1):
        task_id = prompt.get("task_id", "")
        rows.append(
            {
                "case_id": f"case_{index:05d}",
                "image_path": image.as_posix(),
                "image_sha256": sha256_file(image),
                "mask_path": "",
                "mask_sha256": "",
                "task_id": task_id,
                "image_type": "unknown",
                "target_size": "",
                "mask_quality": "none",
                "language": "mixed",
                "difficulty": "unknown",
                "copyright_status": "needs_review",
                "prompt_en": prompt.get("prompt_en", ""),
                "prompt_zh": prompt.get("prompt_zh", ""),
                "expected_change": prompt.get("expected_change", ""),
                "preserve_requirements": prompt.get("preserve_requirements", ""),
                "safety_notes": prompt.get("safety_notes", ""),
            }
        )
    write_csv_rows(Path(args.output), rows, FIELDNAMES)
    print(f"built {len(rows)} benchmark cases")


if __name__ == "__main__":
    main()
