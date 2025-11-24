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
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

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
        self.refresh()

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


