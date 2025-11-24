#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全局快捷键模块
Global Hotkey Module - 注册全局快捷键
"""

import sys
from typing import Dict, Callable, Optional

# 尝试导入快捷键库
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("[全局快捷键] keyboard库未安装，全局快捷键功能不可用")

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QObject, pyqtSignal
except ImportError:
    QObject = object
    pyqtSignal = None


class GlobalHotkeyManager(QObject if 'QObject' in globals() else object):
    """全局快捷键管理器"""
    
    # 信号
    hotkey_triggered = pyqtSignal(str) if 'pyqtSignal' in globals() else None
    
    def __init__(self, parent=None):
        super().__init__(parent) if 'QObject' in globals() else None
        self.hotkeys: Dict[str, Callable] = {}
        self.registered_hotkeys: Dict[str, bool] = {}
        
        if not KEYBOARD_AVAILABLE:
            print("[全局快捷键] 警告：keyboard库未安装，全局快捷键功能不可用")
    
    def register_hotkey(self, hotkey: str, callback: Callable, description: str = "") -> bool:
        """
        注册全局快捷键
        
        Args:
            hotkey: 快捷键字符串，如 'ctrl+shift+n'
            callback: 回调函数
            description: 描述
        
        Returns:
            是否成功
        """
        if not KEYBOARD_AVAILABLE:
            return False
        
        try:
            # 转换快捷键格式
            normalized_hotkey = self._normalize_hotkey(hotkey)
            
            # 如果已注册，先取消
            if normalized_hotkey in self.registered_hotkeys:
                self.unregister_hotkey(hotkey)
            
            # 注册快捷键
            keyboard.add_hotkey(normalized_hotkey, callback)
            
            self.hotkeys[normalized_hotkey] = callback
            self.registered_hotkeys[normalized_hotkey] = True
            
            print(f"[全局快捷键] 注册成功: {normalized_hotkey} - {description}")
            return True
            
        except Exception as e:
            print(f"[全局快捷键] 注册失败: {hotkey} - {e}")
            return False
    
    def unregister_hotkey(self, hotkey: str) -> bool:
        """
        取消注册全局快捷键
        
        Args:
            hotkey: 快捷键字符串
        
        Returns:
            是否成功
        """
        if not KEYBOARD_AVAILABLE:
            return False
        
        try:
            normalized_hotkey = self._normalize_hotkey(hotkey)
            
            if normalized_hotkey in self.registered_hotkeys:
                keyboard.remove_hotkey(normalized_hotkey)
                del self.hotkeys[normalized_hotkey]
                del self.registered_hotkeys[normalized_hotkey]
                print(f"[全局快捷键] 取消注册: {normalized_hotkey}")
                return True
            
            return False
            
        except Exception as e:
            print(f"[全局快捷键] 取消注册失败: {hotkey} - {e}")
            return False
    
    def _normalize_hotkey(self, hotkey: str) -> str:
        """
        标准化快捷键格式
        
        Args:
            hotkey: 快捷键字符串
        
        Returns:
            标准化后的快捷键
        """
        # 转换为小写
        hotkey = hotkey.lower()
        
        # 替换常见格式
        hotkey = hotkey.replace('ctrl', 'ctrl')
        hotkey = hotkey.replace('alt', 'alt')
        hotkey = hotkey.replace('shift', 'shift')
        hotkey = hotkey.replace('win', 'windows')
        
        return hotkey
    
    def register_default_hotkeys(self, callbacks: Dict[str, Callable]):
        """
        注册默认快捷键
        
        Args:
            callbacks: 回调函数字典，键为快捷键，值为回调函数
        """
        default_hotkeys = {
            'ctrl+shift+n': ('新建便签', callbacks.get('new_note')),
            'ctrl+shift+t': ('打开便签', callbacks.get('open_notes')),
            'ctrl+shift+p': ('命令面板', callbacks.get('command_palette')),
        }
        
        for hotkey, (description, callback) in default_hotkeys.items():
            if callback:
                self.register_hotkey(hotkey, callback, description)
    
    def unregister_all(self):
        """取消所有快捷键"""
        for hotkey in list(self.registered_hotkeys.keys()):
            self.unregister_hotkey(hotkey)


# 测试代码
if __name__ == "__main__":
    if KEYBOARD_AVAILABLE:
        manager = GlobalHotkeyManager()
        
        def test_callback():
            print("快捷键触发！")
        
        manager.register_hotkey('ctrl+shift+n', test_callback, "测试快捷键")
        
        print("全局快捷键已注册，按 Ctrl+Shift+N 测试")
        print("按 Ctrl+C 退出")
        
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            manager.unregister_all()
            print("已退出")
    else:
        print("keyboard库未安装，无法测试")

