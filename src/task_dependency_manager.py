#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
任务依赖管理模块
Task Dependency Manager Module - 管理任务之间的依赖关系
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QLabel, QMessageBox,
                             QComboBox, QDialog, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal

try:
    from src.jingyeqian_ui import (JYQButton, JYQComboBox, JYQListWidget, JYQ_COLORS)
except ImportError:
    try:
        from jingyeqian_ui import (JYQButton, JYQComboBox, JYQListWidget, JYQ_COLORS)
    except ImportError:
        JYQButton = QPushButton
        JYQComboBox = QComboBox
        JYQListWidget = QListWidget
        JYQ_COLORS = {'primary': '#007AFF'}


class TaskDependencyManager(QWidget):
    """任务依赖管理器"""
    
    # 信号
    dependency_changed = pyqtSignal()
    
    def __init__(self, task_id, database=None, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.database = database
        self.init_ui()
        self.load_dependencies()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 说明
        info_label = QLabel("此任务依赖以下任务完成：")
        layout.addWidget(info_label)
        
        # 依赖列表
        self.dependency_list = JYQListWidget() if JYQListWidget != QListWidget else QListWidget()
        self.dependency_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dependency_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.dependency_list)
        
        # 添加依赖
        add_layout = QHBoxLayout()
        
        add_layout.addWidget(QLabel("添加依赖:"))
        self.task_combo = JYQComboBox() if JYQComboBox != QComboBox else QComboBox()
        self.load_available_tasks()
        add_layout.addWidget(self.task_combo, 1)
        
        add_btn = JYQButton("添加", style="primary")
        add_btn.clicked.connect(self.add_dependency)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        
        self.setLayout(layout)
    
    def load_available_tasks(self):
        """加载可用的任务列表"""
        self.task_combo.clear()
        
        if not self.database:
            return
        
        # 获取所有未完成的任务（排除自己）
        all_tasks = self.database.get_all_tasks(status='pending')
        
        # 获取已有依赖的任务ID
        existing_deps = [dep['depends_on_task_id'] for dep in self.database.get_task_dependencies(self.task_id)]
        
        for task in all_tasks:
            if task['id'] != self.task_id and task['id'] not in existing_deps:
                self.task_combo.addItem(
                    f"[{task['id']}] {task['title']}",
                    task['id']
                )
    
    def load_dependencies(self):
        """加载依赖列表"""
        self.dependency_list.clear()
        
        if not self.database:
            return
        
        dependencies = self.database.get_task_dependencies(self.task_id)
        
        for dep in dependencies:
            # 获取被依赖的任务信息
            task = self.database.get_task(dep['depends_on_task_id'])
            if task:
                item = QListWidgetItem()
                status_icon = "✅" if task.get('status') == 'completed' else "⏳"
                item.setText(f"{status_icon} [{task['id']}] {task['title']}")
                item.setData(Qt.UserRole, dep)
                
                # 如果已完成，设置为灰色
                if task.get('status') == 'completed':
                    item.setForeground(Qt.gray)
                
                self.dependency_list.addItem(item)
    
    def add_dependency(self):
        """添加依赖"""
        if self.task_combo.currentIndex() < 0:
            QMessageBox.warning(self, "警告", "请选择要依赖的任务！")
            return
        
        depends_on_id = self.task_combo.currentData()
        if not depends_on_id:
            return
        
        # 检查循环依赖
        if self.database:
            if self.database.check_circular_dependency(self.task_id, depends_on_id):
                QMessageBox.warning(
                    self, "错误", 
                    "添加此依赖会形成循环依赖，无法添加！"
                )
                return
            
            if self.database.add_task_dependency(self.task_id, depends_on_id):
                self.load_dependencies()
                self.load_available_tasks()
                self.dependency_changed.emit()
                QMessageBox.information(self, "成功", "依赖添加成功！")
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.dependency_list.itemAt(position)
        if not item:
            return
        
        dep_data = item.data(Qt.UserRole)
        if not dep_data:
            return
        
        from PyQt5.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        delete_action = menu.addAction("删除依赖")
        delete_action.triggered.connect(
            lambda: self.delete_dependency(dep_data['depends_on_task_id'])
        )
        
        menu.exec_(self.dependency_list.mapToGlobal(position))
    
    def delete_dependency(self, depends_on_id):
        """删除依赖"""
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这个依赖吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.database:
                if self.database.delete_task_dependency(self.task_id, depends_on_id):
                    self.load_dependencies()
                    self.load_available_tasks()
                    self.dependency_changed.emit()
    
    def can_start(self) -> bool:
        """检查任务是否可以开始（所有依赖是否完成）"""
        if not self.database:
            return True
        
        dependencies = self.database.get_task_dependencies(self.task_id)
        
        for dep in dependencies:
            task = self.database.get_task(dep['depends_on_task_id'])
            if task and task.get('status') != 'completed':
                return False
        
        return True


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    manager = TaskDependencyManager(task_id=1)
    manager.show()
    
    sys.exit(app.exec_())

