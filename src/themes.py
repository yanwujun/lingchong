#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主题模块
Themes Module - 定义浅色和暗色主题样式
"""

# 浅色主题（默认）
LIGHT_THEME = {
    'todo_window': """
        QWidget {
            background-color: #f5f5f5;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QTableWidget {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            color: #333;
        }
        QHeaderView::section {
            background-color: #e0e0e0;
            padding: 8px;
            border: none;
            font-weight: bold;
            color: #333;
        }
        QLineEdit {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            color: #333;
        }
        QComboBox {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            color: #333;
        }
    """,
    
    'settings_window': """
        QWidget {
            background-color: #f5f5f5;
            font-size: 13px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QGroupBox {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
            color: #333;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
    """,
    
    'reminder_popup': """
        QWidget {
            background-color: white;
            border: 2px solid #ff5722;
            border-radius: 10px;
        }
        QLabel {
            color: #333;
        }
    """
}

# 暗色主题
DARK_THEME = {
    'todo_window': """
        QWidget {
            background-color: #2b2b2b;
            color: #e0e0e0;
        }
        QPushButton {
            background-color: #5a9e5e;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #4a8e4e;
        }
        QTableWidget {
            background-color: #1e1e1e;
            border: 1px solid #444;
            border-radius: 4px;
            color: #e0e0e0;
            gridline-color: #444;
        }
        QHeaderView::section {
            background-color: #3d3d3d;
            padding: 8px;
            border: none;
            font-weight: bold;
            color: #e0e0e0;
        }
        QLineEdit {
            background-color: #3d3d3d;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 5px;
            color: #e0e0e0;
        }
        QComboBox {
            background-color: #3d3d3d;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 5px;
            color: #e0e0e0;
        }
        QComboBox:drop-down {
            border: none;
        }
        QComboBox QAbstractItemView {
            background-color: #3d3d3d;
            color: #e0e0e0;
            selection-background-color: #5a9e5e;
        }
    """,
    
    'settings_window': """
        QWidget {
            background-color: #2b2b2b;
            font-size: 13px;
            color: #e0e0e0;
        }
        QPushButton {
            background-color: #5a9e5e;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #4a8e4e;
        }
        QGroupBox {
            background-color: #1e1e1e;
            border: 1px solid #444;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
            color: #e0e0e0;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QCheckBox {
            color: #e0e0e0;
        }
        QLabel {
            color: #e0e0e0;
        }
        QTabWidget::pane {
            border: 1px solid #444;
            background-color: #2b2b2b;
        }
        QTabBar::tab {
            background-color: #3d3d3d;
            color: #e0e0e0;
            padding: 8px 16px;
            border: 1px solid #444;
        }
        QTabBar::tab:selected {
            background-color: #5a9e5e;
        }
    """,
    
    'reminder_popup': """
        QWidget {
            background-color: #2b2b2b;
            border: 2px solid #ff5722;
            border-radius: 10px;
        }
        QLabel {
            color: #e0e0e0;
        }
    """
}


def get_theme(theme_name='light'):
    """
    获取主题样式
    
    Args:
        theme_name: 主题名称（'light' 或 'dark'）
    
    Returns:
        主题样式字典
    """
    if theme_name == 'dark':
        return DARK_THEME
    return LIGHT_THEME


def apply_theme_to_widget(widget, widget_type, theme_name='light'):
    """
    应用主题到控件
    
    Args:
        widget: Qt控件
        widget_type: 控件类型（'todo_window'/'settings_window'/'reminder_popup'）
        theme_name: 主题名称（'light'/'dark'）
    """
    theme = get_theme(theme_name)
    if widget_type in theme:
        widget.setStyleSheet(theme[widget_type])
        print(f"[主题] 应用 {theme_name} 主题到 {widget_type}")

