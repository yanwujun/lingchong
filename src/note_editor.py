#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
便签编辑器模块
Note Editor Module - 富文本编辑、格式化等功能
"""

import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QTextEdit, QColorDialog, QFontComboBox,
                             QSpinBox, QLabel, QToolBar, QAction, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextCharFormat, QTextCursor, QColor, QIcon, QFont

try:
    from src.jingyeqian_ui import (JYQButton, JYQInput, JYQTextEdit, 
                                   JYQComboBox, JYQCard, JYQ_COLORS)
except ImportError:
    try:
        from jingyeqian_ui import (JYQButton, JYQInput, JYQTextEdit, 
                                   JYQComboBox, JYQCard, JYQ_COLORS)
    except ImportError:
        # 回退到标准组件
        JYQButton = QPushButton
        JYQInput = QLineEdit
        JYQTextEdit = QTextEdit
        JYQComboBox = QComboBox
        JYQCard = QDialog
        JYQ_COLORS = {'primary': '#007AFF', 'surface': '#FFFFFF', 
                     'text_primary': '#000000'}


class NoteEditor(QDialog):
    """便签编辑器对话框"""
    
    # 信号
    note_saved = pyqtSignal(dict)
    
    def __init__(self, parent=None, note_data=None, database=None):
        super().__init__(parent)
        self.note_data = note_data or {}
        self.database = database
        self.init_ui()
        self.load_note_data()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("编辑便签" if self.note_data else "新建便签")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # 标题输入
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("标题:"))
        self.title_edit = JYQInput("输入便签标题...")
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)
        
        # 富文本编辑器
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("输入便签内容...")
        self.content_edit.setAcceptRichText(True)
        layout.addWidget(self.content_edit)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = JYQButton("保存", style="primary")
        self.save_btn.clicked.connect(self.save_note)
        
        cancel_btn = JYQButton("取消", style="secondary")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_toolbar(self):
        """创建格式化工具栏"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # 粗体
        bold_action = QAction("B", self)
        bold_action.setCheckable(True)
        bold_action.triggered.connect(self.toggle_bold)
        toolbar.addAction(bold_action)
        
        # 斜体
        italic_action = QAction("I", self)
        italic_action.setCheckable(True)
        italic_action.triggered.connect(self.toggle_italic)
        toolbar.addAction(italic_action)
        
        # 下划线
        underline_action = QAction("U", self)
        underline_action.setCheckable(True)
        underline_action.triggered.connect(self.toggle_underline)
        toolbar.addAction(underline_action)
        
        toolbar.addSeparator()
        
        # 字体颜色
        color_action = QAction("颜色", self)
        color_action.triggered.connect(self.change_text_color)
        toolbar.addAction(color_action)
        
        # 字体大小
        toolbar.addWidget(QLabel("字号:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self.change_font_size)
        toolbar.addWidget(self.font_size_spin)
        
        toolbar.addSeparator()
        
        # 对齐方式
        align_left_action = QAction("左对齐", self)
        align_left_action.triggered.connect(lambda: self.set_alignment(Qt.AlignLeft))
        toolbar.addAction(align_left_action)
        
        align_center_action = QAction("居中", self)
        align_center_action.triggered.connect(lambda: self.set_alignment(Qt.AlignCenter))
        toolbar.addAction(align_center_action)
        
        align_right_action = QAction("右对齐", self)
        align_right_action.triggered.connect(lambda: self.set_alignment(Qt.AlignRight))
        toolbar.addAction(align_right_action)
        
        return toolbar
    
    def toggle_bold(self):
        """切换粗体"""
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if not self.content_edit.fontWeight() else QFont.Normal)
        self.merge_format(fmt)
    
    def toggle_italic(self):
        """切换斜体"""
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.content_edit.fontItalic())
        self.merge_format(fmt)
    
    def toggle_underline(self):
        """切换下划线"""
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.content_edit.fontUnderline())
        self.merge_format(fmt)
    
    def change_text_color(self):
        """改变文字颜色"""
        color = QColorDialog.getColor(self.content_edit.textColor(), self)
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self.merge_format(fmt)
    
    def change_font_size(self, size):
        """改变字体大小"""
        fmt = QTextCharFormat()
        fmt.setFontPointSize(size)
        self.merge_format(fmt)
    
    def set_alignment(self, alignment):
        """设置对齐方式"""
        self.content_edit.setAlignment(alignment)
    
    def merge_format(self, format):
        """合并格式"""
        cursor = self.content_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.content_edit.mergeCurrentCharFormat(format)
    
    def load_note_data(self):
        """加载便签数据"""
        if self.note_data:
            if 'title' in self.note_data:
                self.title_edit.setText(self.note_data['title'])
            if 'content' in self.note_data:
                self.content_edit.setHtml(self.note_data['content'])
    
    def get_note_data(self) -> dict:
        """获取便签数据"""
        return {
            'title': self.title_edit.text(),
            'content': self.content_edit.toHtml(),
        }
    
    def save_note(self):
        """保存便签"""
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "警告", "便签标题不能为空！")
            return
        
        note_data = self.get_note_data()
        note_data['id'] = self.note_data.get('id')
        
        self.note_saved.emit(note_data)
        self.accept()


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    editor = NoteEditor()
    editor.show()
    
    sys.exit(app.exec_())

