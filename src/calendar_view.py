#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日历视图模块
Calendar View Module - 日历方式显示任务分布
"""

import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QGridLayout, QCalendarWidget)
from PyQt5.QtCore import Qt, QDate

try:
    from src.jingyeqian_ui import JYQButton, JYQ_COLORS
except ImportError:
    try:
        from jingyeqian_ui import JYQButton, JYQ_COLORS
    except ImportError:
        JYQButton = QPushButton
        JYQ_COLORS = {'primary': '#007AFF'}


class CalendarView(QWidget):
    """日历视图"""
    
    def __init__(self, database=None, parent=None):
        super().__init__(parent)
        self.database = database
        self.init_ui()
        self.load_tasks()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 日历组件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_selected)
        layout.addWidget(self.calendar)
        
        # 选中日期的任务列表
        self.task_label = QLabel("选择日期查看任务")
        layout.addWidget(self.task_label)
        
        self.setLayout(layout)
    
    def load_tasks(self):
        """加载任务"""
        if not self.database:
            return
        
        # 获取所有任务
        tasks = self.database.get_all_tasks()
        
        # 标记有任务的日期
        task_dates = {}
        for task in tasks:
            if task.get('due_date'):
                try:
                    date_str = task['due_date'][:10]  # 只取日期部分
                    if date_str not in task_dates:
                        task_dates[date_str] = []
                    task_dates[date_str].append(task)
                except:
                    pass
        
        # 设置日期格式
        date_format = QDate.fromString
        
        # 这里可以设置日期背景色来标记有任务的日期
        # 简化实现
    
    def on_date_selected(self, date: QDate):
        """日期选择事件"""
        if not self.database:
            return
        
        date_str = date.toString("yyyy-MM-dd")
        
        # 获取该日期的任务
        tasks = self.database.get_all_tasks()
        day_tasks = [
            t for t in tasks 
            if t.get('due_date') and t['due_date'].startswith(date_str)
        ]
        
        if day_tasks:
            task_text = f"{date_str} 的任务：\n"
            for task in day_tasks:
                task_text += f"- {task['title']}\n"
            self.task_label.setText(task_text)
        else:
            self.task_label.setText(f"{date_str} 没有任务")


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    view = CalendarView()
    view.show()
    
    sys.exit(app.exec_())

