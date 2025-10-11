#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
番茄钟桌面小组件模块
Pomodoro Widget Module - 桌面悬浮计时器显示
"""

import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QPainter, QColor, QPen

class PomodoroWidget(QWidget):
    """番茄钟桌面小组件"""
    
    def __init__(self, pomodoro_manager=None, parent=None):
        super().__init__(parent)
        self.pomodoro_manager = pomodoro_manager
        self.is_dragging = False
        self.drag_position = QPoint()
        self.init_ui()
        
        if self.pomodoro_manager:
            self.connect_signals()
    
    def init_ui(self):
        """初始化界面"""
        # 窗口设置
        self.setWindowTitle("番茄钟")
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(120, 120)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 时间标签
        self.time_label = QLabel("25:00")
        self.time_label.setFont(QFont("", 20, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: white;")
        layout.addWidget(self.time_label)
        
        # 类型标签
        self.type_label = QLabel("🍅")
        self.type_label.setFont(QFont("", 24))
        self.type_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.type_label)
        
        self.setLayout(layout)
        
        # 初始位置（屏幕右上角）
        self.move_to_corner()
    
    def move_to_corner(self):
        """移动到屏幕右上角"""
        screen = QApplication.desktop().screenGeometry()
        self.move(screen.width() - self.width() - 20, 20)
    
    def connect_signals(self):
        """连接信号"""
        if not self.pomodoro_manager:
            return
        
        timer = self.pomodoro_manager.timer
        timer.tick.connect(self.on_tick)
        timer.session_started.connect(self.on_session_started)
        timer.session_completed.connect(self.on_session_completed)
        timer.session_cancelled.connect(self.on_session_cancelled)
    
    def on_tick(self, remaining_seconds):
        """每秒更新"""
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        self.update()  # 重绘进度环
    
    def on_session_started(self, session_type):
        """会话开始"""
        icons = {'work': '🍅', 'short_break': '☕', 'long_break': '🌴'}
        self.type_label.setText(icons.get(session_type, '🍅'))
        
        # 显示小组件
        self.show()
    
    def on_session_completed(self, session_type, duration):
        """会话完成"""
        self.time_label.setText("完成!")
        # 3秒后隐藏
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, self.reset_display)
    
    def on_session_cancelled(self):
        """会话取消"""
        self.reset_display()
    
    def reset_display(self):
        """重置显示"""
        self.time_label.setText("25:00")
        self.type_label.setText("🍅")
        self.update()
    
    def paintEvent(self, event):
        """绘制事件 - 绘制圆形背景和进度环"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆形背景
        painter.setBrush(QColor(76, 175, 80, 230))  # 半透明绿色
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(10, 10, 100, 100)
        
        # 绘制进度环
        if self.pomodoro_manager and self.pomodoro_manager.timer.is_running:
            progress = self.pomodoro_manager.timer.get_progress()
            
            # 进度环设置
            pen = QPen(QColor(255, 255, 255, 200))
            pen.setWidth(4)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            
            # 绘制进度弧
            start_angle = 90 * 16  # Qt使用1/16度
            span_angle = -int(progress * 360 * 16)
            painter.drawArc(15, 15, 90, 90, start_angle, span_angle)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.LeftButton and self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
    
    def mouseDoubleClickEvent(self, event):
        """双击事件 - 打开主窗口"""
        if event.button() == Qt.LeftButton:
            # 触发信号通知主程序打开番茄钟主窗口
            print("[番茄钟小组件] 双击，应打开主窗口")
            # 这里可以发送信号或调用回调


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    widget = PomodoroWidget()
    widget.show()
    
    sys.exit(app.exec_())

