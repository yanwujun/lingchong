#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
便签分类管理模块
Note Category Manager Module - 管理便签分类
"""

import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QTreeWidget, QTreeWidgetItem, QLabel,
                             QColorDialog, QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

try:
    from src.jingyeqian_ui import (JYQButton, JYQInput, JYQCard, JYQ_COLORS)
except ImportError:
    try:
        from jingyeqian_ui import (JYQButton, JYQInput, JYQCard, JYQ_COLORS)
    except ImportError:
        JYQButton = QPushButton
        JYQInput = QLineEdit
        JYQCard = QDialog
        JYQ_COLORS = {'primary': '#007AFF'}


class NoteCategoryManager(QDialog):
    """便签分类管理器"""
    
    # 信号
    category_changed = pyqtSignal()
    
    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.database = database
        self.init_ui()
        self.load_categories()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("便签分类管理")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # 分类树
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabel("分类")
        self.category_tree.itemDoubleClicked.connect(self.edit_category)
        layout.addWidget(self.category_tree)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        add_btn = JYQButton("添加分类", style="primary")
        add_btn.clicked.connect(self.add_category)
        
        edit_btn = JYQButton("编辑", style="secondary")
        edit_btn.clicked.connect(self.edit_selected_category)
        
        delete_btn = JYQButton("删除", style="danger")
        delete_btn.clicked.connect(self.delete_category)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        
        close_btn = JYQButton("关闭", style="secondary")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_categories(self):
        """加载分类列表"""
        self.category_tree.clear()
        
        if not self.database:
            return
        
        categories = self.database.get_all_note_categories()
        
        # 构建树形结构
        category_dict = {}
        root_items = []
        
        # 第一遍：创建所有节点
        for cat in categories:
            item = QTreeWidgetItem()
            item.setText(0, cat['name'])
            item.setData(0, Qt.UserRole, cat['id'])
            item.setData(0, Qt.UserRole + 1, cat)  # 存储完整数据
            
            # 设置颜色
            if 'color' in cat and cat['color']:
                color = QColor(cat['color'])
                item.setForeground(0, color)
            
            category_dict[cat['id']] = item
            
            if cat['parent_id'] is None:
                root_items.append(item)
        
        # 第二遍：建立父子关系
        for cat in categories:
            if cat['parent_id']:
                parent_item = category_dict.get(cat['parent_id'])
                child_item = category_dict.get(cat['id'])
                if parent_item and child_item:
                    parent_item.addChild(child_item)
        
        # 添加根节点
        for item in root_items:
            self.category_tree.addTopLevelItem(item)
        
        self.category_tree.expandAll()
    
    def add_category(self):
        """添加分类"""
        name, ok = QInputDialog.getText(self, "添加分类", "分类名称:")
        if not ok or not name.strip():
            return
        
        color = QColorDialog.getColor(QColor(JYQ_COLORS.get('primary', '#007AFF')), self)
        if not color.isValid():
            return
        
        if self.database:
            category_id = self.database.add_note_category(
                name=name.strip(),
                color=color.name()
            )
            
            if category_id > 0:
                self.load_categories()
                self.category_changed.emit()
                QMessageBox.information(self, "成功", "分类添加成功！")
    
    def edit_selected_category(self):
        """编辑选中的分类"""
        current_item = self.category_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要编辑的分类！")
            return
        
        self.edit_category(current_item)
    
    def edit_category(self, item):
        """编辑分类"""
        if not item:
            return
        
        cat_data = item.data(0, Qt.UserRole + 1)
        if not cat_data:
            return
        
        # 编辑名称
        new_name, ok = QInputDialog.getText(
            self, "编辑分类", "分类名称:", 
            text=cat_data['name']
        )
        if not ok or not new_name.strip():
            return
        
        # 选择颜色
        current_color = QColor(cat_data.get('color', JYQ_COLORS.get('primary', '#007AFF')))
        color = QColorDialog.getColor(current_color, self)
        if not color.isValid():
            return
        
        # 更新数据库（需要实现update_note_category方法）
        # 这里简化处理，实际需要添加更新方法
        QMessageBox.information(self, "提示", "分类编辑功能需要数据库支持")
    
    def delete_category(self):
        """删除分类"""
        current_item = self.category_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要删除的分类！")
            return
        
        cat_id = current_item.data(0, Qt.UserRole)
        cat_name = current_item.text(0)
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除分类 '{cat_name}' 吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.database:
                if self.database.delete_note_category(cat_id):
                    self.load_categories()
                    self.category_changed.emit()
                    QMessageBox.information(self, "成功", "分类删除成功！")


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    manager = NoteCategoryManager()
    manager.show()
    
    sys.exit(app.exec_())

