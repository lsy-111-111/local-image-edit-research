from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import ensure_parent, sha256_file, write_csv_rows


CASE_FIELDS = [
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
TASK_PROMPT_FIELDS = ["task_id", "prompt_en", "prompt_zh", "expected_change", "preserve_requirements", "safety_notes"]


TASKS = [
    ("T01", "replace the red cube with a blue sphere", "将红色立方体替换为蓝色球体", "object replacement"),
    ("T02", "remove the small sign from the table", "移除桌面上的小标牌", "object removal"),
    ("T03", "change the poster text to HELLO", "将海报文字改为 HELLO", "text editing"),
    ("T04", "make the lamp warmer without changing the desk", "让灯光更暖但不改变桌面", "local color change"),
    ("T05", "add a small plant beside the chair", "在椅子旁添加一盆小植物", "object insertion"),
    ("T06", "change only the cup material to ceramic", "仅将杯子材质改为陶瓷", "material edit"),
    ("T07", "turn the window area into rainy weather", "将窗户区域改成雨天", "local scene change"),
    ("T08", "make the logo area blank", "清空标志区域", "logo removal"),
    ("T09", "change the shirt color to green", "把衬衫颜色改为绿色", "appearance edit"),
    ("T10", "add a shadow under the product", "在产品下方添加阴影", "lighting edit"),
    ("T11", "extend the left background with the same pattern", "向左扩展相同图案背景", "outpaint-like edit"),
    ("T12", "replace the sky patch with sunset colors", "将天空区域替换为日落色", "background edit"),
    ("T13", "make the book cover minimal", "将书封面改成极简风格", "style edit"),
    ("T14", "move the badge to the upper right", "将徽章移到右上角", "layout edit"),
    ("T15", "restore the scratched area on the panel", "修复面板上的划痕区域", "restoration"),
    ("T16", "perform a second small edit while preserving the first", "在保留第一次修改的同时做第二处小修改", "multi-step edit"),
]
MASK_QUALITIES = ["high", "medium", "rough", "none", "high"]


def svg(path: Path, title: str, body: str) -> None:
    ensure_parent(path)
    path.write_text(
        "\n".join(
            [
                '<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">',
                f"<title>{title}</title>",
                '<rect width="512" height="512" fill="#f7f7f2"/>',
                body,
                "</svg>",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def source_svg(task_id: str, index: int, path: Path) -> None:
    color = ["#d95f5f", "#4d8fd9", "#4d9f68", "#d9a64d"][index % 4]
    body = "\n".join(
        [
            f'<rect x="72" y="88" width="152" height="152" rx="8" fill="{color}"/>',
            '<circle cx="330" cy="180" r="64" fill="#6f6f78"/>',
            '<rect x="118" y="300" width="276" height="72" rx="6" fill="#39424e"/>',
            f'<text x="96" y="456" font-size="32" fill="#20242a">{task_id} synthetic scene</text>',
        ]
    )
    svg(path, f"{task_id} synthetic source", body)


def mask_svg(task_id: str, quality: str, path: Path) -> None:
    if quality == "high":
        body = '<rect x="70" y="86" width="156" height="156" fill="#ffffff"/>'
    elif quality == "medium":
        body = '<ellipse cx="148" cy="164" rx="96" ry="84" fill="#ffffff"/>'
    else:
        body = '<polygon points="60,112 236,72 254,236 98,260" fill="#ffffff"/>'
    svg(path, f"{task_id} {quality} mask", '<rect width="512" height="512" fill="#000000"/>\n' + body)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", default="data/benchmark/source_images")
    parser.add_argument("--masks", default="data/benchmark/masks")
    parser.add_argument("--prompts", default="data/benchmark/task_prompts.csv")
    parser.add_argument("--cases", default="data/benchmark/benchmark_cases.csv")
    parser.add_argument("--core-smoke", default="data/benchmark/core_cases_smoke_100.csv")
    args = parser.parse_args()

    image_root = Path(args.images)
    mask_root = Path(args.masks)
    prompt_rows = []
    case_rows = []

    for task_index, (task_id, prompt_en_base, prompt_zh_base, expected_change) in enumerate(TASKS, start=1):
        image_path = image_root / f"{task_id}_source.svg"
        source_svg(task_id, task_index, image_path)
        for case_variant, mask_quality in enumerate(MASK_QUALITIES, start=1):
            prompt_en = f"{prompt_en_base}; case variant {case_variant}"
            prompt_zh = f"{prompt_zh_base}；案例变体 {case_variant}"
            preserve = "preserve all unmasked regions, identity-neutral shapes, layout, and synthetic background"
            safety = "synthetic scene only; no real person, trademark, or copyrighted subject"
            prompt_rows.append(
                {
                    "task_id": task_id,
                    "prompt_en": prompt_en,
                    "prompt_zh": prompt_zh,
                    "expected_change": expected_change,
                    "preserve_requirements": preserve,
                    "safety_notes": safety,
                }
            )
            mask_path = ""
            mask_hash = ""
            if mask_quality != "none":
                mask_file = mask_root / f"{task_id}_{mask_quality}.svg"
                if not mask_file.exists():
                    mask_svg(task_id, mask_quality, mask_file)
                mask_path = mask_file.as_posix()
                mask_hash = sha256_file(mask_file)
            case_rows.append(
                {
                    "case_id": f"{task_id}_case_{case_variant:02d}",
                    "image_path": image_path.as_posix(),
                    "image_sha256": sha256_file(image_path),
                    "mask_path": mask_path,
                    "mask_sha256": mask_hash,
                    "task_id": task_id,
                    "image_type": "synthetic_svg",
                    "target_size": "512",
                    "mask_quality": mask_quality,
                    "language": "bilingual",
                    "difficulty": ["easy", "medium", "hard", "medium", "hard"][case_variant - 1],
                    "copyright_status": "synthetic_codex_generated",
                    "prompt_en": prompt_en,
                    "prompt_zh": prompt_zh,
                    "expected_change": expected_change,
                    "preserve_requirements": preserve,
                    "safety_notes": safety,
                }
            )

    write_csv_rows(Path(args.prompts), prompt_rows, TASK_PROMPT_FIELDS)
    write_csv_rows(Path(args.cases), case_rows, CASE_FIELDS)
    write_csv_rows(Path(args.core_smoke), [], CASE_FIELDS)
    print("created 80 benchmark pilot cases; core smoke remains header-only until 100 validated cases exist")


if __name__ == "__main__":
    main()
