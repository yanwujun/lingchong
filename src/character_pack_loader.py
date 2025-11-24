#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
角色包加载模块
================

负责扫描 `assets/pets` 目录下的 pack.json 文件，将其转换为
在 `PetWindow` 中可直接使用的动画定义。
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

try:  # Pillow is optional at runtime but strongly recommended
    from PIL import Image
except ImportError:  # pragma: no cover - Pillow 已在 requirements.txt 中声明
    Image = None

try:
    from src.utils import get_resource_path
except ImportError:  # pragma: no cover
    from utils import get_resource_path


@dataclass(frozen=True)
class AnimationFrame:
    path: Path
    duration: int


@dataclass
class CharacterAnimation:
    name: str
    loop: bool
    tags: List[str]
    frames: List[AnimationFrame]


@dataclass
class CharacterPack:
    pack_id: str
    name: str
    root_path: Path
    metadata: Dict
    animations: Dict[str, CharacterAnimation]

    @property
    def default_animation(self) -> str:
        return self.metadata.get("default_animation", "idle")

    def get_animation(self, name: str) -> Optional[CharacterAnimation]:
        return self.animations.get(name)

    def supports(self, feature: str) -> bool:
        return feature in self.metadata.get("features", [])


class CharacterPackLoader:
    """扫描并缓存角色包配置。"""

    def __init__(self, packs_root: Optional[Path] = None):
        self.packs_root = Path(
            packs_root or get_resource_path("assets/pets")
        ).resolve()
        self._packs: Dict[str, CharacterPack] = {}
        self._sanitized_dirs: Set[Path] = set()
        self.refresh()
        self._sanitize_default_assets()

    def refresh(self):
        """重新扫描角色包目录。"""
        self._packs.clear()
        if not self.packs_root.exists():
            return

        for pack_dir in sorted(p for p in self.packs_root.iterdir() if p.is_dir()):
            pack = self._load_pack(pack_dir)
            if pack:
                self._packs[pack.pack_id] = pack

    def _load_pack(self, pack_dir: Path) -> Optional[CharacterPack]:
        pack_file = pack_dir / "pack.json"
        if not pack_file.exists():
            return None

        self._sanitize_png_profiles(pack_dir)

        try:
            with pack_file.open("r", encoding="utf-8") as fp:
                metadata = json.load(fp)
        except json.JSONDecodeError as exc:
            print(f"[角色包] 解析失败 {pack_file}: {exc}")
            return None

        animations: Dict[str, CharacterAnimation] = {}
        for name, data in metadata.get("animations", {}).items():
            frames: List[AnimationFrame] = []
            for frame in data.get("frames", []):
                frame_path = (pack_dir / frame["path"]).resolve()
                if not frame_path.exists():
                    print(f"[角色包] 缺少帧 {frame_path}, 跳过 {name}")
                    frames = []
                    break
                frames.append(AnimationFrame(path=frame_path, duration=int(frame["duration"])))
            if not frames:
                continue
            animations[name] = CharacterAnimation(
                name=name,
                loop=data.get("loop", True),
                tags=data.get("tags", []),
                frames=frames,
            )

        pack_id = metadata.get("id") or pack_dir.name
        pack_name = metadata.get("name", pack_dir.name)
        return CharacterPack(
            pack_id=pack_id,
            name=pack_name,
            root_path=pack_dir,
            metadata=metadata,
            animations=animations,
        )

    def list_packs(self) -> List[CharacterPack]:
        return list(self._packs.values())

    def get_pack(self, pack_id: str) -> Optional[CharacterPack]:
        if not pack_id:
            return None
        pack = self._packs.get(pack_id)
        if pack:
            return pack
        # pack 被删除后尝试刷新
        self.refresh()
        return self._packs.get(pack_id)

    # ---------- PNG 清理逻辑 ----------

    def _sanitize_png_profiles(self, pack_dir: Path):
        """
        Qt 在加载带有损坏 ICC Profile 的 PNG 时会触发 libpng 警告，
        这里使用 Pillow 重新保存有问题的图片以移除无效的 profile。
        """
        if Image is None:
            print(f"[角色包] 跳过 PNG 清理（Pillow 未安装）: {pack_dir}")
            return
        if pack_dir in self._sanitized_dirs:
            print(f"[角色包] PNG 清理已缓存: {pack_dir}")
            return

        marker_file = pack_dir / ".icc_clean"
        marker_timestamp = 0.0
        if marker_file.exists():
            try:
                marker_timestamp = float(marker_file.read_text().strip() or "0")
            except Exception:
                marker_timestamp = marker_file.stat().st_mtime

        latest_png_mtime = 0.0
        png_files = list(pack_dir.rglob("*.png"))
        if not png_files:
            self._sanitized_dirs.add(pack_dir)
            return

        print(f"[角色包] 开始 PNG 清理: {pack_dir}, 共 {len(png_files)} 张")
        for png_file in png_files:
            try:
                latest_png_mtime = max(latest_png_mtime, png_file.stat().st_mtime)
            except OSError:
                continue

        if latest_png_mtime and marker_timestamp >= latest_png_mtime:
            self._sanitized_dirs.add(pack_dir)
            print(f"[角色包] 命中 PNG 清理缓存，跳过 {pack_dir}")
            return

        cleaned_any = False
        for png_path in png_files:
            try:
                with Image.open(png_path) as img:
                    icc_profile = img.info.get("icc_profile")
                    if not icc_profile:
                        continue
                    cleaned_any |= self._rewrite_png_without_profile(png_path, img)
            except Exception:
                continue

        try:
            marker_file.write_text(str(time.time()))
        except Exception:
            pass

        if cleaned_any:
            print(f"[角色包] 已修复 {pack_dir} 中的 PNG 颜色配置")
        else:
            print(f"[角色包] 未发现需要修复的 PNG: {pack_dir}")
        self._sanitized_dirs.add(pack_dir)

    def _sanitize_default_assets(self):
        """对默认动画资源目录执行一次 PNG 清理，以消除基础 GIF/PNG 的 ICC 告警。"""
        default_dir = Path(get_resource_path("assets/images/default")).resolve()
        if not default_dir.exists():
            return
        self._sanitize_png_profiles(default_dir)

    @staticmethod
    def _rewrite_png_without_profile(png_path: Path, image: "Image.Image") -> bool:
        """
        将带有 ICC Profile 的 PNG 重新保存为干净版本。
        """
        tmp_path = png_path.with_name(png_path.name + ".icc_tmp")
        try:
            image = image.convert("RGBA")
            image.save(tmp_path, format="PNG", optimize=True)
            tmp_path.replace(png_path)
            print(f"[角色包] 已移除 ICC Profile: {png_path}")
            return True
        except Exception as exc:
            print(f"[角色包] 修复 PNG 失败 {png_path}: {exc}")
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            return False

    def get_default_pack(self) -> Optional[CharacterPack]:
        if not self._packs:
            return None
        # 默认使用 config 中指定的 pack，如无则返回第一个
        return self._packs.get("shimeji") or next(iter(self._packs.values()))


_LOADER: Optional[CharacterPackLoader] = None


def get_character_pack_loader() -> CharacterPackLoader:
    global _LOADER
    if _LOADER is None:
        _LOADER = CharacterPackLoader()
    return _LOADER


