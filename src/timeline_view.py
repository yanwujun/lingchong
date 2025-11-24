#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
时间轴视图模块
Timeline View Module - 时间轴方式显示任务和便签
"""

import sys
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen

try:
    from src.jingyeqian_ui import JYQ_COLORS
except ImportError:
    try:
        from jingyeqian_ui import JYQ_COLORS
    except ImportError:
        JYQ_COLORS = {'primary': '#007AFF', 'surface': '#FFFFFF'}


class TimelineView(QWidget):
    """时间轴视图"""
    
    def __init__(self, database=None, parent=None):
        super().__init__(parent)
        self.database = database
        self.items = []
        self.init_ui()
        self.load_items()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.create_timeline_widget())
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def create_timeline_widget(self):
        """创建时间轴组件"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 这里应该根据数据创建时间轴项目
        # 简化实现
        label = QLabel("时间轴视图（待实现）")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        widget.setLayout(layout)
        return widget
    
    def load_items(self):
        """加载时间轴项目"""
        if not self.database:
            return
        
        # 获取所有任务和便签，按时间排序
        tasks = self.database.get_all_tasks()
        notes = self.database.get_all_notes()
        
        # 合并并排序
        self.items = []
        for task in tasks:
            self.items.append({
                'type': 'task',
                'data': task,
                'time': task.get('created_at', '')
            })
        
        for note in notes:
            self.items.append({
                'type': 'note',
                'data': note,
                'time': note.get('created_at', '')
            })
        
        # 按时间排序
        self.items.sort(key=lambda x: x['time'])


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    view = TimelineView()
    view.show()
    
    sys.exit(app.exec_())

