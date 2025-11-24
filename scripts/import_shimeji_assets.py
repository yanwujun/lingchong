#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将 ShimejiEE-cross-platform 项目的 PNG 资源整理为桌面灵宠的角色包结构。

用法::

    python scripts/import_shimeji_assets.py \
        --source external/shimeji/ShimejiEE-cross-platform/ext-resources/img \
        --output assets/pets

脚本会遍历 source 目录下的每个角色文件夹，复制 PNG 帧至
`assets/pets/<pack_id>/frames/`，并根据预设动作映射生成 `pack.json`。
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


# 预设动作映射（帧号源自 Shimeji 原版 actions.xml）
ANIMATION_PRESET: Dict[str, Dict] = {
    "idle": {"frames": [1], "duration": 250, "loop": True, "tags": ["idle", "ground"]},
    "walk": {"frames": [1, 2, 1, 3], "duration": 80, "loop": True, "tags": ["move", "ground"]},
    "run": {"frames": [1, 2, 1, 3], "duration": 40, "loop": True, "tags": ["move", "ground"]},
    "crawl": {"frames": [20, 21, 20, 21], "duration": 90, "loop": True, "tags": ["move", "ground"]},
    "sit": {"frames": [11], "duration": 250, "loop": True, "tags": ["idle", "ground"]},
    "sit_look_up": {"frames": [26], "duration": 250, "loop": True, "tags": ["idle", "ground"]},
    "sit_dangle": {"frames": [31, 32, 31, 33], "duration": 120, "loop": True, "tags": ["idle", "edge"]},
    "sprawl": {"frames": [21], "duration": 250, "loop": True, "tags": ["idle", "ground"]},
    "climb_wall": {"frames": [14, 12, 13], "duration": 90, "loop": True, "tags": ["climb", "wall"]},
    "grab_wall": {"frames": [13], "duration": 250, "loop": True, "tags": ["climb", "wall"]},
    "climb_ceiling": {"frames": [25, 23, 24], "duration": 90, "loop": True, "tags": ["climb", "ceiling"]},
    "grab_ceiling": {"frames": [23], "duration": 250, "loop": True, "tags": ["climb", "ceiling"]},
    "fall": {"frames": [4], "duration": 120, "loop": True, "tags": ["fall"]},
    "jump": {"frames": [22], "duration": 120, "loop": True, "tags": ["jump"]},
    "bounce": {"frames": [18, 19], "duration": 80, "loop": True, "tags": ["impact"]},
    "dragged": {"frames": [9, 7, 5, 6, 8, 10], "duration": 60, "loop": True, "tags": ["drag"]},
    "stretch": {"frames": [26, 15, 27, 16, 28, 17, 29, 11], "duration": 80, "loop": True, "tags": ["idle"]},
    "happy": {"frames": [34, 35, 34, 36], "duration": 90, "loop": True, "tags": ["carry"]},
}

PACK_NAME_OVERRIDES = {
    "Shimeji": "经典白色 Shimeji",
    "red-shime": "红色 Shimeji",
    "dark-shime": "暗色 Shimeji",
    "greeen-shime": "绿色 Shimeji",
}


@dataclass
class AnimationFrame:
    path: str
    duration: int


@dataclass
class AnimationDefinition:
    name: str
    loop: bool
    tags: List[str]
    frames: List[AnimationFrame]


def copy_frames(source_dir: Path, target_dir: Path) -> List[str]:
    """复制源 PNG 帧至目标目录，并返回文件名列表。"""
    target_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for png_file in sorted(source_dir.glob("*.png")):
        dest = target_dir / png_file.name
        shutil.copy2(png_file, dest)
        copied.append(png_file.name)
    return copied


def build_animation(frame_names: List[str], preset: Dict) -> Optional[AnimationDefinition]:
    frames = []
    for idx in preset["frames"]:
        fname = f"shime{idx}.png"
        if fname not in frame_names:
            return None
        frames.append(AnimationFrame(path=f"frames/{fname}", duration=preset["duration"]))
    return AnimationDefinition(
        name=preset.get("alias", preset.get("name", "")) or "",
        loop=preset["loop"],
        tags=preset["tags"],
        frames=frames,
    )


def pack_metadata(pack_id: str, source_name: str, copied_frames: List[str]) -> Dict:
    display_name = PACK_NAME_OVERRIDES.get(source_name, source_name)
    return {
        "id": pack_id,
        "name": display_name,
        "source": {
            "name": "ShimejiEE-cross-platform",
            "url": "https://github.com/LavenderSnek/ShimejiEE-cross-platform",
            "pack_key": source_name,
        },
        "frame_size": [128, 128],
        "frame_anchor": [64, 128],
        "features": [
            "multi-instance",
            "climb_wall",
            "climb_ceiling",
            "fall",
            "drag",
        ],
        "available_frames": copied_frames,
    }


def generate_pack(source_dir: Path, output_dir: Path):
    pack_id = source_dir.name.replace(" ", "_").lower()
    target_root = output_dir / pack_id
    frames_dir = target_root / "frames"
    target_root.mkdir(parents=True, exist_ok=True)

    copied_frames = copy_frames(source_dir, frames_dir)
    metadata = pack_metadata(pack_id, source_dir.name, copied_frames)

    animations: Dict[str, Dict] = {}
    for anim_name, preset in ANIMATION_PRESET.items():
        anim = build_animation(copied_frames, {"name": anim_name, **preset})
        if not anim:
            continue
        animations[anim_name] = {
            "loop": anim.loop,
            "tags": anim.tags,
            "frames": [frame.__dict__ for frame in anim.frames],
        }

    metadata["animations"] = animations
    metadata["default_animation"] = "idle"

    pack_file = target_root / "pack.json"
    with pack_file.open("w", encoding="utf-8") as fp:
        json.dump(metadata, fp, ensure_ascii=False, indent=2)

    print(f"[IMPORT] 生成角色包: {metadata['name']} -> {pack_file}")


def main():
    parser = argparse.ArgumentParser(description="导入 Shimeji 资源为桌面灵宠角色包")
    parser.add_argument("--source", type=Path, required=True, help="Shimeji 图像资源目录")
    parser.add_argument("--output", type=Path, required=True, help="输出的角色包根目录")
    parser.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="只导入指定文件夹（使用目录名）",
    )
    args = parser.parse_args()

    if not args.source.exists():
        raise SystemExit(f"源目录不存在: {args.source}")

    args.output.mkdir(parents=True, exist_ok=True)

    for sub_dir in sorted(d for d in args.source.iterdir() if d.is_dir()):
        if args.only and sub_dir.name not in args.only:
            continue
        generate_pack(sub_dir, args.output)


if __name__ == "__main__":
    main()


