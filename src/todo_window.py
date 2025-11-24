#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
待办事项窗口模块
Todo Window Module - 负责任务的显示和管理界面
"""

import sys
from datetime import datetime, timedelta
from collections import defaultdict
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QTableWidget, QTableWidgetItem, QLabel,
                             QDialog, QFormLayout, QTextEdit, QDateTimeEdit,
                             QComboBox, QHeaderView, QMessageBox, QApplication, QShortcut, QFrame, QScrollArea, QTabWidget,
                             QTreeWidget, QTreeWidgetItem, QCalendarWidget, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal, QDate, QMimeData
from PyQt5.QtGui import QColor, QKeySequence, QDrag, QIcon

# 导入音效管理器和主题
try:
    from src.sound_manager import get_sound_manager
    from src.themes import apply_theme_to_widget
    from src.modern_ui import (ModernButton, ModernInput, ModernComboBox, 
                              ModernTableWidget, ModernTextEdit, ModernCard, COLORS)
except ImportError:
    try:
        from sound_manager import get_sound_manager
        from themes import apply_theme_to_widget
        from modern_ui import (ModernButton, ModernInput, ModernComboBox, 
                              ModernTableWidget, ModernTextEdit, ModernCard, COLORS)
    except ImportError:
        get_sound_manager = None
        apply_theme_to_widget = None
        # 回退到原始组件
        ModernButton = QPushButton
        ModernInput = QLineEdit
        ModernComboBox = QComboBox
        ModernTableWidget = QTableWidget
        ModernTextEdit = QTextEdit
        ModernCard = QWidget
        COLORS = {'background': '#e0e5ec', 'surface': '#e0e5ec', 'primary': '#6366f1', 'primary_dark': '#4f46e5', 
                  'primary_light': '#a5b4fc', 'text_primary': '#4a5568', 'shadow_dark': '#a3b1c6', 'shadow_light': '#ffffff'}


class TaskDialog(QDialog):
    """任务编辑对话框"""
    
    def __init__(self, parent=None, task_data=None, database=None):
        super().__init__(parent)
        self.task_data = task_data or {}
        self.database = database  # [v0.3.0] 数据库引用用于标签操作
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("编辑任务" if self.task_data else "添加任务")
        self.setFixedSize(500, 500)  # [v0.3.0] 增加高度以容纳标签组件
        
        # 应用浅色主题
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                color: #333333;
            }
        """)
        
        layout = QFormLayout()
        
        # 任务标题
        self.title_edit = ModernInput("输入任务标题...")
        if 'title' in self.task_data:
            self.title_edit.setText(self.task_data['title'])
        layout.addRow("标题*:", self.title_edit)
        
        # 任务描述
        self.desc_edit = ModernTextEdit()
        self.desc_edit.setPlaceholderText("输入任务描述（可选）...")
        self.desc_edit.setMaximumHeight(100)
        if 'description' in self.task_data:
            self.desc_edit.setPlainText(self.task_data['description'])
        layout.addRow("描述:", self.desc_edit)
        
        # 截止日期
        self.due_date_edit = QDateTimeEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDateTime(QDateTime.currentDateTime())
        if 'due_date' in self.task_data and self.task_data['due_date']:
            # 解析日期字符串
            try:
                dt = QDateTime.fromString(self.task_data['due_date'], "yyyy-MM-dd HH:mm:ss")
                if dt.isValid():
                    self.due_date_edit.setDateTime(dt)
            except:
                pass
        layout.addRow("截止日期:", self.due_date_edit)
        
        # 优先级
        self.priority_combo = ModernComboBox()
        self.priority_combo.addItems(["低", "中", "高"])
        if 'priority' in self.task_data:
            self.priority_combo.setCurrentIndex(self.task_data['priority'] - 1)
        layout.addRow("优先级:", self.priority_combo)
        
        # 分类
        self.category_combo = ModernComboBox()
        self.category_combo.addItems(["一般", "工作", "学习", "生活", "其他"])
        self.category_combo.setEditable(True)
        if 'category' in self.task_data and self.task_data['category']:
            # 设置分类
            index = self.category_combo.findText(self.task_data['category'])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                # 如果不在列表中，添加并选中
                self.category_combo.addItem(self.task_data['category'])
                self.category_combo.setCurrentText(self.task_data['category'])
        layout.addRow("分类:", self.category_combo)
        
        # 标签选择 [v0.3.0]
        tags_layout = QVBoxLayout()
        
        # 标签输入和添加
        tag_input_layout = QHBoxLayout()
        self.tag_input = ModernInput("输入新标签...")
        add_tag_btn = ModernButton("+ 添加", style="secondary")
        add_tag_btn.clicked.connect(self.add_new_tag)
        tag_input_layout.addWidget(self.tag_input)
        tag_input_layout.addWidget(add_tag_btn)
        tags_layout.addLayout(tag_input_layout)
        
        # 标签列表（使用简单的文本显示，暂不使用复杂组件）
        self.tags_label = QLabel("标签: 无")
        self.tags_label.setWordWrap(True)
        tags_layout.addWidget(self.tags_label)
        
        # 可用标签按钮
        self.tags_buttons_layout = QHBoxLayout()
        self.tags_buttons_layout.addStretch()
        tags_layout.addLayout(self.tags_buttons_layout)
        
        # 存储选中的标签ID
        self.selected_tag_ids = set()
        
        # 加载标签
        self.load_tags()
        
        layout.addRow("标签:", tags_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_btn = ModernButton("保存", style="primary")
        save_btn.clicked.connect(self.accept)
        cancel_btn = ModernButton("取消", style="secondary")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow("", button_layout)
        
        self.setLayout(layout)
    
    def load_tags(self):
        """加载标签 [v0.3.0]"""
        if not self.database:
            return
        
        # 获取所有标签
        all_tags = self.database.get_all_tags()
        
        # 如果正在编辑任务，加载任务的标签
        if 'id' in self.task_data:
            task_tags = self.database.get_task_tags(self.task_data['id'])
            self.selected_tag_ids = {tag['id'] for tag in task_tags}
        
        # 清空现有按钮
        while self.tags_buttons_layout.count() > 1:  # 保留stretch
            item = self.tags_buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 创建标签按钮
        for tag in all_tags:
            btn = QPushButton(f"🏷️ {tag['name']}")
            btn.setCheckable(True)
            btn.setChecked(tag['id'] in self.selected_tag_ids)
            btn.clicked.connect(lambda checked, tag_id=tag['id']: self.toggle_tag(tag_id, checked))
            self.tags_buttons_layout.insertWidget(self.tags_buttons_layout.count() - 1, btn)
        
        self.update_tags_label()
    
    def add_new_tag(self):
        """添加新标签 [v0.3.0]"""
        if not self.database:
            return
        
        tag_name = self.tag_input.text().strip()
        if not tag_name:
            return
        
        # 添加到数据库
        tag_id = self.database.add_tag(tag_name)
        if tag_id:
            self.tag_input.clear()
            self.load_tags()
            # 自动选中新标签
            self.selected_tag_ids.add(tag_id)
            self.load_tags()
    
    def toggle_tag(self, tag_id, checked):
        """切换标签选择 [v0.3.0]"""
        if checked:
            self.selected_tag_ids.add(tag_id)
        else:
            self.selected_tag_ids.discard(tag_id)
        self.update_tags_label()
    
    def update_tags_label(self):
        """更新标签显示 [v0.3.0]"""
        if not self.database or not self.selected_tag_ids:
            self.tags_label.setText("标签: 无")
            return
        
        # 获取选中标签的名称
        all_tags = self.database.get_all_tags()
        selected_names = [tag['name'] for tag in all_tags if tag['id'] in self.selected_tag_ids]
        
        if selected_names:
            self.tags_label.setText(f"标签: {', '.join(selected_names)}")
        else:
            self.tags_label.setText("标签: 无")
    
    def get_selected_tag_ids(self):
        """获取选中的标签ID列表 [v0.3.0]"""
        return list(self.selected_tag_ids)
    
    def get_task_data(self):
        """获取任务数据"""
        return {
            'title': self.title_edit.text(),
            'description': self.desc_edit.toPlainText(),
            'due_date': self.due_date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            'priority': self.priority_combo.currentIndex() + 1,
            'category': self.category_combo.currentText(),
        }


class TodoWindow(QWidget):
    """待办事项窗口"""
    
    # 信号
    task_added = pyqtSignal(dict)
    task_updated = pyqtSignal(int, dict)
    task_deleted = pyqtSignal(int)
    
    def __init__(self, database=None):
        super().__init__()
        self.database = database
        self.current_theme = 'light'  # 默认主题 [v0.3.0]
        self.statistics_window = None  # 统计窗口引用 [v0.3.0]
        self.current_category = None  # 当前选中的分类
        self.current_tag_id = None  # 当前选中的标签ID
        self.tag_buttons = []  # 标签按钮列表
        self.current_view = 'list'  # 当前视图：list/timeline/calendar/kanban
        self.task_table = None  # 任务表格（列表视图）
        self.timeline_tree = None  # 时间轴树（时间轴视图）
        self.calendar_widget = None  # 日历组件（日历视图）
        self.kanban_lists = {}  # 看板列（看板视图）
        self.init_ui()
        
        # 加载任务（延迟到UI创建完成后）
        QApplication.processEvents()
        if self.database and self.task_table:
            self.load_tasks()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("待办事项")
        self.setGeometry(100, 100, 1000, 700)
        
        # 应用浅色主题背景（类似Clash Verge）
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #333333;
            }
        """)
        
        # 主布局（水平布局：左侧边栏 + 主内容区）
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧边栏
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # 主内容区
        content_area = self.create_content_area()
        main_layout.addWidget(content_area, 1)  # 主内容区占据剩余空间
        
        self.setLayout(main_layout)
        
        # 添加快捷键
        self.setup_shortcuts()
        
        # 应用主题 [v0.3.0]
        self.apply_theme(self.current_theme)
    
    def create_sidebar(self):
        """创建左侧边栏（分类导航）"""
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-right: 1px solid #e0e0e0;
            }
        """)
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # 系统设置按钮（顶部）
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedHeight(50)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 20px;
                text-align: left;
                padding-left: 20px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        sidebar_layout.addWidget(settings_btn)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #e0e0e0; max-height: 1px;")
        sidebar_layout.addWidget(line)
        
        # 分类列表
        categories_label = QLabel("分类")
        categories_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 10px 20px 5px 20px;
                font-weight: bold;
            }
        """)
        sidebar_layout.addWidget(categories_label)
        
        # 分类按钮列表
        self.category_buttons = []
        categories = ["工作", "文档", "生活", "报表", "读书", "今日", "其他"]
        
        for category in categories:
            btn = QPushButton(category)
            btn.setFixedHeight(40)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    text-align: left;
                    padding-left: 20px;
                    color: #333333;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                }
                QPushButton:checked {
                    background-color: #e3f2fd;
                    color: #1976d2;
                    font-weight: bold;
                }
            """)
            btn.clicked.connect(lambda checked, cat=category: self.filter_by_category(cat))
            self.category_buttons.append(btn)
            sidebar_layout.addWidget(btn)
        
        # 默认选中"工作"
        if self.category_buttons:
            self.category_buttons[0].setChecked(True)
        
        # 添加分类按钮
        add_category_btn = QPushButton("+ 添加分类")
        add_category_btn.setFixedHeight(40)
        add_category_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                text-align: left;
                padding-left: 20px;
                color: #1976d2;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        sidebar_layout.addWidget(add_category_btn)
        
        # 分隔线
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("background-color: #e0e0e0; max-height: 1px; margin: 5px 0;")
        sidebar_layout.addWidget(line2)
        
        # 标签列表
        tags_label = QLabel("标签")
        tags_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 10px 20px 5px 20px;
                font-weight: bold;
            }
        """)
        sidebar_layout.addWidget(tags_label)
        
        # 标签按钮列表容器（使用QWidget包装以便滚动）
        tags_widget = QWidget()
        tags_layout = QVBoxLayout(tags_widget)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(0)
        
        self.tag_buttons = []
        # 初始化时加载标签
        if self.database:
            self.load_tags_to_sidebar(tags_layout)
        
        # 使用滚动区域包装标签列表
        tags_scroll_area = QScrollArea()
        tags_scroll_area.setWidget(tags_widget)
        tags_scroll_area.setWidgetResizable(True)
        tags_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        tags_scroll_area.setMaximumHeight(200)
        sidebar_layout.addWidget(tags_scroll_area)
        
        # 刷新标签按钮
        refresh_tags_btn = QPushButton("🔄 刷新标签")
        refresh_tags_btn.setFixedHeight(35)
        refresh_tags_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                text-align: left;
                padding-left: 20px;
                color: #666666;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        refresh_tags_btn.clicked.connect(lambda: self.load_tags_to_sidebar(tags_layout))
        sidebar_layout.addWidget(refresh_tags_btn)
        
        sidebar_layout.addStretch()
        sidebar.setLayout(sidebar_layout)
        
        return sidebar
    
    def create_content_area(self):
        """创建主内容区"""
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 视图标签页
        self.view_tabs = QTabWidget()
        self.view_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                color: #666666;
                border: none;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background-color: #1976d2;
                color: white;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e8e8e8;
            }
        """)
        
        # 列表视图
        list_view_widget = self.create_list_view()
        self.view_tabs.addTab(list_view_widget, "列表视图")
        
        # 时间轴视图
        timeline_view_widget = self.create_timeline_view()
        self.view_tabs.addTab(timeline_view_widget, "时间轴")
        
        # 日历视图
        calendar_view_widget = self.create_calendar_view()
        self.view_tabs.addTab(calendar_view_widget, "日历")
        
        # 看板视图
        kanban_view_widget = self.create_kanban_view()
        self.view_tabs.addTab(kanban_view_widget, "看板")
        
        # 连接标签页切换事件
        self.view_tabs.currentChanged.connect(self.on_view_changed)
        
        content_layout.addWidget(self.view_tabs)
        content_widget.setLayout(content_layout)
        
        # UI创建完成后加载任务（如果task_table已创建）
        if self.task_table and self.database:
            QApplication.processEvents()  # 确保UI已完全渲染
            self.load_tasks()
        
        return content_widget
    
    def create_list_view(self):
        """创建列表视图"""
        list_widget = QWidget()
        list_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)
        
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(20, 20, 20, 20)
        list_layout.setSpacing(15)
        
        # 顶部标题栏
        header = self.create_header()
        list_layout.addLayout(header)
        
        # 任务列表表格
        self.task_table = ModernTableWidget()
        self.task_table.setColumnCount(7)
        self.task_table.setHorizontalHeaderLabels([
            "ID", "标题", "截止时间", "优先级", "状态", "分类", "标签"
        ])
        
        # 设置表格属性
        self.task_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.task_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.task_table.horizontalHeader().setStretchLastSection(True)
        self.task_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )
        
        # 隐藏ID列
        self.task_table.setColumnHidden(0, True)
        
        # 双击编辑
        self.task_table.doubleClicked.connect(self.edit_task)
        
        # 应用浅色主题样式
        self.task_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                gridline-color: #f0f0f0;
                selection-background-color: #e3f2fd;
                alternate-background-color: #fafafa;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTableWidget QHeaderView::section {
                background-color: #fafafa;
                color: #333333;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                padding: 12px;
                font-weight: 600;
                font-size: 13px;
            }
        """)
        
        list_layout.addWidget(self.task_table)
        
        # 底部工具栏和状态栏
        footer = self.create_footer()
        list_layout.addLayout(footer)
        
        list_widget.setLayout(list_layout)
        return list_widget
    
    def create_timeline_view(self):
        """创建时间轴视图"""
        timeline_widget = QWidget()
        timeline_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)
        
        timeline_layout = QVBoxLayout()
        timeline_layout.setContentsMargins(20, 20, 20, 20)
        timeline_layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("时间轴视图")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                padding: 10px 0;
            }
        """)
        timeline_layout.addWidget(title_label)
        
        # 时间轴树
        self.timeline_tree = QTreeWidget()
        self.timeline_tree.setHeaderLabels(["任务", "状态"])
        self.timeline_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTreeWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        self.timeline_tree.itemDoubleClicked.connect(self.on_timeline_item_double_clicked)
        timeline_layout.addWidget(self.timeline_tree)
        
        timeline_widget.setLayout(timeline_layout)
        
        # 初始化时加载数据
        if self.database:
            self.refresh_timeline_view()
        
        return timeline_widget
    
    def create_calendar_view(self):
        """创建日历视图"""
        calendar_widget = QWidget()
        calendar_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)
        
        calendar_layout = QVBoxLayout()
        calendar_layout.setContentsMargins(20, 20, 20, 20)
        calendar_layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("日历视图")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                padding: 10px 0;
            }
        """)
        calendar_layout.addWidget(title_label)
        
        # 日历组件
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setStyleSheet("""
            QCalendarWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                selection-background-color: #1976d2;
                selection-color: white;
            }
        """)
        self.calendar_widget.selectionChanged.connect(self.on_calendar_date_selected)
        self.calendar_widget.clicked.connect(self.on_calendar_date_selected)
        calendar_layout.addWidget(self.calendar_widget)
        
        # 任务列表（选中日期的任务）
        self.calendar_task_list = QListWidget()
        self.calendar_task_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        self.calendar_task_list.itemDoubleClicked.connect(self.on_calendar_task_double_clicked)
        calendar_layout.addWidget(self.calendar_task_list)
        
        calendar_widget.setLayout(calendar_layout)
        
        # 初始化时加载数据
        if self.database:
            self.refresh_calendar_view()
        
        return calendar_widget
    
    def create_kanban_view(self):
        """创建看板视图"""
        kanban_widget = QWidget()
        kanban_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)
        
        kanban_layout = QVBoxLayout()
        kanban_layout.setContentsMargins(20, 20, 20, 20)
        kanban_layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("看板视图")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                padding: 10px 0;
            }
        """)
        kanban_layout.addWidget(title_label)
        
        # 看板列（水平布局）
        kanban_columns = QHBoxLayout()
        kanban_columns.setSpacing(15)
        
        # 待完成列
        pending_column = self.create_kanban_column("待完成", "pending")
        kanban_columns.addWidget(pending_column)
        
        # 已完成列
        completed_column = self.create_kanban_column("已完成", "completed")
        kanban_columns.addWidget(completed_column)
        
        # 已过期列
        expired_column = self.create_kanban_column("已过期", "expired")
        kanban_columns.addWidget(expired_column)
        
        kanban_layout.addLayout(kanban_columns)
        kanban_widget.setLayout(kanban_layout)
        
        # 初始化时加载数据
        if self.database:
            self.refresh_kanban_view()
        
        return kanban_widget
    
    def create_kanban_column(self, title, status_key):
        """创建看板列"""
        column_widget = QWidget()
        column_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-radius: 8px;
            }
        """)
        
        column_layout = QVBoxLayout()
        column_layout.setContentsMargins(10, 10, 10, 10)
        column_layout.setSpacing(5)
        
        # 列标题
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                padding: 5px;
            }
        """)
        column_layout.addWidget(title_label)
        
        # 任务列表
        task_list = QListWidget()
        task_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                min-height: 400px;
            }
            QListWidget::item {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                margin: 3px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-color: #1976d2;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        task_list.itemDoubleClicked.connect(self.on_kanban_task_double_clicked)
        task_list.setDragDropMode(QListWidget.DragDrop)
        task_list.setDefaultDropAction(Qt.MoveAction)
        column_layout.addWidget(task_list)
        
        column_widget.setLayout(column_layout)
        
        # 保存引用
        self.kanban_lists[status_key] = task_list
        
        return column_widget
    
    def on_view_changed(self, index):
        """视图切换回调"""
        try:
            view_names = ['list', 'timeline', 'calendar', 'kanban']
            if 0 <= index < len(view_names):
                old_view = self.current_view
                self.current_view = view_names[index]
                print(f"[待办窗口] 切换到视图: {view_names[index]}")
                
                # 刷新当前视图
                self.refresh_current_view()
        except Exception as e:
            print(f"[待办窗口] 视图切换异常: {e}")
            import traceback
            traceback.print_exc()
            # 回退到列表视图
            if self.view_tabs:
                self.view_tabs.setCurrentIndex(0)
                self.current_view = 'list'
    
    def refresh_current_view(self):
        """刷新当前视图"""
        try:
            if self.current_view == 'list':
                if self.task_table:
                    self.load_tasks()
            elif self.current_view == 'timeline':
                self.refresh_timeline_view()
            elif self.current_view == 'calendar':
                self.refresh_calendar_view()
            elif self.current_view == 'kanban':
                self.refresh_kanban_view()
        except Exception as e:
            print(f"[待办窗口] 刷新视图失败: {e}")
            import traceback
            traceback.print_exc()
    
    def create_header(self):
        """创建顶部标题栏"""
        header_layout = QHBoxLayout()
        
        # 当前分类标题
        self.category_title = QLabel("工作")
        self.category_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
            }
        """)
        header_layout.addWidget(self.category_title)
        
        # 分类信息（如"1个默认"）
        category_info = QLabel("1个默认")
        category_info.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #666666;
                margin-left: 10px;
            }
        """)
        header_layout.addWidget(category_info)
        
        header_layout.addStretch()
        
        # 添加任务按钮
        self.add_btn = QPushButton("+ 新增待办")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        self.add_btn.clicked.connect(self.add_task)
        header_layout.addWidget(self.add_btn)
        
        return header_layout
    
    def create_footer(self):
        """创建底部工具栏和状态栏"""
        footer_layout = QVBoxLayout()
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        # 编辑按钮
        self.edit_btn = QPushButton("✏️ 编辑")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #eeeeee;
            }
        """)
        self.edit_btn.clicked.connect(self.edit_task)
        
        # 删除按钮
        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #eeeeee;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_task)
        
        # 完成按钮
        self.complete_btn = QPushButton("✅ 完成")
        self.complete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #eeeeee;
            }
        """)
        self.complete_btn.clicked.connect(self.complete_task)
        
        # 统计按钮
        self.stats_btn = QPushButton("📊 统计")
        self.stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #eeeeee;
            }
        """)
        self.stats_btn.clicked.connect(self.show_statistics)
        
        toolbar_layout.addWidget(self.edit_btn)
        toolbar_layout.addWidget(self.delete_btn)
        toolbar_layout.addWidget(self.complete_btn)
        toolbar_layout.addWidget(self.stats_btn)
        
        # 搜索框
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 搜索任务...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #1976d2;
                background-color: #ffffff;
            }
        """)
        self.search_edit.textChanged.connect(self.search_tasks)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_edit)
        
        # 筛选下拉框
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部", "待完成", "已完成", "已过期"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                min-width: 100px;
            }
            QComboBox:hover {
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #666666;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.filter_tasks)
        toolbar_layout.addWidget(QLabel("筛选:"))
        toolbar_layout.addWidget(self.filter_combo)
        
        footer_layout.addLayout(toolbar_layout)
        
        # 状态栏
        status_bar = self.create_status_bar()
        footer_layout.addLayout(status_bar)
        
        return footer_layout
    
    def filter_by_category(self, category):
        """按分类筛选任务"""
        # 清除标签筛选
        self.current_tag_id = None
        for tag_btn in self.tag_buttons:
            tag_btn.setChecked(False)
        
        # 处理特殊分类
        if category == "今日":
            self.category_title.setText("今日")
            self.current_category = None
            # 加载今日任务（只在列表视图时更新表格）
            if self.database:
                if self.task_table and self.current_view == 'list':
                    tasks = self.database.get_today_tasks()
                    self.task_table.setRowCount(0)
                    for task in tasks:
                        self.add_task_to_table(task)
                    self.update_status()
                # 更新其他视图
                self.refresh_current_view()
        else:
            self.category_title.setText(category)
            self.current_category = category
            # 刷新任务列表
            if self.current_view == 'list':
                self.load_tasks()
            else:
                self.refresh_current_view()
        
        # 更新侧边栏按钮状态
        for btn in self.category_buttons:
            btn.setChecked(btn.text() == category)
    
    def filter_by_tag(self, tag_id, tag_name):
        """按标签筛选任务"""
        # 清除分类筛选
        self.current_category = None
        for btn in self.category_buttons:
            btn.setChecked(False)
        
        self.current_tag_id = tag_id
        self.category_title.setText(f"标签: {tag_name}")
        
        # 刷新任务列表
        if self.current_view == 'list':
            self.load_tasks()
        else:
            self.refresh_current_view()
    
    def load_tags_to_sidebar(self, layout):
        """加载标签到侧边栏"""
        # 清空现有标签按钮
        for tag_btn in self.tag_buttons:
            tag_btn.deleteLater()
        self.tag_buttons.clear()
        
        # 清空布局
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.database:
            return
        
        # 获取所有标签
        tags = self.database.get_all_tags()
        
        if not tags:
            no_tags_label = QLabel("暂无标签")
            no_tags_label.setStyleSheet("""
                QLabel {
                    color: #999999;
                    font-size: 12px;
                    padding: 10px 20px;
                }
            """)
            layout.addWidget(no_tags_label)
            return
        
        # 创建标签按钮
        for tag in tags:
            tag_btn = QPushButton(f"🏷️ {tag['name']}")
            tag_btn.setFixedHeight(35)
            tag_btn.setCheckable(True)
            tag_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    text-align: left;
                    padding-left: 20px;
                    color: #333333;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                }
                QPushButton:checked {
                    background-color: #e3f2fd;
                    color: #1976d2;
                    font-weight: bold;
                }
            """)
            tag_btn.clicked.connect(lambda checked, tid=tag['id'], tname=tag['name']: 
                                   self.filter_by_tag(tid, tname) if checked else None)
            self.tag_buttons.append(tag_btn)
            layout.addWidget(tag_btn)
        
        layout.addStretch()
    
    def create_status_bar(self):
        """创建状态栏"""
        status_bar = QHBoxLayout()
        status_bar.setContentsMargins(0, 10, 0, 0)
        
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 5px;
            }
        """)
        
        self.task_count_label = QLabel("总任务: 0")
        self.task_count_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 5px;
            }
        """)
        
        status_bar.addWidget(self.status_label)
        status_bar.addStretch()
        status_bar.addWidget(self.task_count_label)
        
        return status_bar
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+N: 新建任务
        new_task_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_task_shortcut.activated.connect(self.add_task)
        
        # Ctrl+F: 聚焦搜索框
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(lambda: self.search_edit.setFocus())
        
        # Ctrl+W: 关闭窗口
        close_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_shortcut.activated.connect(self.hide)
        
        # Delete: 删除选中任务
        delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_shortcut.activated.connect(self.delete_task)
        
        # Enter: 编辑选中任务
        edit_shortcut = QShortcut(QKeySequence("Return"), self)
        edit_shortcut.activated.connect(self.edit_task)
        
        print("[待办窗口] 快捷键已设置: Ctrl+N(新建) Ctrl+F(搜索) Ctrl+W(关闭) Delete(删除)")
    
    def load_tasks(self, status=None, category=None, tag_id=None):
        """加载任务列表"""
        if not self.database or not self.task_table:
            return
        
        # 使用当前筛选条件
        if category is None:
            category = self.current_category
        if tag_id is None:
            tag_id = self.current_tag_id
        
        # 获取任务
        tasks = self.database.get_all_tasks(status=status, category=category, tag_id=tag_id)
        
        # 清空表格
        self.task_table.setRowCount(0)
        
        # 填充数据
        for task in tasks:
            self.add_task_to_table(task)
        
        # 更新状态
        self.update_status()
    
    def add_task_to_table(self, task):
        """添加任务到表格"""
        if not self.task_table:
            return
        
        row = self.task_table.rowCount()
        self.task_table.insertRow(row)
        
        # ID (隐藏列)
        self.task_table.setItem(row, 0, QTableWidgetItem(str(task['id'])))
        
        # 标题
        self.task_table.setItem(row, 1, QTableWidgetItem(task['title']))
        
        # 截止时间
        due_date = task['due_date'] if task['due_date'] else "未设置"
        self.task_table.setItem(row, 2, QTableWidgetItem(due_date))
        
        # 优先级
        priority_map = {1: "低", 2: "中", 3: "高"}
        priority_text = priority_map.get(task['priority'], "中")
        priority_item = QTableWidgetItem(priority_text)
        
        # 根据优先级设置颜色
        if task['priority'] == 3:
            priority_item.setForeground(QColor(255, 0, 0))  # 红色
        elif task['priority'] == 2:
            priority_item.setForeground(QColor(255, 165, 0))  # 橙色
        
        self.task_table.setItem(row, 3, priority_item)
        
        # 状态
        status_map = {
            'pending': '待完成',
            'completed': '已完成',
            'expired': '已过期'
        }
        status_text = status_map.get(task['status'], '未知')
        self.task_table.setItem(row, 4, QTableWidgetItem(status_text))
        
        # 分类
        self.task_table.setItem(row, 5, QTableWidgetItem(task['category']))
        
        # 标签（第6列）
        if self.database:
            tags = self.database.get_task_tags(task['id'])
            if tags:
                tag_names = [tag['name'] for tag in tags]
                tag_text = ", ".join(tag_names)
            else:
                tag_text = ""
            self.task_table.setItem(row, 6, QTableWidgetItem(tag_text))
        else:
            self.task_table.setItem(row, 6, QTableWidgetItem(""))
    
    def add_task(self):
        """添加新任务"""
        try:
            dialog = TaskDialog(self, database=self.database)  # [v0.3.0] 传递database
            if dialog.exec_() == QDialog.Accepted:
                task_data = dialog.get_task_data()
                
                # 验证标题
                if not task_data['title'].strip():
                    QMessageBox.warning(self, "警告", "任务标题不能为空！")
                    return
                
                # 获取选中的标签 [v0.3.0]
                tag_ids = dialog.get_selected_tag_ids()
                
                # 保存到数据库
                if self.database:
                    task_id = self.database.add_task(**task_data)
                    
                    if task_id > 0:
                        # 保存标签关联 [v0.3.0]
                        for tag_id in tag_ids:
                            self.database.add_task_tag(task_id, tag_id)
                        
                        task_data['id'] = task_id
                        task_data['status'] = 'pending'
                        
                        # 添加到表格（如果当前在列表视图）
                        if self.current_view == 'list' and self.task_table:
                            self.add_task_to_table(task_data)
                            self.update_status()
                        
                        # 刷新所有视图
                        self.refresh_current_view()
                        
                        # 发送信号
                        self.task_added.emit(task_data)
                        
                        self.status_label.setText(f"✅ 添加任务成功: {task_data['title']}")
                        self.status_label.setStyleSheet("""
                            QLabel {
                                color: #4caf50;
                                font-size: 12px;
                                padding: 5px;
                            }
                        """)
                    else:
                        QMessageBox.warning(self, "错误", "添加任务失败，请查看日志")
                        self.status_label.setText("❌ 添加任务失败")
                        self.status_label.setStyleSheet("""
                            QLabel {
                                color: #f44336;
                                font-size: 12px;
                                padding: 5px;
                            }
                        """)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加任务时发生错误：\n{str(e)}")
            self.status_label.setText("❌ 添加任务失败")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #f44336;
                    font-size: 12px;
                    padding: 5px;
                }
            """)
            print(f"[待办窗口] 添加任务异常: {e}")
    
    def edit_task(self):
        """编辑选中的任务"""
        if not self.task_table:
            QMessageBox.warning(self, "警告", "请先切换到列表视图！")
            return
        
        current_row = self.task_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要编辑的任务！")
            return
        
        # 获取任务ID
        task_id = int(self.task_table.item(current_row, 0).text())
        
        # 从数据库获取完整任务数据
        if not self.database:
            QMessageBox.warning(self, "错误", "数据库未初始化！")
            return
        
        task_data = self.database.get_task(task_id)
        if not task_data:
            QMessageBox.warning(self, "错误", f"找不到任务 ID: {task_id}")
            return
        
        # 显示编辑对话框
        dialog = TaskDialog(self, task_data, database=self.database)  # [v0.3.0] 传递database
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_task_data()
            
            # 获取新的标签 [v0.3.0]
            new_tag_ids = set(dialog.get_selected_tag_ids())
            old_tag_ids = {tag['id'] for tag in self.database.get_task_tags(task_id)}
            
            # 更新数据库
            self.database.update_task(task_id, **new_data)
            
            # 更新标签关联 [v0.3.0]
            # 删除不再需要的标签
            for tag_id in old_tag_ids - new_tag_ids:
                self.database.remove_task_tag(task_id, tag_id)
            # 添加新标签
            for tag_id in new_tag_ids - old_tag_ids:
                self.database.add_task_tag(task_id, tag_id)
            
            # 刷新所有视图
            self.refresh_current_view()
            
            # 更新状态
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"✅ 任务已更新: {new_data['title']}")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #4caf50;
                    font-size: 12px;
                    padding: 5px;
                }
            """)
            
            # 发送信号
            self.task_updated.emit(task_id, new_data)
    
    def delete_task(self):
        """删除选中的任务（支持多选）"""
        if not self.task_table:
            QMessageBox.warning(self, "警告", "请先切换到列表视图！")
            return
        
        try:
            # 获取所有选中的行
            selected_ranges = self.task_table.selectedRanges()
            if not selected_ranges:
                QMessageBox.warning(self, "警告", "请先选择要删除的任务！")
                return
            
            # 收集所有选中的行号（去重）
            selected_rows = set()
            for range_obj in selected_ranges:
                for row in range(range_obj.topRow(), range_obj.bottomRow() + 1):
                    selected_rows.add(row)
            
            if not selected_rows:
                QMessageBox.warning(self, "警告", "请先选择要删除的任务！")
                return
            
            # 确认删除
            count = len(selected_rows)
            reply = QMessageBox.question(
                self, "确认", f"确定要删除选中的 {count} 个任务吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 获取所有选中行的任务ID（按行号倒序排列，以便从后往前删除，避免索引变化问题）
                task_ids = []
                rows_to_delete = sorted(selected_rows, reverse=True)
                
                for row in rows_to_delete:
                    try:
                        task_id_item = self.task_table.item(row, 0)
                        if task_id_item:
                            task_id = int(task_id_item.text())
                            task_ids.append((row, task_id))
                    except (ValueError, AttributeError) as e:
                        print(f"[待办窗口] 获取任务ID失败，行{row}: {e}")
                        continue
                
                if not task_ids:
                    QMessageBox.warning(self, "错误", "无法获取任务ID")
                    return
                
                # 批量删除
                if self.database:
                    success_count = 0
                    failed_count = 0
                    
                    for row, task_id in task_ids:
                        try:
                            if self.database.delete_task(task_id):
                                self.task_deleted.emit(task_id)
                                success_count += 1
                            else:
                                failed_count += 1
                                print(f"[待办窗口] 删除任务失败，ID: {task_id}")
                        except Exception as e:
                            failed_count += 1
                            print(f"[待办窗口] 删除任务异常，ID: {task_id}, 错误: {e}")
                    
                    # 刷新所有视图
                    self.refresh_current_view()
                    
                    if failed_count == 0:
                        self.status_label.setText(f"✅ 成功删除 {success_count} 个任务")
                        self.status_label.setStyleSheet("""
                            QLabel {
                                color: #4caf50;
                                font-size: 12px;
                                padding: 5px;
                            }
                        """)
                    elif success_count > 0:
                        self.status_label.setText(f"⚠️ 成功删除 {success_count} 个，失败 {failed_count} 个")
                        self.status_label.setStyleSheet("""
                            QLabel {
                                color: #ff9800;
                                font-size: 12px;
                                padding: 5px;
                            }
                        """)
                    else:
                        QMessageBox.warning(self, "错误", f"删除任务失败，共 {failed_count} 个任务删除失败")
                        self.status_label.setText("❌ 删除任务失败")
                        self.status_label.setStyleSheet("""
                            QLabel {
                                color: #f44336;
                                font-size: 12px;
                                padding: 5px;
                            }
                        """)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除任务时发生错误：\n{str(e)}")
            self.status_label.setText("❌ 删除任务失败")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #f44336;
                    font-size: 12px;
                    padding: 5px;
                }
            """)
            print(f"[待办窗口] 删除任务异常: {e}")
    
    def complete_task(self):
        """标记任务为已完成"""
        if not self.task_table:
            QMessageBox.warning(self, "警告", "请先切换到列表视图！")
            return
        
        try:
            current_row = self.task_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "警告", "请先选择要完成的任务！")
                return
            
            # 获取任务ID
            task_id = int(self.task_table.item(current_row, 0).text())
            
            # 更新数据库
            if self.database:
                if self.database.mark_completed(task_id):
                    # 刷新所有视图
                    self.refresh_current_view()
                    
                    if hasattr(self, 'status_label'):
                        self.status_label.setText("✅ 任务已完成！")
                    self.status_label.setStyleSheet("""
                        QLabel {
                            color: #4caf50;
                            font-size: 12px;
                            padding: 5px;
                        }
                    """)
                    
                    # 播放完成音效 [v0.3.0]
                    if get_sound_manager:
                        sound_mgr = get_sound_manager()
                        sound_mgr.play_complete()
                else:
                    QMessageBox.warning(self, "错误", "标记完成失败")
                    self.status_label.setText("❌ 操作失败")
                    self.status_label.setStyleSheet("""
                        QLabel {
                            color: #f44336;
                            font-size: 12px;
                            padding: 5px;
                        }
                    """)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"标记完成时发生错误：\n{str(e)}")
            self.status_label.setText("❌ 操作失败")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #f44336;
                    font-size: 12px;
                    padding: 5px;
                }
            """)
            print(f"[待办窗口] 标记完成异常: {e}")
    
    def search_tasks(self, keyword):
        """搜索任务"""
        if not self.task_table:
            return
        
        if not keyword.strip():
            # 如果搜索框为空，恢复当前筛选
            self.load_tasks(category=self.current_category, tag_id=self.current_tag_id)
            return
        
        if not self.database:
            return
        
        # 使用数据库搜索
        all_tasks = self.database.search_tasks(keyword)
        
        # 进一步按分类和标签筛选
        filtered_tasks = []
        for task in all_tasks:
            # 分类筛选
            if self.current_category and task.get('category') != self.current_category:
                continue
            # 标签筛选
            if self.current_tag_id:
                task_tags = self.database.get_task_tags(task['id'])
                if not any(tag['id'] == self.current_tag_id for tag in task_tags):
                    continue
            filtered_tasks.append(task)
        
        # 清空表格
        self.task_table.setRowCount(0)
        
        # 显示搜索结果
        for task in filtered_tasks:
            self.add_task_to_table(task)
        
        # 更新状态
        self.update_status()
        self.status_label.setText(f"🔍 找到 {len(filtered_tasks)} 个匹配任务")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 5px;
            }
        """)
    
    def filter_tasks(self, filter_text):
        """筛选任务（按状态）"""
        status_map = {
            "全部": None,
            "待完成": "pending",
            "已完成": "completed",
            "已过期": "expired"
        }
        
        status = status_map.get(filter_text)
        # 保持当前分类和标签筛选
        self.load_tasks(status=status, category=self.current_category, tag_id=self.current_tag_id)
    
    def update_status(self):
        """更新状态栏"""
        if not self.task_table:
            return
        
        count = self.task_table.rowCount()
        if hasattr(self, 'task_count_label'):
            self.task_count_label.setText(f"总任务: {count}")
    
    def show_statistics(self):
        """
        显示统计窗口 [v0.3.0]
        """
        try:
            if self.statistics_window is None:
                # 延迟导入
                try:
                    from src.statistics_window import StatisticsWindow
                except ImportError:
                    from statistics_window import StatisticsWindow
                
                self.statistics_window = StatisticsWindow(self.database)
                self.statistics_window.apply_theme(self.current_theme)
            
            self.statistics_window.load_statistics()  # 刷新数据
            self.statistics_window.show()
            self.statistics_window.raise_()
            self.statistics_window.activateWindow()
            
            print("[待办窗口] 打开统计窗口")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开统计窗口失败：\n{str(e)}")
            print(f"[待办窗口] 打开统计窗口异常: {e}")
    
    def apply_theme(self, theme_name='light'):
        """
        应用主题 [v0.3.0]
        
        Args:
            theme_name: 主题名称（'light'/'dark'）
        """
        if apply_theme_to_widget:
            apply_theme_to_widget(self, 'todo_window', theme_name)
            self.current_theme = theme_name
            print(f"[待办窗口] 已应用 {theme_name} 主题")
            
            # 同步主题到统计窗口
            if self.statistics_window:
                self.statistics_window.apply_theme(theme_name)
        else:
            print("[待办窗口] 主题模块不可用")
    
    def refresh_timeline_view(self):
        """刷新时间轴视图"""
        if not self.timeline_tree or not self.database:
            return
        try:
            self.timeline_tree.clear()
            # 获取任务
            tasks = self.database.get_all_tasks(
                category=self.current_category if self.current_category else None,
                tag_id=self.current_tag_id if self.current_tag_id else None
            )
            # 按日期分组
            tasks_by_date = defaultdict(list)
            for task in tasks:
                due_date = task.get('due_date')
                if due_date:
                    try:
                        date_key = due_date[:10] if len(due_date) >= 10 else "未设置"
                    except:
                        date_key = "未设置"
                else:
                    date_key = "未设置"
                tasks_by_date[date_key].append(task)
            # 添加日期组和任务
            for date_key in sorted(tasks_by_date.keys()):
                date_item = QTreeWidgetItem(self.timeline_tree)
                date_item.setText(0, date_key)
                date_item.setExpanded(True)
                for task in sorted(tasks_by_date[date_key], key=lambda x: x.get('priority', 2), reverse=True):
                    task_item = QTreeWidgetItem(date_item)
                    priority_text = {1: "低", 2: "中", 3: "高"}.get(task.get('priority', 2), "中")
                    task_item.setText(0, f"[{priority_text}] {task.get('title', '无标题')}")
                    status_map = {'pending': '待完成', 'completed': '已完成', 'expired': '已过期'}
                    task_item.setText(1, status_map.get(task.get('status', 'pending'), '未知'))
                    task_item.setData(0, Qt.UserRole, task.get('id'))
                    if task.get('priority') == 3:
                        task_item.setForeground(0, QColor(255, 0, 0))
        except Exception as e:
            print(f"[待办窗口] 刷新时间轴视图失败: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_calendar_view(self):
        """刷新日历视图"""
        if not self.calendar_widget or not self.database:
            return
        try:
            # 获取任务
            tasks = self.database.get_all_tasks(
                category=self.current_category if self.current_category else None,
                tag_id=self.current_tag_id if self.current_tag_id else None
            )
            # 标记有任务的日期
            dates_with_tasks = {}
            for task in tasks:
                due_date = task.get('due_date')
                if due_date:
                    try:
                        date_str = due_date[:10] if len(due_date) >= 10 else None
                        if date_str:
                            date = QDate.fromString(date_str, "yyyy-MM-dd")
                            if date.isValid():
                                if date not in dates_with_tasks:
                                    dates_with_tasks[date] = []
                                dates_with_tasks[date].append(task)
                    except:
                        pass
            # 更新日历格式和显示选中日期的任务
            for date, date_tasks in dates_with_tasks.items():
                format = self.calendar_widget.dateTextFormat(date)
                format.setForeground(QColor(255, 0, 0))
                format.setFontWeight(700)
                self.calendar_widget.setDateTextFormat(date, format)
            
            # 显示当前选中日期的任务
            selected_date = self.calendar_widget.selectedDate()
            if hasattr(self, 'calendar_task_list') and self.calendar_task_list:
                self.calendar_task_list.clear()
                if selected_date in dates_with_tasks:
                    for task in dates_with_tasks[selected_date]:
                        priority_text = {1: "低", 2: "中", 3: "高"}.get(task.get('priority', 2), "中")
                        item_text = f"[{priority_text}] {task.get('title', '无标题')}"
                        item = QListWidgetItem(item_text)
                        item.setData(Qt.UserRole, task.get('id'))
                        if task.get('priority') == 3:
                            item.setForeground(QColor(255, 0, 0))
                        self.calendar_task_list.addItem(item)
                # 如果没有选中日期，触发一次选择事件以显示任务
                if not selected_date.isValid():
                    self.calendar_widget.setSelectedDate(QDate.currentDate())
                    self.on_calendar_date_selected()
        except Exception as e:
            print(f"[待办窗口] 刷新日历视图失败: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_kanban_view(self):
        """刷新看板视图"""
        if not self.kanban_lists or not self.database:
            return
        try:
            # 清空所有列
            for status_key in ['pending', 'completed', 'expired']:
                if status_key in self.kanban_lists:
                    self.kanban_lists[status_key].clear()
            # 获取任务
            tasks = self.database.get_all_tasks(
                category=self.current_category if self.current_category else None,
                tag_id=self.current_tag_id if self.current_tag_id else None
            )
            # 添加到对应列
            for task in tasks:
                status = task.get('status', 'pending')
                if status in self.kanban_lists:
                    priority_text = {1: "低", 2: "中", 3: "高"}.get(task.get('priority', 2), "中")
                    item_text = f"[{priority_text}] {task.get('title', '无标题')}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, task.get('id'))
                    priority = task.get('priority', 2)
                    if priority == 3:
                        item.setForeground(QColor(255, 0, 0))
                    self.kanban_lists[status].addItem(item)
        except Exception as e:
            print(f"[待办窗口] 刷新看板视图失败: {e}")
            import traceback
            traceback.print_exc()
    
    def on_timeline_item_double_clicked(self, item, column):
        """时间轴任务双击"""
        task_id = item.data(0, Qt.UserRole)
        if task_id and self.database:
            task_data = self.database.get_task(task_id)
            if task_data:
                dialog = TaskDialog(self, task_data, database=self.database)
                if dialog.exec_() == QDialog.Accepted:
                    self.refresh_current_view()
    
    def on_calendar_date_selected(self, date=None):
        """日历日期选中"""
        if not hasattr(self, 'calendar_task_list') or not self.calendar_widget or not self.database:
            return
        try:
            # 如果没有传入日期，使用当前选中的日期
            if date is None:
                date = self.calendar_widget.selectedDate()
            
            self.calendar_task_list.clear()
            date_str = date.toString("yyyy-MM-dd")
            tasks = self.database.get_all_tasks(
                category=self.current_category if self.current_category else None,
                tag_id=self.current_tag_id if self.current_tag_id else None
            )
            for task in tasks:
                due_date = task.get('due_date', '')
                if due_date and due_date.startswith(date_str):
                    priority_text = {1: "低", 2: "中", 3: "高"}.get(task.get('priority', 2), "中")
                    item_text = f"[{priority_text}] {task.get('title', '无标题')}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, task.get('id'))
                    if task.get('priority') == 3:
                        item.setForeground(QColor(255, 0, 0))
                    self.calendar_task_list.addItem(item)
        except Exception as e:
            print(f"[待办窗口] 加载日历任务失败: {e}")
            import traceback
            traceback.print_exc()
    
    def on_calendar_task_double_clicked(self, item):
        """日历任务双击"""
        task_id = item.data(Qt.UserRole)
        if task_id and self.database:
            task_data = self.database.get_task(task_id)
            if task_data:
                dialog = TaskDialog(self, task_data, database=self.database)
                if dialog.exec_() == QDialog.Accepted:
                    self.refresh_current_view()
    
    def on_kanban_task_double_clicked(self, item):
        """看板任务双击"""
        task_id = item.data(Qt.UserRole)
        if task_id and self.database:
            task_data = self.database.get_task(task_id)
            if task_data:
                dialog = TaskDialog(self, task_data, database=self.database)
                if dialog.exec_() == QDialog.Accepted:
                    self.refresh_current_view()
    
    def closeEvent(self, event):
        """关闭事件 - 隐藏窗口而不是退出"""
        event.ignore()  # 忽略关闭事件
        self.hide()     # 隐藏窗口
        print("[待办窗口] 窗口已隐藏")


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = TodoWindow()
    window.show()
    
    sys.exit(app.exec_())

