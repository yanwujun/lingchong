#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
命令面板模块
Command Palette Module - 类似VS Code的命令面板
"""

import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QListWidget,
                             QListWidgetItem, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence

try:
    from src.jingyeqian_ui import (JYQInput, JYQListWidget, JYQ_COLORS)
except ImportError:
    try:
        from jingyeqian_ui import (JYQInput, JYQListWidget, JYQ_COLORS)
    except ImportError:
        JYQInput = QLineEdit
        JYQListWidget = QListWidget
        JYQ_COLORS = {'primary': '#007AFF'}


class CommandPalette(QDialog):
    """命令面板"""
    
    # 信号
    command_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.commands = []
        self.filtered_commands = []
        self.init_ui()
        self.load_commands()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("命令面板")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 搜索框
        self.search_input = JYQInput("输入命令...")
        self.search_input.textChanged.connect(self.filter_commands)
        self.search_input.returnPressed.connect(self.execute_selected)
        layout.addWidget(self.search_input)
        
        # 命令列表
        self.command_list = JYQListWidget() if JYQListWidget != QListWidget else QListWidget()
        self.command_list.itemDoubleClicked.connect(self.execute_command)
        self.command_list.currentRowChanged.connect(self.on_selection_changed)
        layout.addWidget(self.command_list)
        
        # 提示
        self.hint_label = QLabel("使用 ↑↓ 选择，Enter 执行，Esc 关闭")
        self.hint_label.setStyleSheet("color: #8E8E93; font-size: 11px;")
        layout.addWidget(self.hint_label)
        
        self.setLayout(layout)
        
        # 设置样式
        self.setStyleSheet(f"""
            CommandPalette {{
                background-color: {JYQ_COLORS.get('surface', '#FFFFFF')};
                border: 1px solid {JYQ_COLORS.get('border', '#C6C6C8')};
                border-radius: 12px;
            }}
        """)
    
    def load_commands(self):
        """加载命令列表"""
        self.commands = [
            {'id': 'new_task', 'name': '新建任务', 'category': '任务', 'shortcut': 'Ctrl+N'},
            {'id': 'new_note', 'name': '新建便签', 'category': '便签', 'shortcut': 'Ctrl+Shift+N'},
            {'id': 'open_todo', 'name': '打开待办窗口', 'category': '窗口', 'shortcut': 'Ctrl+T'},
            {'id': 'open_notes', 'name': '打开便签窗口', 'category': '窗口', 'shortcut': 'Ctrl+Shift+T'},
            {'id': 'open_pomodoro', 'name': '打开番茄钟', 'category': '工具', 'shortcut': ''},
            {'id': 'open_settings', 'name': '打开设置', 'category': '设置', 'shortcut': 'Ctrl+,,'},
            {'id': 'export_data', 'name': '导出数据', 'category': '数据', 'shortcut': ''},
            {'id': 'import_data', 'name': '导入数据', 'category': '数据', 'shortcut': ''},
            {'id': 'show_statistics', 'name': '显示统计', 'category': '数据', 'shortcut': ''},
        ]
        
        self.filtered_commands = self.commands
        self.update_command_list()
    
    def filter_commands(self, keyword: str):
        """过滤命令"""
        if not keyword.strip():
            self.filtered_commands = self.commands
        else:
            keyword_lower = keyword.lower()
            self.filtered_commands = [
                cmd for cmd in self.commands
                if keyword_lower in cmd['name'].lower() or 
                   keyword_lower in cmd['category'].lower()
            ]
        
        self.update_command_list()
    
    def update_command_list(self):
        """更新命令列表"""
        self.command_list.clear()
        
        current_category = None
        for cmd in self.filtered_commands:
            # 添加分类标题
            if cmd['category'] != current_category:
                current_category = cmd['category']
                category_item = QListWidgetItem(f"--- {current_category} ---")
                category_item.setFlags(Qt.NoItemFlags)
                category_item.setForeground(Qt.gray)
                self.command_list.addItem(category_item)
            
            # 添加命令
            item = QListWidgetItem(cmd['name'])
            item.setData(Qt.UserRole, cmd['id'])
            
            # 显示快捷键
            if cmd['shortcut']:
                item.setText(f"{cmd['name']}  ({cmd['shortcut']})")
            
            self.command_list.addItem(item)
        
        # 选中第一项
        if self.command_list.count() > 0:
            first_item = self.command_list.item(0)
            if first_item.flags() & Qt.ItemIsSelectable:
                self.command_list.setCurrentRow(0)
    
    def execute_selected(self):
        """执行选中的命令"""
        current_item = self.command_list.currentItem()
        if current_item and current_item.data(Qt.UserRole):
            command_id = current_item.data(Qt.UserRole)
            self.command_selected.emit(command_id)
            self.accept()
    
    def execute_command(self, item):
        """执行命令"""
        if item.data(Qt.UserRole):
            command_id = item.data(Qt.UserRole)
            self.command_selected.emit(command_id)
            self.accept()
    
    def on_selection_changed(self, row):
        """选择改变"""
        pass
    
    def keyPressEvent(self, event):
        """按键事件"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.execute_selected()
        else:
            super().keyPressEvent(event)
    
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        self.search_input.setFocus()
        self.search_input.selectAll()


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    palette = CommandPalette()
    palette.command_selected.connect(lambda cmd: print(f"执行命令: {cmd}"))
    palette.show()
    
    sys.exit(app.exec_())

