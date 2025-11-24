#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
现代化UI设计模块
Modern UI Module - 提供Material Design风格的现代化界面
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

# 现代化浅色主题颜色常量（类似 Clash Verge/Notion 风格）
COLORS = {
    'background': '#ffffff',     # 主背景色（白色）
    'surface': '#f5f5f5',        # 次要背景色（浅灰）
    'primary': '#6366f1',        # 主色调（紫蓝色）
    'primary_dark': '#4f46e5',   # 深色主色调
    'primary_light': '#e0e7ff',  # 浅色主色调（用于hover）
    'accent': '#ec4899',         # 强调色（粉红）
    'text_primary': '#333333',   # 主要文本（深灰）
    'text_secondary': '#666666',  # 次要文本（中灰）
    'border': '#e0e0e0',         # 边框色
    'divider': '#e0e0e0',        # 分割线
    'hover': '#f5f5f5',          # hover背景色
    'selected': '#e3f2fd',       # 选中背景色
    'error': '#f44336',          # 错误色
    'success': '#4caf50',        # 成功色
    'warning': '#ff9800',        # 警告色
    'info': '#2196f3',           # 信息色
    # 保留旧字段以兼容性
    'shadow_dark': '#e0e0e0',    # 不再使用阴影，改为边框色
    'shadow_light': '#ffffff',   # 不再使用阴影
}

class ModernCard(QFrame):
    """现代化卡片组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            ModernCard {{
                background-color: {COLORS['background']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 20px;
            }}
        """)

class ModernButton(QPushButton):
    """现代化按钮组件"""
    
    def __init__(self, text="", parent=None, style="primary"):
        super().__init__(text, parent)
        self.style_type = style
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.apply_style()
        # 添加点击动画效果
        self.pressed.connect(self._on_pressed)
        self.released.connect(self._on_released)
    
    def _on_pressed(self):
        """按下时的动画效果"""
        from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(100)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        current_rect = self.geometry()
        self.animation.setStartValue(current_rect)
        # 轻微缩小
        self.animation.setEndValue(current_rect.adjusted(1, 1, -1, -1))
        self.animation.start()
    
    def _on_released(self):
        """释放时的动画效果"""
        if hasattr(self, 'animation'):
            from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(100)
            self.animation.setEasingCurve(QEasingCurve.OutCubic)
            current_rect = self.geometry()
            self.animation.setStartValue(current_rect)
            # 恢复原大小
            self.animation.setEndValue(current_rect.adjusted(-1, -1, 1, 1))
            self.animation.start()
    
    def apply_style(self):
        if self.style_type == "primary":
            self.setStyleSheet(f"""
                ModernButton {{
                    background: {COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-weight: 600;
                    font-size: 14px;
                }}
                ModernButton:hover {{
                    background: {COLORS['primary_dark']};
                }}
                ModernButton:pressed {{
                    background: {COLORS['primary_dark']};
                    opacity: 0.9;
                }}
            """)
        elif self.style_type == "secondary":
            self.setStyleSheet(f"""
                ModernButton {{
                    background: {COLORS['surface']};
                    color: {COLORS['text_primary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-weight: 500;
                    font-size: 14px;
                }}
                ModernButton:hover {{
                    background: {COLORS['hover']};
                    border-color: {COLORS['primary']};
                }}
                ModernButton:pressed {{
                    background: {COLORS['border']};
                }}
            """)

class ModernInput(QLineEdit):
    """现代化输入框组件"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            ModernInput {{
                background: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            ModernInput:focus {{
                border: 2px solid {COLORS['primary']};
                outline: none;
            }}
            ModernInput:hover {{
                border-color: {COLORS['primary_light']};
            }}
        """)

class ModernComboBox(QComboBox):
    """现代化下拉框组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            ModernComboBox {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                background-color: {COLORS['background']};
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            ModernComboBox:focus {{
                border: 2px solid {COLORS['primary']};
                outline: none;
            }}
            ModernComboBox:hover {{
                border-color: {COLORS['primary_light']};
            }}
            ModernComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            ModernComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS['text_secondary']};
                margin-right: 8px;
            }}
            ModernComboBox QAbstractItemView {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                selection-background-color: {COLORS['selected']};
                selection-color: {COLORS['primary']};
            }}
        """)

class ModernProgressBar(QProgressBar):
    """现代化进度条组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(8)
        self.setTextVisible(False)
        self.setStyleSheet("""
            ModernProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #E0E0E0;
            }
            ModernProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
        """)

class ModernTabWidget(QTabWidget):
    """现代化标签页组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ModernTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background-color: {COLORS['background']};
                top: -1px;
            }}
            ModernTabWidget::tab-bar {{
                alignment: left;
            }}
            ModernTabWidget::tab {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_secondary']};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: none;
            }}
            ModernTabWidget::tab:selected {{
                background-color: {COLORS['background']};
                color: {COLORS['primary']};
                border-bottom: 2px solid {COLORS['primary']};
                font-weight: 600;
            }}
            ModernTabWidget::tab:hover {{
                background-color: {COLORS['hover']};
                color: {COLORS['text_primary']};
            }}
        """)

class ModernWindow(QWidget):
    """现代化窗口基类"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet("""
            ModernWindow {
                background-color: #FAFAFA;
                color: #333;
            }
        """)

class ModernPetWindow(ModernWindow):
    """现代化宠物窗口"""
    
    def __init__(self, parent=None):
        super().__init__("🐱 桌面宠物", parent)
        self.setFixedSize(300, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 宠物卡片
        pet_card = ModernCard()
        pet_layout = QVBoxLayout(pet_card)
        
        # 宠物头像
        self.pet_label = QLabel("🐱")
        self.pet_label.setFont(QFont("", 64))
        self.pet_label.setAlignment(Qt.AlignCenter)
        pet_layout.addWidget(self.pet_label)
        
        # 宠物信息
        info_layout = QVBoxLayout()
        
        # 宠物名称
        name_label = QLabel("小宠物")
        name_label.setFont(QFont("", 16, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(name_label)
        
        # 等级和经验
        level_layout = QHBoxLayout()
        level_label = QLabel("Lv.5")
        level_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        level_layout.addWidget(level_label)
        
        # 经验条
        self.exp_bar = ModernProgressBar()
        self.exp_bar.setValue(65)
        level_layout.addWidget(self.exp_bar)
        
        info_layout.addLayout(level_layout)
        pet_layout.addLayout(info_layout)
        
        layout.addWidget(pet_card)
        self.setLayout(layout)

class ModernTodoWindow(ModernWindow):
    """现代化待办窗口"""
    
    def __init__(self, parent=None):
        super().__init__("📝 待办事项", parent)
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题栏
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📝 我的任务")
        title_label.setFont(QFont("", 24, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 添加任务按钮
        add_btn = ModernButton("+ 添加任务", style="primary")
        add_btn.clicked.connect(self.add_task)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # 任务列表卡片
        tasks_card = ModernCard()
        tasks_layout = QVBoxLayout(tasks_card)
        
        # 任务表格
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(5)
        self.tasks_table.setHorizontalHeaderLabels(["任务", "优先级", "截止时间", "状态", "操作"])
        self.tasks_table.horizontalHeader().setStretchLastSection(True)
        self.tasks_table.setAlternatingRowColors(True)
        self.tasks_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
            }
        """)
        
        tasks_layout.addWidget(self.tasks_table)
        layout.addWidget(tasks_card)
        
        self.setLayout(layout)
    
    def add_task(self):
        # 添加任务逻辑
        pass

class ModernSettingsWindow(ModernWindow):
    """现代化设置窗口"""
    
    def __init__(self, parent=None):
        super().__init__("⚙️ 设置", parent)
        self.setGeometry(100, 100, 700, 500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("⚙️ 应用设置")
        title_label.setFont(QFont("", 24, QFont.Bold))
        layout.addWidget(title_label)
        
        # 设置标签页
        self.tabs = ModernTabWidget()
        
        # 宠物设置
        pet_tab = self.create_pet_settings()
        self.tabs.addTab(pet_tab, "🐱 宠物")
        
        # 界面设置
        ui_tab = self.create_ui_settings()
        self.tabs.addTab(ui_tab, "🎨 界面")
        
        # 系统设置
        system_tab = self.create_system_settings()
        self.tabs.addTab(system_tab, "🔧 系统")
        
        layout.addWidget(self.tabs)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = ModernButton("💾 保存", style="primary")
        reset_btn = ModernButton("🔄 重置", style="secondary")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(reset_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_pet_settings(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 宠物外观卡片
        appearance_card = ModernCard()
        appearance_layout = QVBoxLayout(appearance_card)
        
        appearance_title = QLabel("外观设置")
        appearance_title.setFont(QFont("", 16, QFont.Bold))
        appearance_layout.addWidget(appearance_title)
        
        # 宠物大小
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("宠物大小:"))
        
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(50, 200)
        self.size_slider.setValue(100)
        size_layout.addWidget(self.size_slider)
        
        appearance_layout.addLayout(size_layout)
        layout.addWidget(appearance_card)
        
        return widget
    
    def create_ui_settings(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 主题设置卡片
        theme_card = ModernCard()
        theme_layout = QVBoxLayout(theme_card)
        
        theme_title = QLabel("主题设置")
        theme_title.setFont(QFont("", 16, QFont.Bold))
        theme_layout.addWidget(theme_title)
        
        # 主题选择
        theme_layout.addWidget(QLabel("选择主题:"))
        self.theme_combo = ModernComboBox()
        self.theme_combo.addItems(["浅色主题", "深色主题", "跟随系统"])
        theme_layout.addWidget(self.theme_combo)
        
        layout.addWidget(theme_card)
        return widget
    
    def create_system_settings(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 系统设置卡片
        system_card = ModernCard()
        system_layout = QVBoxLayout(system_card)
        
        system_title = QLabel("系统设置")
        system_title.setFont(QFont("", 16, QFont.Bold))
        system_layout.addWidget(system_title)
        
        # 开机自启
        self.auto_start_check = QCheckBox("开机自动启动")
        system_layout.addWidget(self.auto_start_check)
        
        # 最小化到托盘
        self.tray_minimize_check = QCheckBox("最小化到系统托盘")
        system_layout.addWidget(self.tray_minimize_check)
        
        layout.addWidget(system_card)
        return widget

class ModernTableWidget(QTableWidget):
    """现代化表格组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ModernTableWidget {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                gridline-color: {COLORS['divider']};
                selection-background-color: {COLORS['selected']};
                alternate-background-color: {COLORS['surface']};
            }}
            ModernTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {COLORS['divider']};
            }}
            ModernTableWidget::item:selected {{
                background-color: {COLORS['selected']};
                color: {COLORS['primary']};
            }}
            ModernTableWidget::item:hover {{
                background-color: {COLORS['hover']};
            }}
            ModernTableWidget QHeaderView::section {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: none;
                border-bottom: 2px solid {COLORS['divider']};
                padding: 12px;
                font-weight: 600;
            }}
        """)

class ModernListWidget(QListWidget):
    """现代化列表组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ModernListWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['divider']};
                border-radius: 8px;
                selection-background-color: {COLORS['primary_light']};
                alternate-background-color: #F8F9FA;
            }}
            ModernListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }}
            ModernListWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary_dark']};
            }}
        """)

class ModernTextEdit(QTextEdit):
    """现代化文本编辑组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ModernTextEdit {{
                background: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            ModernTextEdit:focus {{
                border: 2px solid {COLORS['primary']};
                outline: none;
            }}
            ModernTextEdit:hover {{
                border-color: {COLORS['primary_light']};
            }}
        """)

class ModernSlider(QSlider):
    """现代化滑块组件"""
    
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setStyleSheet(f"""
            ModernSlider::groove:horizontal {{
                border: none;
                height: 10px;
                background: {COLORS['surface']};
                border-radius: 5px;
                box-shadow: inset 2px 2px 4px {COLORS['shadow_dark']}, 
                           inset -2px -2px 4px {COLORS['shadow_light']};
            }}
            ModernSlider::handle:horizontal {{
                background: {COLORS['primary']};
                border: none;
                width: 24px;
                height: 24px;
                border-radius: 12px;
                margin: -7px 0;
                box-shadow: 3px 3px 6px {COLORS['shadow_dark']}, 
                           -3px -3px 6px {COLORS['shadow_light']};
            }}
            ModernSlider::handle:horizontal:hover {{
                background: {COLORS['primary_dark']};
            }}
            ModernSlider::handle:horizontal:pressed {{
                box-shadow: inset 2px 2px 4px {COLORS['shadow_dark']};
            }}
        """)

class ModernCheckBox(QCheckBox):
    """现代化复选框组件"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            ModernCheckBox {{
                color: {COLORS['text_primary']};
                font-size: 14px;
                spacing: 10px;
            }}
            ModernCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                background: {COLORS['background']};
            }}
            ModernCheckBox::indicator:hover {{
                border-color: {COLORS['primary']};
            }}
            ModernCheckBox::indicator:checked {{
                background: {COLORS['primary']};
                border-color: {COLORS['primary']};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }}
        """)

class ModernSpinBox(QSpinBox):
    """现代化数字输入框组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ModernSpinBox {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['divider']};
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            ModernSpinBox:focus {{
                border-color: {COLORS['primary']};
                outline: none;
            }}
            ModernSpinBox::up-button {{
                background-color: {COLORS['primary']};
                border: none;
                border-radius: 3px;
                width: 20px;
            }}
            ModernSpinBox::down-button {{
                background-color: {COLORS['primary']};
                border: none;
                border-radius: 3px;
                width: 20px;
            }}
        """)

# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 测试现代化窗口
    window = ModernSettingsWindow()
    window.show()
    
    sys.exit(app.exec_())
