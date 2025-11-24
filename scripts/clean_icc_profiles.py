#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量移除 PNG 文件中的损坏 ICC Profile，避免 Qt/libpng 输出 “iCCP: known incorrect sRGB profile” 警告。

用法:
    python scripts/clean_icc_profiles.py

脚本会扫描 assets/images/default、assets/icons 以及 assets/pets 下的 PNG 文件，
若检测到 icc_profile 元数据，则重新保存以移除该 Profile。
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    raise SystemExit("该脚本依赖 Pillow，请先执行 `pip install Pillow`")


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGETS = [
    ROOT / "assets" / "images" / "default",
    ROOT / "assets" / "icons",
    ROOT / "assets" / "pets",
]


def iter_png_files(path: Path) -> Iterable[Path]:
    if path.is_file() and path.suffix.lower() == ".png":
        yield path
        return
    if not path.exists():
        return
    for file in path.rglob("*.png"):
        if file.is_file():
            yield file


def strip_icc_profile(png_path: Path) -> bool:
    try:
        with Image.open(png_path) as img:
            icc = img.info.get("icc_profile")
            if not icc:
                return False
            img.load()
            tmp_path = png_path.with_suffix(png_path.suffix + ".icc_tmp")
            img.save(tmp_path, format="PNG", optimize=True)
            tmp_path.replace(png_path)
            return True
    except Exception as exc:
        print(f"[WARN] 处理 {png_path} 失败: {exc}")
        return False


def clean_directories(targets: Iterable[Path]) -> None:
    total = cleaned = 0
    for target in targets:
        if not target.exists():
            continue
        for png in iter_png_files(target):
            total += 1
            if strip_icc_profile(png):
                cleaned += 1
                print(f"[OK] 已移除 ICC Profile: {png}")
    print(f"[DONE] 共扫描 {total} 个 PNG，清理 {cleaned} 个文件")


def main():
    parser = argparse.ArgumentParser(description="移除 PNG 文件中的 ICC Profile")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="需要扫描的额外目录/文件（可选）",
    )
    args = parser.parse_args()

    targets = DEFAULT_TARGETS + args.paths
    clean_directories(targets)


if __name__ == "__main__":
    main()

