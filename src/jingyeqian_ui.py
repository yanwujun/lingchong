#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
敬业签UI组件库
Jingyeqian UI Module - 提供扁平化现代化界面组件
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

# 扁平化设计颜色方案
JYQ_COLORS = {
    # 主色调
    'primary': '#007AFF',           # 蓝色
    'primary_dark': '#0051D5',      # 深蓝
    'primary_light': '#5AC8FA',     # 浅蓝
    
    # 背景色
    'background': '#F2F2F7',        # 浅灰背景
    'surface': '#FFFFFF',            # 白色表面
    'surface_dark': '#1C1C1E',      # 深色表面
    
    # 文本色
    'text_primary': '#000000',      # 主文本（黑色）
    'text_secondary': '#8E8E93',    # 次要文本（灰色）
    'text_tertiary': '#C7C7CC',     # 三级文本（浅灰）
    
    # 语义色
    'success': '#34C759',           # 成功（绿色）
    'warning': '#FF9500',           # 警告（橙色）
    'error': '#FF3B30',             # 错误（红色）
    'info': '#007AFF',              # 信息（蓝色）
    
    # 边框和分割线
    'border': '#C6C6C8',            # 边框色
    'divider': '#E5E5EA',           # 分割线
    
    # 阴影
    'shadow': 'rgba(0, 0, 0, 0.1)', # 阴影
}

class JYQCard(QFrame):
    """扁平化卡片组件"""
    
    def __init__(self, parent=None, elevation=0):
        super().__init__(parent)
        self.elevation = elevation
        self.setFrameStyle(QFrame.NoFrame)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.update_style()
    
    def update_style(self):
        """更新样式"""
        shadow = ""
        if self.elevation > 0:
            shadow = f"box-shadow: 0 {self.elevation}px {self.elevation * 2}px {JYQ_COLORS['shadow']};"
        
        self.setStyleSheet(f"""
            JYQCard {{
                background-color: {JYQ_COLORS['surface']};
                border-radius: 12px;
                border: 1px solid {JYQ_COLORS['border']};
                padding: 16px;
                {shadow}
            }}
        """)

class JYQButton(QPushButton):
    """扁平化按钮组件"""
    
    def __init__(self, text="", parent=None, style="primary", size="medium"):
        super().__init__(text, parent)
        self.style_type = style
        self.size_type = size
        self.setCursor(Qt.PointingHandCursor)
        self.update_style()
    
    def update_style(self):
        """更新样式"""
        # 根据样式选择颜色
        if self.style_type == "primary":
            bg_color = JYQ_COLORS['primary']
            text_color = "#FFFFFF"
            hover_color = JYQ_COLORS['primary_dark']
        elif self.style_type == "secondary":
            bg_color = JYQ_COLORS['surface']
            text_color = JYQ_COLORS['primary']
            hover_color = JYQ_COLORS['background']
        elif self.style_type == "danger":
            bg_color = JYQ_COLORS['error']
            text_color = "#FFFFFF"
            hover_color = "#D70015"
        else:
            bg_color = JYQ_COLORS['surface']
            text_color = JYQ_COLORS['text_primary']
            hover_color = JYQ_COLORS['background']
        
        # 根据尺寸选择大小
        if self.size_type == "small":
            padding = "6px 12px"
            font_size = "13px"
        elif self.size_type == "large":
            padding = "12px 24px"
            font_size = "17px"
        else:  # medium
            padding = "10px 20px"
            font_size = "15px"
        
        self.setStyleSheet(f"""
            JYQButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 8px;
                padding: {padding};
                font-size: {font_size};
                font-weight: 500;
            }}
            JYQButton:hover {{
                background-color: {hover_color};
            }}
            JYQButton:pressed {{
                opacity: 0.8;
            }}
            JYQButton:disabled {{
                background-color: {JYQ_COLORS['divider']};
                color: {JYQ_COLORS['text_tertiary']};
            }}
        """)

class JYQInput(QLineEdit):
    """扁平化输入框组件"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.update_style()
    
    def update_style(self):
        """更新样式"""
        self.setStyleSheet(f"""
            JYQInput {{
                background-color: {JYQ_COLORS['surface']};
                border: 1px solid {JYQ_COLORS['border']};
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 15px;
                color: {JYQ_COLORS['text_primary']};
            }}
            JYQInput:focus {{
                border: 2px solid {JYQ_COLORS['primary']};
                padding: 9px 11px;
            }}
            JYQInput::placeholder {{
                color: {JYQ_COLORS['text_tertiary']};
            }}
        """)

class JYQTextEdit(QTextEdit):
    """扁平化文本编辑框组件"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.update_style()
    
    def update_style(self):
        """更新样式"""
        self.setStyleSheet(f"""
            JYQTextEdit {{
                background-color: {JYQ_COLORS['surface']};
                border: 1px solid {JYQ_COLORS['border']};
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 15px;
                color: {JYQ_COLORS['text_primary']};
            }}
            JYQTextEdit:focus {{
                border: 2px solid {JYQ_COLORS['primary']};
                padding: 9px 11px;
            }}
        """)

class JYQComboBox(QComboBox):
    """扁平化下拉框组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_style()
    
    def update_style(self):
        """更新样式"""
        self.setStyleSheet(f"""
            JYQComboBox {{
                background-color: {JYQ_COLORS['surface']};
                border: 1px solid {JYQ_COLORS['border']};
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 15px;
                color: {JYQ_COLORS['text_primary']};
            }}
            JYQComboBox:focus {{
                border: 2px solid {JYQ_COLORS['primary']};
                padding: 9px 11px;
            }}
            JYQComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            JYQComboBox QAbstractItemView {{
                background-color: {JYQ_COLORS['surface']};
                border: 1px solid {JYQ_COLORS['border']};
                border-radius: 8px;
                selection-background-color: {JYQ_COLORS['primary']};
                selection-color: #FFFFFF;
            }}
        """)

class JYQListWidget(QListWidget):
    """扁平化列表组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_style()
    
    def update_style(self):
        """更新样式"""
        self.setStyleSheet(f"""
            JYQListWidget {{
                background-color: {JYQ_COLORS['surface']};
                border: 1px solid {JYQ_COLORS['border']};
                border-radius: 8px;
                padding: 4px;
            }}
            JYQListWidget::item {{
                border-radius: 6px;
                padding: 8px;
                margin: 2px;
            }}
            JYQListWidget::item:hover {{
                background-color: {JYQ_COLORS['background']};
            }}
            JYQListWidget::item:selected {{
                background-color: {JYQ_COLORS['primary']};
                color: #FFFFFF;
            }}
        """)

class JYQTableWidget(QTableWidget):
    """扁平化表格组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_style()
    
    def update_style(self):
        """更新样式"""
        self.setStyleSheet(f"""
            JYQTableWidget {{
                background-color: {JYQ_COLORS['surface']};
                border: 1px solid {JYQ_COLORS['border']};
                border-radius: 8px;
                gridline-color: {JYQ_COLORS['divider']};
            }}
            JYQTableWidget::item {{
                padding: 8px;
            }}
            JYQTableWidget::item:selected {{
                background-color: {JYQ_COLORS['primary']};
                color: #FFFFFF;
            }}
            QHeaderView::section {{
                background-color: {JYQ_COLORS['background']};
                color: {JYQ_COLORS['text_primary']};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {JYQ_COLORS['divider']};
                font-weight: 600;
            }}
        """)

class JYQBadge(QLabel):
    """徽章组件"""
    
    def __init__(self, text="", parent=None, color="primary"):
        super().__init__(text, parent)
        self.badge_color = color
        self.setAlignment(Qt.AlignCenter)
        self.update_style()
    
    def update_style(self):
        """更新样式"""
        if self.badge_color == "primary":
            bg = JYQ_COLORS['primary']
        elif self.badge_color == "success":
            bg = JYQ_COLORS['success']
        elif self.badge_color == "warning":
            bg = JYQ_COLORS['warning']
        elif self.badge_color == "error":
            bg = JYQ_COLORS['error']
        else:
            bg = JYQ_COLORS['text_secondary']
        
        self.setStyleSheet(f"""
            JYQBadge {{
                background-color: {bg};
                color: #FFFFFF;
                border-radius: 12px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)

class JYQDivider(QFrame):
    """分割线组件"""
    
    def __init__(self, parent=None, orientation=Qt.Horizontal):
        super().__init__(parent)
        if orientation == Qt.Horizontal:
            self.setFixedHeight(1)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        else:
            self.setFixedWidth(1)
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        self.setStyleSheet(f"""
            JYQDivider {{
                background-color: {JYQ_COLORS['divider']};
                border: none;
            }}
        """)

class JYQIconButton(QPushButton):
    """图标按钮组件"""
    
    def __init__(self, icon_path=None, icon_text="", parent=None, size=24):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(size + 16, size + 16)
        
        if icon_path:
            icon = QIcon(icon_path)
            self.setIcon(icon)
            self.setIconSize(QSize(size, size))
        elif icon_text:
            self.setText(icon_text)
            self.setFont(QFont("Arial", size // 2))
        
        self.update_style()
    
    def update_style(self):
        """更新样式"""
        self.setStyleSheet(f"""
            JYQIconButton {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
            }}
            JYQIconButton:hover {{
                background-color: {JYQ_COLORS['background']};
            }}
            JYQIconButton:pressed {{
                background-color: {JYQ_COLORS['divider']};
            }}
        """)

def apply_jyq_theme(widget, theme='light'):
    """应用敬业签主题到窗口"""
    if theme == 'dark':
        # 暗色主题（未来实现）
        pass
    else:
        # 亮色主题
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {JYQ_COLORS['background']};
                color: {JYQ_COLORS['text_primary']};
            }}
        """)

