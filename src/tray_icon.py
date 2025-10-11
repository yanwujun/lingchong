#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统托盘模块
System Tray Module - 负责系统托盘图标和菜单
"""

import sys
import os
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal

# 导入工具函数
try:
    from src.utils import get_resource_path
except ImportError:
    from utils import get_resource_path


class SystemTray(QSystemTrayIcon):
    """系统托盘类"""
    
    # 信号
    show_pet_signal = pyqtSignal()
    hide_pet_signal = pyqtSignal()
    show_todo_signal = pyqtSignal()
    show_settings_signal = pyqtSignal()
    quit_signal = pyqtSignal()
    
    def __init__(self, icon_path="assets/icons/tray_icon.png", parent=None):
        """
        初始化系统托盘
        
        Args:
            icon_path: 托盘图标路径
            parent: 父对象
        """
        super().__init__(parent)
        
        # 设置图标（使用资源路径函数）
        full_icon_path = get_resource_path(icon_path)
        icon = QIcon(full_icon_path)
        if icon.isNull():
            # 如果图标加载失败，使用默认图标
            print(f"[托盘] 警告: 无法加载图标 {icon_path}")
        else:
            print(f"[托盘] 加载图标成功: {icon_path}")
        self.setIcon(icon)
        
        # 设置提示文本
        self.setToolTip("桌面灵宠 - Desktop Pet")
        
        # 创建菜单
        self.menu = QMenu()
        self.create_menu()
        
        # 设置菜单
        self.setContextMenu(self.menu)
        
        # 连接信号
        self.activated.connect(self.on_activated)
        
        print("[托盘] 系统托盘初始化成功")
    
    def create_menu(self):
        """创建托盘菜单"""
        # 显示/隐藏宠物
        self.show_action = QAction("显示宠物", self)
        self.show_action.triggered.connect(self.show_pet_signal.emit)
        self.menu.addAction(self.show_action)
        
        self.hide_action = QAction("隐藏宠物", self)
        self.hide_action.triggered.connect(self.hide_pet_signal.emit)
        self.menu.addAction(self.hide_action)
        
        self.menu.addSeparator()
        
        # 待办事项
        todo_action = QAction("📝 待办事项", self)
        todo_action.triggered.connect(self.show_todo_signal.emit)
        self.menu.addAction(todo_action)
        
        # 设置
        settings_action = QAction("⚙️ 设置", self)
        settings_action.triggered.connect(self.show_settings_signal.emit)
        self.menu.addAction(settings_action)
        
        self.menu.addSeparator()
        
        # 退出
        quit_action = QAction("❌ 退出", self)
        quit_action.triggered.connect(self.quit_signal.emit)
        self.menu.addAction(quit_action)
    
    def on_activated(self, reason):
        """
        托盘图标被激活
        
        Args:
            reason: 激活原因
        """
        if reason == QSystemTrayIcon.Trigger:
            # 单击托盘图标 - 显示宠物
            self.show_pet_signal.emit()
        elif reason == QSystemTrayIcon.DoubleClick:
            # 双击托盘图标 - 打开待办窗口
            self.show_todo_signal.emit()
    
    def show_notification(self, title, message, icon=QSystemTrayIcon.Information, duration=3000):
        """
        显示托盘通知
        
        Args:
            title: 通知标题
            message: 通知内容
            icon: 图标类型
            duration: 显示时长（毫秒）
        """
        self.showMessage(title, message, icon, duration)
        print(f"[托盘] 显示通知: {title} - {message}")
    
    def update_tooltip(self, text):
        """更新提示文本"""
        self.setToolTip(text)


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 创建托盘图标
    tray = SystemTray()
    
    # 连接信号
    tray.show_pet_signal.connect(lambda: print("[测试] 显示宠物"))
    tray.hide_pet_signal.connect(lambda: print("[测试] 隐藏宠物"))
    tray.show_todo_signal.connect(lambda: print("[测试] 打开待办"))
    tray.show_settings_signal.connect(lambda: print("[测试] 打开设置"))
    tray.quit_signal.connect(lambda: app.quit())
    
    # 显示托盘
    tray.show()
    
    # 测试通知
    tray.show_notification("测试", "系统托盘测试消息")
    
    print("=" * 60)
    print("系统托盘测试")
    print("=" * 60)
    print("提示：右键点击托盘图标可以看到菜单")
    print("=" * 60)
    
    sys.exit(app.exec_())

