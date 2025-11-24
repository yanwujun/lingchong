#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
便签窗口模块
Note Window Module - 便签主窗口，显示和管理所有便签
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QLabel, QMessageBox,
                             QMenu, QInputDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

try:
    from src.jingyeqian_ui import (JYQButton, JYQInput, JYQListWidget, 
                                   JYQCard, JYQ_COLORS, apply_jyq_theme)
    from src.note_editor import NoteEditor
    from src.note_category_manager import NoteCategoryManager
    from src.attachment_manager import AttachmentManager
except ImportError:
    try:
        from jingyeqian_ui import (JYQButton, JYQInput, JYQListWidget, 
                                   JYQCard, JYQ_COLORS, apply_jyq_theme)
        from note_editor import NoteEditor
        from note_category_manager import NoteCategoryManager
        from attachment_manager import AttachmentManager
    except ImportError:
        JYQButton = QPushButton
        JYQInput = QLineEdit
        JYQListWidget = QListWidget
        JYQCard = QWidget
        JYQ_COLORS = {'primary': '#007AFF', 'surface': '#FFFFFF'}
        NoteEditor = None
        NoteCategoryManager = None
        AttachmentManager = None
        apply_jyq_theme = None


class NoteItemWidget(QWidget):
    """便签列表项组件"""
    
    def __init__(self, note_data, parent=None):
        super().__init__(parent)
        self.note_data = note_data
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        
        # 标题
        title_label = QLabel(self.note_data.get('title', '无标题'))
        title_label.setStyleSheet("font-weight: 600; font-size: 15px;")
        layout.addWidget(title_label)
        
        # 内容预览（去除HTML标签）
        content = self.note_data.get('content', '')
        # 简单去除HTML标签
        import re
        plain_text = re.sub(r'<[^>]+>', '', content)
        if len(plain_text) > 100:
            plain_text = plain_text[:100] + "..."
        
        if plain_text.strip():
            content_label = QLabel(plain_text)
            content_label.setStyleSheet("color: #8E8E93; font-size: 13px;")
            content_label.setWordWrap(True)
            layout.addWidget(content_label)
        
        # 底部信息
        info_layout = QHBoxLayout()
        
        # 置顶标识
        if self.note_data.get('is_pinned'):
            pin_label = QLabel("📌")
            info_layout.addWidget(pin_label)
        
        # 锁定标识
        if self.note_data.get('is_locked'):
            lock_label = QLabel("🔒")
            info_layout.addWidget(lock_label)
        
        info_layout.addStretch()
        
        # 更新时间
        updated_at = self.note_data.get('updated_at', '')
        if updated_at:
            time_label = QLabel(updated_at[:10])  # 只显示日期
            time_label.setStyleSheet("color: #C7C7CC; font-size: 11px;")
            info_layout.addWidget(time_label)
        
        layout.addLayout(info_layout)
        self.setLayout(layout)
        
        # 设置背景色
        if self.note_data.get('color'):
            self.setStyleSheet(f"""
                NoteItemWidget {{
                    background-color: {self.note_data['color']};
                    border-radius: 8px;
                    padding: 4px;
                }}
            """)


class NoteWindow(QWidget):
    """便签主窗口"""
    
    def __init__(self, database=None):
        super().__init__()
        self.database = database
        self.attachment_manager = AttachmentManager(database) if AttachmentManager else None
        self.init_ui()
        self.load_notes()
        
        # 应用主题
        if apply_jyq_theme:
            apply_jyq_theme(self)
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("📝 便签")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar = self.create_toolbar()
        layout.addLayout(toolbar)
        
        # 便签列表
        self.note_list = JYQListWidget() if JYQListWidget != QListWidget else QListWidget()
        self.note_list.itemDoubleClicked.connect(self.edit_note)
        self.note_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.note_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.note_list)
        
        # 状态栏
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QHBoxLayout()
        
        # 新建便签
        new_btn = JYQButton("➕ 新建便签", style="primary")
        new_btn.clicked.connect(self.new_note)
        
        # 分类管理
        category_btn = JYQButton("📁 分类管理", style="secondary")
        category_btn.clicked.connect(self.manage_categories)
        
        # 搜索框
        self.search_input = JYQInput("🔍 搜索便签...")
        self.search_input.textChanged.connect(self.search_notes)
        
        toolbar.addWidget(new_btn)
        toolbar.addWidget(category_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.search_input)
        
        return toolbar
    
    def load_notes(self, category_id=None):
        """加载便签列表"""
        self.note_list.clear()
        
        if not self.database:
            return
        
        notes = self.database.get_all_notes(category_id=category_id)
        
        for note in notes:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, note)
            
            # 创建自定义组件
            widget = NoteItemWidget(note)
            item.setSizeHint(widget.sizeHint())
            
            self.note_list.addItem(item)
            self.note_list.setItemWidget(item, widget)
        
        self.status_label.setText(f"共 {len(notes)} 条便签")
    
    def new_note(self):
        """新建便签"""
        if not NoteEditor:
            QMessageBox.warning(self, "错误", "便签编辑器未加载")
            return
        
        editor = NoteEditor(self, database=self.database)
        editor.note_saved.connect(self.on_note_saved)
        editor.exec_()
    
    def edit_note(self, item):
        """编辑便签"""
        if not NoteEditor:
            return
        
        note_data = item.data(Qt.UserRole)
        if not note_data:
            return
        
        editor = NoteEditor(self, note_data=note_data, database=self.database)
        editor.note_saved.connect(self.on_note_saved)
        editor.exec_()
    
    def on_note_saved(self, note_data):
        """便签保存回调"""
        if not self.database:
            return
        
        if 'id' in note_data and note_data['id']:
            # 更新
            self.database.update_note(note_data['id'], **note_data)
        else:
            # 新建
            note_id = self.database.add_note(**note_data)
            if note_id > 0:
                note_data['id'] = note_id
        
        self.load_notes()
        self.status_label.setText("✅ 便签已保存")
    
    def search_notes(self, keyword):
        """搜索便签"""
        if not keyword.strip():
            self.load_notes()
            return
        
        if not self.database:
            return
        
        notes = self.database.search_notes(keyword)
        self.note_list.clear()
        
        for note in notes:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, note)
            
            widget = NoteItemWidget(note)
            item.setSizeHint(widget.sizeHint())
            
            self.note_list.addItem(item)
            self.note_list.setItemWidget(item, widget)
        
        self.status_label.setText(f"找到 {len(notes)} 条便签")
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.note_list.itemAt(position)
        if not item:
            return
        
        note_data = item.data(Qt.UserRole)
        if not note_data:
            return
        
        menu = QMenu(self)
        
        edit_action = menu.addAction("编辑")
        edit_action.triggered.connect(lambda: self.edit_note(item))
        
        menu.addSeparator()
        
        pin_action = menu.addAction("置顶" if not note_data.get('is_pinned') else "取消置顶")
        pin_action.triggered.connect(lambda: self.toggle_pin(note_data['id']))
        
        lock_action = menu.addAction("锁定" if not note_data.get('is_locked') else "解锁")
        lock_action.triggered.connect(lambda: self.toggle_lock(note_data['id']))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(lambda: self.delete_note(note_data['id']))
        
        menu.exec_(self.note_list.mapToGlobal(position))
    
    def toggle_pin(self, note_id):
        """切换置顶状态"""
        if not self.database:
            return
        
        note = self.database.get_note(note_id)
        if note:
            new_pinned = not note.get('is_pinned', False)
            self.database.update_note(note_id, is_pinned=new_pinned)
            self.load_notes()
    
    def toggle_lock(self, note_id):
        """切换锁定状态"""
        if not self.database:
            return
        
        note = self.database.get_note(note_id)
        if note:
            new_locked = not note.get('is_locked', False)
            self.database.update_note(note_id, is_locked=new_locked)
            self.load_notes()
    
    def delete_note(self, note_id):
        """删除便签"""
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这条便签吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.database:
                if self.database.delete_note(note_id):
                    self.load_notes()
                    self.status_label.setText("✅ 便签已删除")
    
    def manage_categories(self):
        """管理分类"""
        if not NoteCategoryManager:
            QMessageBox.warning(self, "错误", "分类管理器未加载")
            return
        
        manager = NoteCategoryManager(self, self.database)
        manager.category_changed.connect(self.load_notes)
        manager.exec_()
    
    def closeEvent(self, event):
        """关闭事件"""
        event.ignore()
        self.hide()


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    window = NoteWindow()
    window.show()
    
    sys.exit(app.exec_())

