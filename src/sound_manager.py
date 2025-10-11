#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
音效管理模块
Sound Manager Module - 负责音效的加载和播放
"""

import os
import sys
from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtMultimedia import QSoundEffect

# 导入工具函数
try:
    from src.utils import get_resource_path
except ImportError:
    from utils import get_resource_path


class SoundManager(QObject):
    """音效管理器（单例模式）"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化音效管理器"""
        # 确保父类初始化总是被调用
        super().__init__()
        
        # 防止重复初始化业务逻辑
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        
        # 音效字典
        self.sounds = {}
        
        # 音效启用状态
        self.enabled = True
        
        # 音量（0.0 - 1.0）
        self.volume = 0.5
        
        # 加载音效
        self.load_sounds()
    
    def load_sounds(self):
        """加载所有音效文件"""
        sound_files = {
            'click': 'assets/sounds/click.wav',
            'alert': 'assets/sounds/alert.wav',
            'complete': 'assets/sounds/complete.wav',
            'hover': 'assets/sounds/hover.wav',
        }
        
        for name, relative_path in sound_files.items():
            sound_path = get_resource_path(relative_path)
            
            if os.path.exists(sound_path):
                try:
                    sound = QSoundEffect()
                    sound.setSource(QUrl.fromLocalFile(sound_path))
                    sound.setVolume(self.volume)
                    self.sounds[name] = sound
                    print(f"[音效] 加载成功: {name} <- {relative_path}")
                except Exception as e:
                    print(f"[音效] 加载失败: {name} - {e}")
            else:
                print(f"[音效] 文件不存在: {sound_path}")
        
        if self.sounds:
            print(f"[音效] 音效管理器初始化成功，已加载 {len(self.sounds)} 个音效")
        else:
            print("[音效] 警告：未找到任何音效文件，音效功能将不可用")
    
    def play(self, sound_name):
        """
        播放指定音效
        
        Args:
            sound_name: 音效名称（click/alert/complete/hover）
        """
        if not self.enabled:
            return
        
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"[音效] 播放失败: {sound_name} - {e}")
        else:
            print(f"[音效] 未找到音效: {sound_name}")
    
    def play_click(self):
        """播放点击音效"""
        self.play('click')
    
    def play_alert(self):
        """播放提醒音效"""
        self.play('alert')
    
    def play_complete(self):
        """播放完成音效"""
        self.play('complete')
    
    def play_hover(self):
        """播放悬停音效"""
        self.play('hover')
    
    def set_volume(self, volume):
        """
        设置音量
        
        Args:
            volume: 音量（0.0 - 1.0）
        """
        self.volume = max(0.0, min(1.0, volume))
        
        for sound in self.sounds.values():
            sound.setVolume(self.volume)
        
        print(f"[音效] 音量设置为: {int(self.volume * 100)}%")
    
    def set_enabled(self, enabled):
        """
        启用/禁用音效
        
        Args:
            enabled: 是否启用
        """
        self.enabled = enabled
        print(f"[音效] 音效{'启用' if enabled else '禁用'}")
    
    def is_available(self):
        """检查音效是否可用"""
        return len(self.sounds) > 0
    
    def get_loaded_sounds(self):
        """获取已加载的音效列表"""
        return list(self.sounds.keys())


# 全局音效管理器实例
_sound_manager = None

def get_sound_manager():
    """获取全局音效管理器"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import time
    
    app = QApplication(sys.argv)
    
    print("=" * 60)
    print("音效系统测试")
    print("=" * 60)
    
    # 创建音效管理器
    sound_mgr = get_sound_manager()
    
    print(f"\n音效可用性: {sound_mgr.is_available()}")
    print(f"已加载音效: {sound_mgr.get_loaded_sounds()}")
    
    if sound_mgr.is_available():
        print("\n播放测试音效（如果有音效文件）...")
        
        # 测试播放
        print("  播放点击音效...")
        sound_mgr.play_click()
        time.sleep(1)
        
        print("  播放提醒音效...")
        sound_mgr.play_alert()
        time.sleep(1)
        
        print("  播放完成音效...")
        sound_mgr.play_complete()
        time.sleep(1)
        
        # 测试音量调节
        print("\n测试音量调节...")
        sound_mgr.set_volume(0.3)
        sound_mgr.play_click()
        time.sleep(1)
        
        sound_mgr.set_volume(1.0)
        sound_mgr.play_click()
        time.sleep(1)
        
        # 测试禁用
        print("\n测试禁用音效...")
        sound_mgr.set_enabled(False)
        sound_mgr.play_click()  # 不应该播放
        
        sound_mgr.set_enabled(True)
        sound_mgr.play_click()  # 应该播放
    else:
        print("\n[提示] 未找到音效文件，请将音效文件放到 assets/sounds/ 目录")
        print("  需要的文件:")
        print("    - click.wav")
        print("    - alert.wav")
        print("    - complete.wav")
        print("    - hover.wav")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

