#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
看板视图模块
Kanban View Module - 看板方式显示任务
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QLabel, QPushButton)
from PyQt5.QtCore import Qt

try:
    from src.jingyeqian_ui import (JYQButton, JYQListWidget, JYQCard, JYQ_COLORS)
except ImportError:
    try:
        from jingyeqian_ui import (JYQButton, JYQListWidget, JYQCard, JYQ_COLORS)
    except ImportError:
        JYQButton = QPushButton
        JYQListWidget = QListWidget
        JYQCard = QWidget
        JYQ_COLORS = {'primary': '#007AFF'}


class KanbanView(QWidget):
    """看板视图"""
    
    def __init__(self, database=None, parent=None):
        super().__init__(parent)
        self.database = database
        self.init_ui()
        self.load_tasks()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 看板列
        columns_layout = QHBoxLayout()
        
        # 待办列
        self.todo_column = self.create_column("待办", "pending")
        columns_layout.addWidget(self.todo_column)
        
        # 进行中列
        self.in_progress_column = self.create_column("进行中", "in_progress")
        columns_layout.addWidget(self.in_progress_column)
        
        # 已完成列
        self.completed_column = self.create_column("已完成", "completed")
        columns_layout.addWidget(self.completed_column)
        
        layout.addLayout(columns_layout)
        self.setLayout(layout)
    
    def create_column(self, title: str, status: str):
        """创建看板列"""
        column = QWidget()
        layout = QVBoxLayout()
        
        # 列标题
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: 600; font-size: 16px; padding: 10px;")
        layout.addWidget(title_label)
        
        # 任务列表
        task_list = JYQListWidget() if JYQListWidget != QListWidget else QListWidget()
        task_list.setDragDropMode(QListWidget.InternalMove)
        layout.addWidget(task_list)
        
        column.setLayout(layout)
        column.status = status
        column.task_list = task_list
        
        return column
    
    def load_tasks(self):
        """加载任务"""
        if not self.database:
            return
        
        tasks = self.database.get_all_tasks()
        
        # 按状态分组
        for task in tasks:
            status = task.get('status', 'pending')
            
            if status == 'pending':
                self.add_task_to_column(self.todo_column, task)
            elif status == 'in_progress':
                self.add_task_to_column(self.in_progress_column, task)
            elif status == 'completed':
                self.add_task_to_column(self.completed_column, task)
    
    def add_task_to_column(self, column, task):
        """添加任务到列"""
        item = QListWidgetItem(task.get('title', '无标题'))
        item.setData(Qt.UserRole, task)
        column.task_list.addItem(item)


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    view = KanbanView()
    view.show()
    
    sys.exit(app.exec_())

