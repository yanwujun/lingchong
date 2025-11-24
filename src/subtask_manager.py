#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
子任务管理模块
Subtask Manager Module - 管理任务的子任务
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QLineEdit, QCheckBox,
                             QDialog, QFormLayout, QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

try:
    from src.jingyeqian_ui import (JYQButton, JYQInput, JYQListWidget, JYQ_COLORS)
except ImportError:
    try:
        from jingyeqian_ui import (JYQButton, JYQInput, JYQListWidget, JYQ_COLORS)
    except ImportError:
        JYQButton = QPushButton
        JYQInput = QLineEdit
        JYQListWidget = QListWidget
        JYQ_COLORS = {'primary': '#007AFF'}


class SubtaskItemWidget(QWidget):
    """子任务项组件"""
    
    def __init__(self, subtask_data, parent=None):
        super().__init__(parent)
        self.subtask_data = subtask_data
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        
        # 完成复选框
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.subtask_data.get('status') == 'completed')
        self.checkbox.stateChanged.connect(self.on_status_changed)
        layout.addWidget(self.checkbox)
        
        # 标题
        title_label = QLabel(self.subtask_data.get('title', '无标题'))
        if self.subtask_data.get('status') == 'completed':
            title_label.setStyleSheet("text-decoration: line-through; color: #8E8E93;")
        layout.addWidget(title_label, 1)
        
        self.setLayout(layout)
    
    def on_status_changed(self, state):
        """状态改变"""
        # 信号会由父组件处理
        pass


class SubtaskManager(QWidget):
    """子任务管理器"""
    
    # 信号
    subtask_changed = pyqtSignal()
    
    def __init__(self, task_id, database=None, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.database = database
        self.init_ui()
        self.load_subtasks()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        add_btn = JYQButton("➕ 添加子任务", style="primary")
        add_btn.clicked.connect(self.add_subtask)
        
        toolbar.addWidget(add_btn)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # 子任务列表
        self.subtask_list = JYQListWidget() if JYQListWidget != QListWidget else QListWidget()
        self.subtask_list.itemDoubleClicked.connect(self.edit_subtask)
        self.subtask_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.subtask_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.subtask_list)
        
        # 进度显示
        self.progress_label = QLabel("进度: 0/0 (0%)")
        layout.addWidget(self.progress_label)
        
        self.setLayout(layout)
    
    def load_subtasks(self):
        """加载子任务列表"""
        self.subtask_list.clear()
        
        if not self.database:
            return
        
        subtasks = self.database.get_subtasks(self.task_id)
        
        for subtask in subtasks:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, subtask)
            
            widget = SubtaskItemWidget(subtask)
            widget.checkbox.stateChanged.connect(
                lambda state, sid=subtask['id']: self.toggle_subtask_status(sid, state == Qt.Checked)
            )
            
            item.setSizeHint(widget.sizeHint())
            self.subtask_list.addItem(item)
            self.subtask_list.setItemWidget(item, widget)
        
        self.update_progress()
    
    def add_subtask(self):
        """添加子任务"""
        title, ok = QInputDialog.getText(self, "添加子任务", "子任务标题:")
        if not ok or not title.strip():
            return
        
        if self.database:
            subtask_id = self.database.add_subtask(
                task_id=self.task_id,
                title=title.strip()
            )
            
            if subtask_id > 0:
                self.load_subtasks()
                self.subtask_changed.emit()
    
    def edit_subtask(self, item):
        """编辑子任务"""
        subtask_data = item.data(Qt.UserRole)
        if not subtask_data:
            return
        
        title, ok = QInputDialog.getText(
            self, "编辑子任务", "子任务标题:",
            text=subtask_data.get('title', '')
        )
        
        if ok and title.strip():
            if self.database:
                self.database.update_subtask(
                    subtask_data['id'],
                    title=title.strip()
                )
                self.load_subtasks()
                self.subtask_changed.emit()
    
    def toggle_subtask_status(self, subtask_id, completed):
        """切换子任务状态"""
        if not self.database:
            return
        
        status = 'completed' if completed else 'pending'
        self.database.update_subtask(subtask_id, status=status)
        self.load_subtasks()
        self.subtask_changed.emit()
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.subtask_list.itemAt(position)
        if not item:
            return
        
        subtask_data = item.data(Qt.UserRole)
        if not subtask_data:
            return
        
        from PyQt5.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        edit_action = menu.addAction("编辑")
        edit_action.triggered.connect(lambda: self.edit_subtask(item))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(
            lambda: self.delete_subtask(subtask_data['id'])
        )
        
        menu.exec_(self.subtask_list.mapToGlobal(position))
    
    def delete_subtask(self, subtask_id):
        """删除子任务"""
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这个子任务吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.database:
                if self.database.delete_subtask(subtask_id):
                    self.load_subtasks()
                    self.subtask_changed.emit()
    
    def update_progress(self):
        """更新进度显示"""
        if not self.database:
            return
        
        subtasks = self.database.get_subtasks(self.task_id)
        total = len(subtasks)
        completed = sum(1 for s in subtasks if s.get('status') == 'completed')
        
        if total > 0:
            percentage = int(completed / total * 100)
            self.progress_label.setText(f"进度: {completed}/{total} ({percentage}%)")
        else:
            self.progress_label.setText("进度: 0/0 (0%)")
    
    def get_progress(self) -> tuple[int, int]:
        """获取进度（完成数，总数）"""
        if not self.database:
            return 0, 0
        
        subtasks = self.database.get_subtasks(self.task_id)
        total = len(subtasks)
        completed = sum(1 for s in subtasks if s.get('status') == 'completed')
        return completed, total


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    manager = SubtaskManager(task_id=1)
    manager.show()
    
    sys.exit(app.exec_())

