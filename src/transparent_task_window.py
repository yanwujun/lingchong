#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
透明桌面任务窗口模块
Transparent Desktop Task Window - 在桌面上透明显示任务列表
"""

import sys
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QApplication,
                             QMenu, QInputDialog, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSize, QRect
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QFont, QFontMetrics, QMouseEvent


class TransparentTaskWindow(QWidget):
    """透明桌面任务窗口"""
    
    # 信号定义
    task_clicked = pyqtSignal(int)  # 任务点击信号
    task_double_clicked = pyqtSignal(int)  # 任务双击信号
    
    def __init__(self, database=None, parent=None):
        """
        初始化透明任务窗口
        
        Args:
            database: 数据库实例
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.database = database
        self.tasks = []  # 未完成任务列表
        self.completed_tasks = []  # 已完成任务列表
        self.is_dragging = False  # 是否正在拖动
        self.drag_position = QPoint()  # 拖动起始位置
        self.opacity = 0.85  # 默认透明度 (0.0-1.0)
        self.show_completed_count = True  # 是否显示完成数量
        self.show_completed = True  # 是否显示已完成任务
        self.is_collapsed = False  # 是否已折叠
        self.saved_height = 400  # 保存的高度
        
        # 从配置或默认值初始化窗口位置和大小
        self.default_x = 50
        self.default_y = 100
        self.default_width = 350
        self.max_height = 600
        
        # 初始化UI
        self.init_ui()
        
        # 设置窗口属性
        self.setup_window()
        
        # 启动定时刷新
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_tasks)
        self.refresh_timer.start(5000)  # 每5秒刷新一次
        
        # 初始加载任务
        self.load_tasks()
    
    def init_ui(self):
        """初始化界面"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(8)
        
        # 标题栏（可拖动）
        title_bar = self.create_title_bar()
        main_layout.addWidget(title_bar)
        
        # 任务列表滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.2);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.5);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.7);
            }
        """)
        
        # 任务容器
        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout()
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_layout.setSpacing(6)
        self.tasks_layout.addStretch()
        self.tasks_container.setLayout(self.tasks_layout)
        
        self.scroll_area.setWidget(self.tasks_container)
        main_layout.addWidget(self.scroll_area, 1)
        
        self.setLayout(main_layout)
    
    def create_title_bar(self):
        """创建标题栏（可拖动区域）"""
        title_widget = QWidget()
        title_widget.setFixedHeight(35)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(5, 0, 5, 0)
        title_layout.setSpacing(10)
        
        # 标题文本
        self.title_label = QLabel("事项清单 - 未完成")
        self.title_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # 控制按钮
        self.collapse_btn = QPushButton("=")
        self.collapse_btn.setFixedSize(24, 24)
        self.collapse_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.7);
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: rgba(255, 255, 255, 1.0);
                background: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
            }
        """)
        self.collapse_btn.clicked.connect(self.toggle_collapse)
        
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(24, 24)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.7);
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: rgba(255, 255, 255, 1.0);
                background: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
            }
        """)
        self.add_btn.clicked.connect(self.show_add_task_dialog)
        
        self.menu_btn = QPushButton("⋮")
        self.menu_btn.setFixedSize(24, 24)
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.7);
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: rgba(255, 255, 255, 1.0);
                background: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
            }
        """)
        self.menu_btn.clicked.connect(self.show_menu)
        
        title_layout.addWidget(self.collapse_btn)
        title_layout.addWidget(self.add_btn)
        title_layout.addWidget(self.menu_btn)
        
        title_widget.setLayout(title_layout)
        
        # 设置鼠标跟踪以便拖动
        title_widget.setMouseTracking(True)
        title_widget.mousePressEvent = self.on_title_mouse_press
        title_widget.mouseMoveEvent = self.on_title_mouse_move
        title_widget.mouseReleaseEvent = self.on_title_mouse_release
        
        return title_widget
    
    def setup_window(self):
        """设置窗口属性"""
        # 设置窗口标志：无边框、置顶、透明
        # 注意：不使用 WindowTransparentForInput，这样任务项才能被点击
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        
        # 设置窗口透明背景
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 设置窗口位置和大小
        self.setGeometry(
            self.default_x,
            self.default_y,
            self.default_width,
            400  # 初始高度
        )
        
        # 应用样式
        self.update_style()
    
    def update_style(self):
        """更新窗口样式"""
        # 设置窗口透明度
        self.setWindowOpacity(self.opacity)
        
        # 更新窗口样式表（主要是背景色）
        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)
    
    def paintEvent(self, event):
        """绘制窗口背景（半透明黑色背景）"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制半透明背景
        bg_color = QColor(30, 30, 35, int(230 * self.opacity))
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        
        # 绘制圆角矩形背景
        rect = self.rect()
        radius = 10
        painter.drawRoundedRect(rect, radius, radius)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            # 右键菜单
            self.show_context_menu(event.globalPos())
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()
    
    def on_title_mouse_press(self, event: QMouseEvent):
        """标题栏鼠标按下"""
        self.mousePressEvent(event)
    
    def on_title_mouse_move(self, event: QMouseEvent):
        """标题栏鼠标移动"""
        self.mouseMoveEvent(event)
    
    def on_title_mouse_release(self, event: QMouseEvent):
        """标题栏鼠标释放"""
        self.mouseReleaseEvent(event)
    
    def show_context_menu(self, pos):
        """显示右键菜单"""
        try:
            menu = QMenu(self)
            menu.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Popup)
            
            # 透明度调整
            opacity_menu = menu.addMenu("透明度")
            for op in [0.5, 0.6, 0.7, 0.85, 0.95, 1.0]:
                action = opacity_menu.addAction(f"{int(op * 100)}%")
                # 修复lambda闭包问题
                def make_opacity_setter(o):
                    return lambda checked: self.set_opacity(o)
                action.triggered.connect(make_opacity_setter(op))
                if abs(self.opacity - o) < 0.01:
                    action.setCheckable(True)
                    action.setChecked(True)
            
            menu.addSeparator()
            
            # 显示/隐藏已完成任务
            show_completed_action = menu.addAction("显示已完成任务")
            show_completed_action.setCheckable(True)
            show_completed_action.setChecked(self.show_completed)
            show_completed_action.triggered.connect(self.toggle_show_completed)
            
            menu.addSeparator()
            
            # 刷新任务
            refresh_action = menu.addAction("刷新任务")
            refresh_action.triggered.connect(self.load_tasks)
            
            menu.addSeparator()
            
            # 始终置顶
            pin_action = menu.addAction("始终置顶")
            pin_action.setCheckable(True)
            pin_action.setChecked(True)
            pin_action.triggered.connect(self.toggle_always_on_top)
            
            menu.addSeparator()
            
            # 关闭窗口
            close_action = menu.addAction("关闭窗口")
            close_action.triggered.connect(self.hide)
            
            menu.exec_(pos)
            
        except Exception as e:
            print(f"[透明任务窗口] 显示右键菜单失败: {e}")
            import traceback
            traceback.print_exc()
    
    def show_menu(self):
        """显示菜单按钮菜单"""
        try:
            # 获取按钮的全局位置
            global_pos = self.menu_btn.mapToGlobal(QPoint(0, self.menu_btn.height()))
            
            # 创建菜单，不设置特殊的WindowFlags，让Qt自动处理
            menu = QMenu(self)
            # 只设置置顶，不要设置FramelessWindowHint，这会导致崩溃
            menu.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Popup)
            
            # 透明度调整
            opacity_menu = menu.addMenu("透明度")
            for op in [0.5, 0.6, 0.7, 0.85, 0.95, 1.0]:
                action = opacity_menu.addAction(f"{int(op * 100)}%")
                # 修复lambda闭包问题
                def make_opacity_setter(o):
                    return lambda checked: self.set_opacity(o)
                action.triggered.connect(make_opacity_setter(op))
                if abs(self.opacity - o) < 0.01:
                    action.setCheckable(True)
                    action.setChecked(True)
            
            menu.addSeparator()
            
            # 显示/隐藏已完成任务
            show_completed_action = menu.addAction("显示已完成任务")
            show_completed_action.setCheckable(True)
            show_completed_action.setChecked(self.show_completed)
            show_completed_action.triggered.connect(self.toggle_show_completed)
            
            menu.addSeparator()
            
            # 刷新任务
            refresh_action = menu.addAction("刷新任务")
            refresh_action.triggered.connect(self.load_tasks)
            
            menu.addSeparator()
            
            # 始终置顶
            pin_action = menu.addAction("始终置顶")
            pin_action.setCheckable(True)
            pin_action.setChecked(True)
            pin_action.triggered.connect(self.toggle_always_on_top)
            
            menu.addSeparator()
            
            # 关闭窗口
            close_action = menu.addAction("关闭窗口")
            close_action.triggered.connect(self.hide)
            
            # 显示菜单
            menu.exec_(global_pos)
            
        except Exception as e:
            print(f"[透明任务窗口] 显示菜单失败: {e}")
            import traceback
            traceback.print_exc()
    
    def toggle_collapse(self):
        """折叠/展开窗口"""
        if not self.is_collapsed:
            # 折叠：只显示标题栏
            self.saved_height = self.height()
            self.is_collapsed = True
            self.scroll_area.setVisible(False)
            self.resize(self.width(), 35)
            self.collapse_btn.setText("◢")  # 改变按钮文本表示已折叠
        else:
            # 展开：恢复之前的高度
            self.is_collapsed = False
            self.scroll_area.setVisible(True)
            self.resize(self.width(), self.saved_height)
            self.collapse_btn.setText("=")  # 恢复按钮文本
    
    def toggle_always_on_top(self, checked: bool):
        """切换始终置顶"""
        if checked:
            self.setWindowFlags(
                self.windowFlags() | Qt.WindowStaysOnTopHint
            )
        else:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowStaysOnTopHint
            )
        self.show()
    
    def set_opacity(self, opacity: float):
        """设置窗口透明度"""
        self.opacity = max(0.1, min(1.0, opacity))
        self.setWindowOpacity(self.opacity)
        self.update()
    
    def show_add_task_dialog(self):
        """显示添加任务对话框"""
        if not self.database:
            return
        
        text, ok = QInputDialog.getText(
            self,
            "添加任务",
            "请输入任务标题：",
            flags=Qt.WindowStaysOnTopHint
        )
        
        if ok and text.strip():
            task_id = self.database.add_task(
                title=text.strip(),
                priority=2,  # 默认中等优先级
                category="一般"
            )
            
            if task_id > 0:
                # 刷新任务列表
                self.load_tasks()
    
    def load_tasks(self):
        """加载任务列表"""
        if not self.database:
            return
        
        try:
            # 获取所有未完成的任务
            self.tasks = self.database.get_all_tasks(status='pending')
            
            # 按优先级和截止日期排序
            self.tasks.sort(key=lambda x: (
                -x.get('priority', 1),  # 优先级降序（高优先级在前）
                x.get('due_date') or '9999-99-99'  # 截止日期升序
            ))
            
            # 获取所有已完成的任务
            self.completed_tasks = self.database.get_all_tasks(status='completed')
            
            # 按完成日期降序排序（最近完成的在前）
            self.completed_tasks.sort(key=lambda x: (
                x.get('completed_date') or x.get('updated_at') or '',
            ), reverse=True)
            
            # 更新UI
            self.update_task_list()
            
        except Exception as e:
            print(f"[透明任务窗口] 加载任务失败: {e}")
            import traceback
            traceback.print_exc()
    
    def update_task_list(self):
        """更新任务列表显示"""
        # 清除现有任务项
        while self.tasks_layout.count() > 1:  # 保留最后的stretch
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 更新标题
        task_count = len(self.tasks)
        completed_count = len(self.completed_tasks) if self.show_completed else 0
        total_text = f"事项清单 - 未完成 ({task_count})"
        if completed_count > 0:
            total_text += f" | 已完成 ({completed_count})"
        self.title_label.setText(total_text)
        
        # 添加未完成任务项
        if task_count > 0:
            # 未完成任务标题
            pending_label = QLabel("未完成")
            pending_label.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 12px;
                    font-weight: bold;
                    padding: 5px 0;
                    background: transparent;
                }
            """)
            self.tasks_layout.insertWidget(
                self.tasks_layout.count() - 1,
                pending_label
            )
            
            for task in self.tasks:
                task_widget = self.create_task_item(task, is_completed=False)
                self.tasks_layout.insertWidget(
                    self.tasks_layout.count() - 1,  # 在stretch之前插入
                    task_widget
                )
        else:
            # 如果没有未完成任务，显示提示
            empty_label = QLabel("暂无待办事项")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 0.5);
                    font-size: 13px;
                    padding: 20px;
                    background: transparent;
                }
            """)
            self.tasks_layout.insertWidget(
                self.tasks_layout.count() - 1,
                empty_label
            )
        
        # 添加已完成任务项（如果启用显示）
        if self.show_completed and len(self.completed_tasks) > 0:
            # 分隔线
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFixedHeight(1)
            separator.setStyleSheet("""
                QFrame {
                    background: rgba(255, 255, 255, 0.2);
                    border: none;
                }
            """)
            self.tasks_layout.insertWidget(
                self.tasks_layout.count() - 1,
                separator
            )
            
            # 已完成任务标题
            completed_label = QLabel("已完成")
            completed_label.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 12px;
                    font-weight: bold;
                    padding: 5px 0;
                    background: transparent;
                }
            """)
            self.tasks_layout.insertWidget(
                self.tasks_layout.count() - 1,
                completed_label
            )
            
            # 只显示最近10个已完成的任务
            for task in self.completed_tasks[:10]:
                task_widget = self.create_task_item(task, is_completed=True)
                self.tasks_layout.insertWidget(
                    self.tasks_layout.count() - 1,
                    task_widget
                )
        
        # 自动调整窗口高度（限制最大高度）
        task_item_height = 45  # 每个任务项的高度
        spacing = 6  # 任务项之间的间距
        header_height = 35  # 标题栏高度
        margins = 20  # 上下边距
        
        # 计算需要的总高度
        if task_count == 0:
            content_height = 60  # 空状态提示的高度
        else:
            content_height = task_count * (task_item_height + spacing) - spacing
        
        total_height = header_height + content_height + margins
        
        # 限制在最小和最大高度之间
        min_height = 100
        new_height = max(min_height, min(total_height, self.max_height))
        
        # 更新窗口大小（保持宽度不变）
        current_width = self.width()
        self.resize(current_width, new_height)
    
    def create_task_item(self, task: dict, is_completed: bool = False) -> QWidget:
        """创建单个任务项"""
        task_widget = QFrame()
        task_widget.setFrameShape(QFrame.NoFrame)
        
        # 根据是否有备注调整高度
        has_notes = task.get('notes') and task.get('notes').strip()
        task_widget.setFixedHeight(70 if has_notes else 45)
        
        # 设置样式
        if is_completed:
            bg_color = 'rgba(76, 175, 80, 0.2)'  # 已完成 - 绿色
            hover_bg = 'rgba(76, 175, 80, 0.3)'
        else:
            priority = task.get('priority', 1)
            priority_colors = {
                1: 'rgba(100, 149, 237, 0.3)',  # 低优先级 - 蓝色
                2: 'rgba(255, 193, 7, 0.3)',    # 中优先级 - 黄色
                3: 'rgba(255, 82, 82, 0.3)'     # 高优先级 - 红色
            }
            bg_color = priority_colors.get(priority, 'rgba(255, 255, 255, 0.1)')
            hover_bg = bg_color.replace('0.3', '0.5') if '0.3' in bg_color else 'rgba(255, 255, 255, 0.2)'
        
        task_widget.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            QFrame:hover {{
                background: {hover_bg};
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
        """)
        
        # 主布局（垂直布局以支持备注）
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(5)
        
        # 第一行：指示器、标题和日期
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)
        
        # 完成复选框或优先级指示器
        task_id = task['id']  # 保存task_id用于闭包
        
        if is_completed:
            # 已完成任务显示复选框（已选中，但可点击取消）
            complete_checkbox = QCheckBox()
            complete_checkbox.setChecked(True)
            complete_checkbox.setStyleSheet("""
                QCheckBox {
                    spacing: 0px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border: 2px solid rgba(76, 175, 80, 0.8);
                    border-radius: 4px;
                    background: rgba(76, 175, 80, 0.5);
                }
                QCheckBox::indicator:hover {
                    border: 2px solid rgba(76, 175, 80, 1.0);
                    background: rgba(76, 175, 80, 0.7);
                }
                QCheckBox::indicator:checked {
                    background: rgba(76, 175, 80, 0.9);
                    border: 2px solid rgba(76, 175, 80, 1.0);
                }
                QCheckBox::indicator:checked:hover {
                    background: rgba(76, 175, 80, 1.0);
                }
            """)
            # 连接复选框点击事件来取消完成
            def on_checkbox_uncomplete(checked):
                if not checked:  # 取消选中时
                    QTimer.singleShot(100, lambda: self.uncomplete_task(task_id))
            complete_checkbox.clicked.connect(on_checkbox_uncomplete)
            title_layout.addWidget(complete_checkbox)
            
            # 已完成任务不显示优先级指示器
        else:
            # 未完成任务显示可点击的复选框和优先级指示器
            # 复选框（用于标记完成）
            complete_checkbox = QCheckBox()
            complete_checkbox.setChecked(False)
            complete_checkbox.setStyleSheet("""
                QCheckBox {
                    spacing: 0px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border: 2px solid rgba(255, 255, 255, 0.6);
                    border-radius: 4px;
                    background: rgba(255, 255, 255, 0.05);
                }
                QCheckBox::indicator:hover {
                    border: 2px solid rgba(255, 255, 255, 0.9);
                    background: rgba(255, 255, 255, 0.15);
                }
                QCheckBox::indicator:checked {
                    background: rgba(76, 175, 80, 0.9);
                    border: 2px solid rgba(76, 175, 80, 1.0);
                }
                QCheckBox::indicator:checked:hover {
                    background: rgba(76, 175, 80, 1.0);
                }
            """)
            # 连接复选框点击事件来标记完成
            task_id = task['id']  # 保存task_id用于闭包
            def on_checkbox_clicked(checked):
                if checked:
                    # 使用QTimer延迟执行，避免在事件处理中直接操作
                    QTimer.singleShot(100, lambda: self.complete_task(task_id))
            complete_checkbox.clicked.connect(on_checkbox_clicked)
            title_layout.addWidget(complete_checkbox)
            
            # 优先级指示器（小圆点）
            priority_indicator = QLabel("•")
            priority_val = task.get('priority', 1)
            priority_colors_indicator = {
                1: 'rgba(100, 149, 237, 1.0)',  # 低优先级 - 蓝色
                2: 'rgba(255, 193, 7, 1.0)',    # 中优先级 - 黄色
                3: 'rgba(255, 82, 82, 1.0)'     # 高优先级 - 红色
            }
            indicator_color = priority_colors_indicator.get(priority_val, 'rgba(255, 255, 255, 1.0)')
            priority_indicator.setStyleSheet(f"""
                QLabel {{
                    color: {indicator_color};
                    font-size: 12px;
                    font-weight: bold;
                    background: transparent;
                }}
            """)
            title_layout.addWidget(priority_indicator)
        
        # 任务标题
        title_text = task.get('title', '无标题')
        # 限制显示长度
        if len(title_text) > 30:
            title_text = title_text[:30] + "..."
        
        title_label = QLabel(title_text)
        title_style = """
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 13px;
                background: transparent;
            }
        """
        if is_completed:
            title_style = """
            QLabel {
                color: rgba(255, 255, 255, 0.6);
                font-size: 13px;
                text-decoration: line-through;
                background: transparent;
            }
        """
        title_label.setStyleSheet(title_style)
        title_layout.addWidget(title_label, 1)
        
        # 截止日期（如果有且未完成）
        due_date = task.get('due_date')
        if due_date and not is_completed:
            try:
                date_obj = datetime.strptime(due_date.split()[0], "%Y-%m-%d")
                today = datetime.now().date()
                task_date = date_obj.date()
                
                days_diff = (task_date - today).days
                if days_diff < 0:
                    date_text = f"已过期 {abs(days_diff)}天"
                    date_color = "rgba(255, 82, 82, 0.9)"
                elif days_diff == 0:
                    date_text = "今天"
                    date_color = "rgba(255, 193, 7, 0.9)"
                elif days_diff == 1:
                    date_text = "明天"
                    date_color = "rgba(255, 193, 7, 0.8)"
                else:
                    date_text = f"{days_diff}天后"
                    date_color = "rgba(255, 255, 255, 0.6)"
                
                date_label = QLabel(date_text)
                date_label.setStyleSheet(f"""
                    QLabel {{
                        color: {date_color};
                        font-size: 11px;
                        background: transparent;
                    }}
                """)
                title_layout.addWidget(date_label)
            except:
                pass
        
        main_layout.addLayout(title_layout)
        
        # 备注显示（如果有）
        if has_notes:
            notes_text = task.get('notes', '').strip()
            if len(notes_text) > 40:
                notes_text = notes_text[:40] + "..."
            notes_label = QLabel(notes_text)
            notes_label.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 11px;
                    font-style: italic;
                    padding-left: 26px;
                    background: transparent;
                }
            """)
            notes_label.setWordWrap(True)
            main_layout.addWidget(notes_label)
        
        task_widget.setLayout(main_layout)
        
        # 点击事件
        task_id = task['id']  # 保存任务ID用于闭包
        
        def on_click(event):
            if event.button() == Qt.LeftButton:
                self.task_clicked.emit(task_id)
            elif event.button() == Qt.RightButton:
                self.show_task_menu(task, event.globalPos(), is_completed)
        
        def on_double_click(event):
            if event.button() == Qt.LeftButton:
                self.task_double_clicked.emit(task_id)
        
        task_widget.mousePressEvent = on_click
        task_widget.mouseDoubleClickEvent = on_double_click
        
        return task_widget
    
    def show_task_menu(self, task: dict, pos, is_completed: bool = False):
        """显示任务右键菜单"""
        try:
            menu = QMenu(self)
            # 只设置置顶，不要设置FramelessWindowHint
            menu.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Popup)
            task_id = task['id']
            
            if not is_completed:
                # 未完成任务菜单
                complete_action = menu.addAction("✓ 标记为完成")
                complete_action.triggered.connect(lambda checked, tid=task_id: self.complete_task(tid))
                menu.addSeparator()
            else:
                # 已完成任务菜单
                uncomplete_action = menu.addAction("↶ 取消完成")
                uncomplete_action.triggered.connect(lambda checked, tid=task_id: self.uncomplete_task(tid))
                menu.addSeparator()
            
            # 添加/编辑备注
            note_text = "编辑备注" if task.get('notes') else "添加备注"
            note_action = menu.addAction(f"📝 {note_text}")
            note_action.triggered.connect(lambda checked, tid=task_id, t=task: self.edit_task_notes(tid, t))
            
            menu.addSeparator()
            
            # 删除任务
            delete_action = menu.addAction("🗑 删除任务")
            delete_action.triggered.connect(lambda checked, tid=task_id: self.delete_task(tid))
            
            menu.exec_(pos)
            
        except Exception as e:
            print(f"[透明任务窗口] 显示任务菜单失败: {e}")
            import traceback
            traceback.print_exc()
    
    def toggle_show_completed(self, checked: bool):
        """切换显示已完成任务"""
        self.show_completed = checked
        self.load_tasks()
    
    def complete_task(self, task_id: int):
        """完成任务"""
        if self.database:
            # 使用update_task来标记完成，并设置完成日期
            from datetime import datetime
            completed_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.database.update_task(task_id, status='completed', completed_date=completed_date)
            self.load_tasks()
            QApplication.processEvents()
    
    def uncomplete_task(self, task_id: int):
        """取消完成，恢复为未完成状态"""
        if self.database:
            # 将任务状态改回pending，并清空完成日期
            self.database.update_task(task_id, status='pending', completed_date=None)
            self.load_tasks()
            QApplication.processEvents()
    
    def edit_task_notes(self, task_id: int, task: dict):
        """编辑任务备注"""
        from PyQt5.QtWidgets import QTextEdit, QDialog, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑备注")
        dialog.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        dialog.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        notes_edit = QTextEdit()
        notes_edit.setPlaceholderText("输入任务备注...")
        notes_edit.setPlainText(task.get('notes', ''))
        notes_edit.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                color: rgba(255, 255, 255, 0.9);
                padding: 8px;
            }
        """)
        layout.addWidget(notes_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            notes_text = notes_edit.toPlainText().strip()
            if self.database:
                self.database.update_task(task_id, notes=notes_text)
                self.load_tasks()
    
    def delete_task(self, task_id: int):
        """删除任务"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个任务吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
            flags=Qt.WindowStaysOnTopHint
        )
        
        if reply == QMessageBox.Yes and self.database:
            self.database.delete_task(task_id)
            self.load_tasks()
            QApplication.processEvents()
    
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        # 显示时刷新任务
        self.load_tasks()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止定时器
        if self.refresh_timer:
            self.refresh_timer.stop()
        event.accept()

