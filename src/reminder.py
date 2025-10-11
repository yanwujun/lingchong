#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
提醒系统模块
Reminder Module - 负责任务提醒功能
"""

import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont

# 导入音效管理器和主题
try:
    from src.sound_manager import get_sound_manager
    from src.themes import apply_theme_to_widget
except ImportError:
    try:
        from sound_manager import get_sound_manager
        from themes import apply_theme_to_widget
    except ImportError:
        get_sound_manager = None
        apply_theme_to_widget = None


class ReminderPopup(QWidget):
    """提醒弹窗"""
    
    # 信号
    completed = pyqtSignal(int)
    snoozed = pyqtSignal(int, int)
    dismissed = pyqtSignal(int)
    
    def __init__(self, task_info, parent=None):
        super().__init__(parent)
        self.task_info = task_info
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        # 窗口设置
        self.setWindowTitle("⏰ 任务提醒")
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setFixedSize(400, 250)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 图标和标题
        header_layout = QHBoxLayout()
        
        icon_label = QLabel("⏰")
        icon_label.setFont(QFont("", 32))
        
        title_label = QLabel("任务提醒")
        title_label.setFont(QFont("", 16, QFont.Bold))
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # 任务标题
        task_title = QLabel(self.task_info.get('title', '未知任务'))
        task_title.setFont(QFont("", 14, QFont.Bold))
        task_title.setWordWrap(True)
        task_title.setStyleSheet("color: #333; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(task_title)
        
        # 任务描述
        if self.task_info.get('description'):
            desc_label = QLabel(self.task_info['description'][:100] + "...")
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666;")
            layout.addWidget(desc_label)
        
        # 截止时间
        if self.task_info.get('due_date'):
            due_label = QLabel(f"📅 截止时间: {self.task_info['due_date']}")
            due_label.setStyleSheet("color: #ff5722; font-weight: bold;")
            layout.addWidget(due_label)
        
        layout.addStretch()
        
        # 按钮组
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 标记完成按钮
        complete_btn = QPushButton("✅ 标记完成")
        complete_btn.clicked.connect(self.on_complete)
        complete_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # 稍后提醒按钮
        snooze_btn = QPushButton("⏱️ 稍后提醒")
        snooze_btn.clicked.connect(self.on_snooze)
        snooze_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        
        # 关闭按钮
        dismiss_btn = QPushButton("❌ 关闭")
        dismiss_btn.clicked.connect(self.on_dismiss)
        dismiss_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        button_layout.addWidget(complete_btn)
        button_layout.addWidget(snooze_btn)
        button_layout.addWidget(dismiss_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 应用主题 [v0.3.0]
        if apply_theme_to_widget:
            apply_theme_to_widget(self, 'reminder_popup', 'light')
        
        # 居中显示
        self.center_on_screen()
    
    def center_on_screen(self):
        """居中显示在屏幕上"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def on_complete(self):
        """标记完成"""
        task_id = self.task_info.get('id')
        if task_id:
            self.completed.emit(task_id)
        self.close()
    
    def on_snooze(self):
        """稍后提醒（5分钟后）"""
        task_id = self.task_info.get('id')
        if task_id:
            self.snoozed.emit(task_id, 5)  # 5分钟后
        self.close()
    
    def on_dismiss(self):
        """关闭提醒"""
        task_id = self.task_info.get('id')
        if task_id:
            self.dismissed.emit(task_id)
        self.close()


class ReminderSystem(QObject):
    """提醒系统"""
    
    # 定义信号
    completed = pyqtSignal(int)  # 任务完成信号
    snoozed = pyqtSignal(int, int)  # 任务延后信号 (task_id, minutes)
    
    def __init__(self, database, pet_window=None):
        """
        初始化提醒系统
        
        Args:
            database: 数据库实例
            pet_window: 宠物窗口实例（用于触发动画）
        """
        super().__init__()
        self.database = database
        self.pet_window = pet_window
        
        # 检查定时器
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_reminders)
        
        # 提醒窗口列表
        self.reminder_windows = []
        
        # 已提醒的任务ID集合（避免重复提醒）
        self.reminded_tasks = set()
    
    def start(self, interval=60000):
        """
        启动提醒系统
        
        Args:
            interval: 检查间隔（毫秒），默认60秒
        """
        self.check_timer.start(interval)
        print(f"[提醒系统] 启动成功，检查间隔: {interval/1000}秒")
        
        # 立即检查一次
        self.check_reminders()
    
    def stop(self):
        """停止提醒系统"""
        self.check_timer.stop()
        print("[提醒系统] 已停止")
    
    def check_reminders(self):
        """检查待提醒的任务"""
        if not self.database:
            return
        
        # 获取待提醒任务
        pending_tasks = self.database.get_pending_reminders()
        
        for task in pending_tasks:
            task_id = task['id']
            
            # 避免重复提醒
            if task_id in self.reminded_tasks:
                continue
            
            # 显示提醒
            self.show_reminder(task)
            
            # 标记已提醒
            self.reminded_tasks.add(task_id)
            
            # 触发宠物提醒动画
            if self.pet_window:
                self.pet_window.show_reminder(task)
            
            print(f"[提醒系统] 提醒任务: {task['title']}")
    
    def show_reminder(self, task_info):
        """显示提醒弹窗"""
        popup = ReminderPopup(task_info)
        
        # 连接信号
        popup.completed.connect(self.on_task_completed)
        popup.snoozed.connect(self.on_task_snoozed)
        popup.dismissed.connect(self.on_task_dismissed)
        
        # 显示弹窗
        popup.show()
        
        # 保存引用
        self.reminder_windows.append(popup)
        
        # 播放提醒音效 [v0.3.0]
        if get_sound_manager:
            sound_mgr = get_sound_manager()
            sound_mgr.play_alert()
    
    def on_task_completed(self, task_id):
        """任务完成回调"""
        if self.database:
            self.database.mark_completed(task_id)
        print(f"[提醒系统] 任务 {task_id} 已完成")
        # 发送信号
        self.completed.emit(task_id)
    
    def on_task_snoozed(self, task_id, minutes):
        """任务延后回调"""
        # 计算新的提醒时间
        new_remind_time = datetime.now() + timedelta(minutes=minutes)
        remind_time_str = new_remind_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 更新数据库
        if self.database:
            self.database.update_task(task_id, remind_time=remind_time_str)
        
        # 从已提醒集合中移除，允许再次提醒
        self.reminded_tasks.discard(task_id)
        
        print(f"[提醒系统] 任务 {task_id} 延后 {minutes} 分钟")
        # 发送信号
        self.snoozed.emit(task_id, minutes)
    
    def on_task_dismissed(self, task_id):
        """提醒关闭回调"""
        print(f"[提醒系统] 任务 {task_id} 提醒已关闭")
    
    def add_reminder(self, task_id, remind_time):
        """
        添加提醒
        
        Args:
            task_id: 任务ID
            remind_time: 提醒时间（datetime或字符串）
        """
        if isinstance(remind_time, datetime):
            remind_time = remind_time.strftime("%Y-%m-%d %H:%M:%S")
        
        if self.database:
            self.database.update_task(task_id, remind_time=remind_time)
            print(f"[提醒系统] 为任务 {task_id} 设置提醒: {remind_time}")
    
    def remove_reminder(self, task_id):
        """移除提醒"""
        if self.database:
            self.database.update_task(task_id, remind_time=None)
            print(f"[提醒系统] 移除任务 {task_id} 的提醒")
    
    def get_upcoming_reminders(self, hours=24):
        """
        获取未来N小时内的提醒
        
        Args:
            hours: 小时数
        
        Returns:
            任务列表
        """
        # TODO: 实现获取即将到来的提醒
        pass


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 测试提醒弹窗
    test_task = {
        'id': 1,
        'title': '完成项目文档',
        'description': '编写桌面灵宠应用的开发需求文档和技术实现方案',
        'due_date': '2025-10-15 18:00:00',
        'priority': 3
    }
    
    popup = ReminderPopup(test_task)
    popup.show()
    
    print("=" * 60)
    print("提醒弹窗测试")
    print("=" * 60)
    print("测试任务：", test_task['title'])
    print("=" * 60)
    
    sys.exit(app.exec_())

