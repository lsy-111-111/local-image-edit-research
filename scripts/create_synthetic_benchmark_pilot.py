from __future__ import annotations

import argparse
from pathlib import Path

from scripts.common import ensure_parent, sha256_file, write_csv_rows

try:
    from PIL import Image, ImageDraw
except ImportError as exc:  # pragma: no cover - exercised only in missing dependency environments
    raise SystemExit("Pillow is required to generate PNG benchmark assets") from exc


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
    ("T03", "insert a small green plant beside the chair", "在椅子旁添加一盆绿色小植物", "object insertion"),
    ("T04", "change the cube color to teal", "将立方体颜色改为青绿色", "color editing"),
    ("T05", "change only the cup material to ceramic", "仅将杯子材质改为陶瓷", "material editing"),
    ("T06", "make only the poster area watercolor style", "仅将海报区域改成水彩风格", "local style editing"),
    ("T07", "replace the background with a simple studio backdrop", "将背景替换为简洁影棚背景", "background replacement"),
    ("T08", "make the lamp warmer without changing the desk", "让灯光更暖但不改变桌面", "lighting editing"),
    ("T09", "make a tiny pose-neutral expression mark happier", "让合成头像的微表情更开心", "expression micro edit"),
    ("T10", "change the jacket color to green", "把外套颜色改为绿色", "clothing edit"),
    ("T11", "add a soft product shadow under the bottle", "在瓶子下方添加柔和商品阴影", "product image edit"),
    ("T12", "replace the poster text with HELLO", "将海报文字改为 HELLO", "text-in-image edit"),
    ("T13", "insert an object matching the reference color swatch", "插入与参考色块匹配的物体", "reference-guided insertion"),
    ("T14", "apply the second edit while preserving the first edit", "在保留第一次修改的同时执行第二处修改", "multi-turn edit"),
    ("T15", "repair the tiny scratch on the panel", "修复面板上的细小划痕", "small object fine edit"),
    ("T16", "edit the reflected object without changing the mirror edge", "编辑反射中的物体但不改变镜面边缘", "occlusion/reflection complex edit"),
]
MASK_QUALITIES = ["high", "medium", "rough", "none", "high", "medium", "rough"]


def draw_source(task_id: str, index: int, path: Path) -> None:
    ensure_parent(path)
    bg = [(246, 244, 236), (238, 244, 247), (242, 239, 249), (245, 242, 235)][index % 4]
    accent = [(215, 92, 92), (65, 139, 210), (72, 157, 103), (211, 157, 66)][index % 4]
    image = Image.new("RGB", (512, 512), bg)
    draw = ImageDraw.Draw(image)
    draw.rectangle((52, 62, 460, 438), outline=(38, 42, 48), width=3)
    draw.rectangle((78, 98, 216, 236), fill=accent, outline=(30, 34, 40), width=2)
    draw.ellipse((310, 106, 430, 226), fill=(108, 112, 126), outline=(30, 34, 40), width=2)
    draw.rounded_rectangle((112, 306, 404, 384), radius=10, fill=(57, 66, 78))
    draw.rectangle((284, 274, 386, 312), fill=(250, 245, 220), outline=(30, 34, 40), width=2)
    draw.text((88, 452), f"{task_id} synthetic scene", fill=(32, 36, 42))
    image.save(path)


def draw_mask(task_id: str, quality: str, path: Path) -> None:
    ensure_parent(path)
    image = Image.new("L", (512, 512), 0)
    draw = ImageDraw.Draw(image)
    if quality == "high":
        draw.rectangle((76, 96, 220, 240), fill=255)
    elif quality == "medium":
        draw.ellipse((58, 78, 246, 256), fill=255)
    else:
        draw.polygon([(62, 118), (236, 74), (260, 236), (98, 270)], fill=255)
    image.save(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", default="data/benchmark/source_images")
    parser.add_argument("--masks", default="data/benchmark/masks")
    parser.add_argument("--prompts", default="data/benchmark/task_prompts.csv")
    parser.add_argument("--cases", default="data/benchmark/benchmark_cases.csv")
    parser.add_argument("--pilot-cases", default="data/benchmark/pilot_cases_100.csv")
    parser.add_argument("--core-smoke", default="data/benchmark/core_cases_smoke_100.csv")
    args = parser.parse_args()

    image_root = Path(args.images)
    mask_root = Path(args.masks)
    prompt_rows = []
    case_rows = []

    for task_index, (task_id, prompt_en_base, prompt_zh_base, expected_change) in enumerate(TASKS, start=1):
        image_path = image_root / f"{task_id}_source.png"
        draw_source(task_id, task_index, image_path)
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
                mask_file = mask_root / f"{task_id}_{quality_suffix(mask_quality, case_variant)}.png"
                if not mask_file.exists():
                    draw_mask(task_id, mask_quality, mask_file)
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
                    "image_type": "synthetic_png",
                    "target_size": "512",
                    "mask_quality": mask_quality,
                    "language": "bilingual",
                    "difficulty": ["easy", "medium", "hard", "medium", "hard", "medium", "hard"][case_variant - 1],
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
    sampled = balanced_sample_100(case_rows)
    write_csv_rows(Path(args.pilot_cases), sampled, CASE_FIELDS)
    write_csv_rows(Path(args.core_smoke), sampled, CASE_FIELDS)
    print("created 112 PNG benchmark cases; pilot/core smoke case sets contain 100 validated cases")


def quality_suffix(mask_quality: str, case_variant: int) -> str:
    return f"{mask_quality}_{case_variant:02d}"


def balanced_sample_100(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_task: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_task.setdefault(str(row["task_id"]), []).append(row)
    sampled: list[dict[str, object]] = []
    for task_id in sorted(by_task):
        sampled.extend(by_task[task_id][:6])
    for task_id in sorted(by_task)[:4]:
        sampled.append(by_task[task_id][6])
    return sampled


if __name__ == "__main__":
    main()
