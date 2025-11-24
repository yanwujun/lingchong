#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
任务模板管理模块
Task Template Manager Module - 管理任务模板
"""

import sys
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QDialog, QFormLayout,
                             QLineEdit, QTextEdit, QComboBox, QMessageBox,
                             QInputDialog, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal

try:
    from src.jingyeqian_ui import (JYQButton, JYQInput, JYQTextEdit, 
                                   JYQComboBox, JYQListWidget, JYQ_COLORS)
except ImportError:
    try:
        from jingyeqian_ui import (JYQButton, JYQInput, JYQTextEdit, 
                                   JYQComboBox, JYQListWidget, JYQ_COLORS)
    except ImportError:
        JYQButton = QPushButton
        JYQInput = QLineEdit
        JYQTextEdit = QTextEdit
        JYQComboBox = QComboBox
        JYQListWidget = QListWidget
        JYQ_COLORS = {'primary': '#007AFF'}


class TemplateDialog(QDialog):
    """模板编辑对话框"""
    
    def __init__(self, parent=None, template_data=None, database=None):
        super().__init__(parent)
        self.template_data = template_data or {}
        self.database = database
        self.init_ui()
        self.load_template_data()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("编辑模板" if self.template_data else "新建模板")
        self.setMinimumSize(500, 400)
        
        layout = QFormLayout()
        
        # 模板名称
        self.name_edit = JYQInput("输入模板名称...")
        layout.addRow("模板名称*:", self.name_edit)
        
        # 任务标题
        self.title_edit = JYQInput("输入任务标题模板...")
        layout.addRow("任务标题*:", self.title_edit)
        
        # 任务描述
        self.desc_edit = JYQTextEdit()
        self.desc_edit.setPlaceholderText("输入任务描述模板...")
        self.desc_edit.setMaximumHeight(100)
        layout.addRow("任务描述:", self.desc_edit)
        
        # 分类
        self.category_combo = JYQComboBox() if JYQComboBox != QComboBox else QComboBox()
        self.category_combo.addItems(["一般", "工作", "学习", "生活", "其他"])
        self.category_combo.setEditable(True)
        layout.addRow("分类:", self.category_combo)
        
        # 优先级
        self.priority_combo = JYQComboBox()
        self.priority_combo.addItems(["低", "中", "高"])
        layout.addRow("优先级:", self.priority_combo)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = JYQButton("保存", style="primary")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = JYQButton("取消", style="secondary")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow("", button_layout)
        
        self.setLayout(layout)
    
    def load_template_data(self):
        """加载模板数据"""
        if self.template_data:
            if 'name' in self.template_data:
                self.name_edit.setText(self.template_data['name'])
            if 'title' in self.template_data:
                self.title_edit.setText(self.template_data['title'])
            if 'description' in self.template_data:
                self.desc_edit.setPlainText(self.template_data['description'])
            if 'category' in self.template_data:
                index = self.category_combo.findText(self.template_data['category'])
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
            if 'priority' in self.template_data:
                self.priority_combo.setCurrentIndex(self.template_data['priority'] - 1)
    
    def get_template_data(self) -> dict:
        """获取模板数据"""
        return {
            'name': self.name_edit.text(),
            'title': self.title_edit.text(),
            'description': self.desc_edit.toPlainText(),
            'category': self.category_combo.currentText(),
            'priority': self.priority_combo.currentIndex() + 1,
        }


class TaskTemplateManager(QWidget):
    """任务模板管理器"""
    
    # 信号
    template_selected = pyqtSignal(dict)
    
    def __init__(self, database=None, parent=None):
        super().__init__(parent)
        self.database = database
        self.init_ui()
        self.load_templates()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        new_btn = JYQButton("➕ 新建模板", style="primary")
        new_btn.clicked.connect(self.new_template)
        
        edit_btn = JYQButton("✏️ 编辑", style="secondary")
        edit_btn.clicked.connect(self.edit_template)
        
        delete_btn = JYQButton("🗑️ 删除", style="danger")
        delete_btn.clicked.connect(self.delete_template)
        
        use_btn = JYQButton("使用模板", style="primary")
        use_btn.clicked.connect(self.use_template)
        
        toolbar.addWidget(new_btn)
        toolbar.addWidget(edit_btn)
        toolbar.addWidget(delete_btn)
        toolbar.addStretch()
        toolbar.addWidget(use_btn)
        
        layout.addLayout(toolbar)
        
        # 模板列表
        self.template_list = JYQListWidget() if JYQListWidget != QListWidget else QListWidget()
        self.template_list.itemDoubleClicked.connect(self.use_template)
        layout.addWidget(self.template_list)
        
        # 使用次数显示
        self.usage_label = QLabel("")
        layout.addWidget(self.usage_label)
        
        self.setLayout(layout)
    
    def load_templates(self):
        """加载模板列表"""
        self.template_list.clear()
        
        if not self.database:
            return
        
        templates = self.database.get_all_task_templates()
        
        for template in templates:
            item = QListWidgetItem()
            usage_count = template.get('usage_count', 0)
            item.setText(f"{template['name']} (使用{usage_count}次)")
            item.setData(Qt.UserRole, template)
            self.template_list.addItem(item)
    
    def new_template(self):
        """新建模板"""
        dialog = TemplateDialog(self, database=self.database)
        if dialog.exec_() == QDialog.Accepted:
            template_data = dialog.get_template_data()
            
            if not template_data['name'].strip():
                QMessageBox.warning(self, "警告", "模板名称不能为空！")
                return
            
            if self.database:
                template_id = self.database.add_task_template(**template_data)
                if template_id > 0:
                    self.load_templates()
                    QMessageBox.information(self, "成功", "模板创建成功！")
    
    def edit_template(self):
        """编辑模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要编辑的模板！")
            return
        
        template_data = current_item.data(Qt.UserRole)
        dialog = TemplateDialog(self, template_data=template_data, database=self.database)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_template_data()
            # 更新模板（需要实现update_task_template方法）
            QMessageBox.information(self, "提示", "模板更新功能需要数据库支持")
            self.load_templates()
    
    def delete_template(self):
        """删除模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要删除的模板！")
            return
        
        template_data = current_item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除模板 '{template_data['name']}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.database:
                if self.database.delete_task_template(template_data['id']):
                    self.load_templates()
                    QMessageBox.information(self, "成功", "模板删除成功！")
    
    def use_template(self):
        """使用模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要使用的模板！")
            return
        
        template_data = current_item.data(Qt.UserRole)
        
        # 更新使用次数
        if self.database:
            self.database.update_task_template_usage(template_data['id'])
        
        # 发送信号
        self.template_selected.emit(template_data)
        self.load_templates()


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    manager = TaskTemplateManager()
    manager.show()
    
    sys.exit(app.exec_())

