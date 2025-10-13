#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fluent Design UI模块
Fluent Design UI Module - 提供微软Fluent Design风格的现代化界面
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

class FluentCard(QFrame):
    """Fluent Design卡片组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            FluentCard {
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                padding: 16px;
                backdrop-filter: blur(20px);
            }
            FluentCard:hover {
                background-color: rgba(255, 255, 255, 0.9);
                border-color: rgba(0, 120, 212, 0.3);
            }
        """)

class FluentButton(QPushButton):
    """Fluent Design按钮组件"""
    
    def __init__(self, text="", parent=None, style="primary"):
        super().__init__(text, parent)
        self.style_type = style
        self.setMinimumHeight(32)
        self.setCursor(Qt.PointingHandCursor)
        self.apply_style()
    
    def apply_style(self):
        if self.style_type == "primary":
            self.setStyleSheet("""
                FluentButton {
                    background-color: #0078D4;
                    color: white;
                    border: none;
                    border-radius: 2px;
                    padding: 8px 16px;
                    font-weight: 400;
                    font-size: 14px;
                }
                FluentButton:hover {
                    background-color: #106EBE;
                }
                FluentButton:pressed {
                    background-color: #005A9E;
                }
            """)
        elif self.style_type == "secondary":
            self.setStyleSheet("""
                FluentButton {
                    background-color: transparent;
                    color: #0078D4;
                    border: 1px solid #0078D4;
                    border-radius: 2px;
                    padding: 8px 16px;
                    font-weight: 400;
                    font-size: 14px;
                }
                FluentButton:hover {
                    background-color: rgba(0, 120, 212, 0.1);
                }
            """)

class FluentInput(QLineEdit):
    """Fluent Design输入框组件"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(32)
        self.setStyleSheet("""
            FluentInput {
                border: 1px solid #8A8886;
                border-radius: 2px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            FluentInput:focus {
                border-color: #0078D4;
                outline: none;
            }
            FluentInput:hover {
                border-color: #323130;
            }
        """)

class FluentProgressBar(QProgressBar):
    """Fluent Design进度条组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(4)
        self.setTextVisible(False)
        self.setStyleSheet("""
            FluentProgressBar {
                border: none;
                border-radius: 2px;
                background-color: #E1DFDD;
            }
            FluentProgressBar::chunk {
                background-color: #0078D4;
                border-radius: 2px;
            }
        """)

class FluentAcrylicWindow(QWidget):
    """Fluent Design毛玻璃窗口"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("""
            FluentAcrylicWindow {
                background-color: rgba(243, 242, 241, 0.8);
                backdrop-filter: blur(20px);
                color: #323130;
            }
        """)

class FluentPetWindow(FluentAcrylicWindow):
    """Fluent Design宠物窗口"""
    
    def __init__(self, parent=None):
        super().__init__("🐱 桌面宠物", parent)
        self.setFixedSize(320, 420)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 宠物卡片
        pet_card = FluentCard()
        pet_layout = QVBoxLayout(pet_card)
        
        # 宠物头像
        self.pet_label = QLabel("🐱")
        self.pet_label.setFont(QFont("Segoe UI Emoji", 72))
        self.pet_label.setAlignment(Qt.AlignCenter)
        pet_layout.addWidget(self.pet_label)
        
        # 宠物信息
        info_layout = QVBoxLayout()
        
        # 宠物名称
        name_label = QLabel("小宠物")
        name_label.setFont(QFont("Segoe UI", 18, QFont.Medium))
        name_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(name_label)
        
        # 等级和经验
        level_layout = QHBoxLayout()
        level_label = QLabel("Level 5")
        level_label.setStyleSheet("color: #D83B01; font-weight: 600;")
        level_layout.addWidget(level_label)
        
        # 经验条
        self.exp_bar = FluentProgressBar()
        self.exp_bar.setValue(65)
        level_layout.addWidget(self.exp_bar)
        
        info_layout.addLayout(level_layout)
        pet_layout.addLayout(info_layout)
        
        layout.addWidget(pet_card)
        self.setLayout(layout)

# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 测试Fluent Design窗口
    window = FluentPetWindow()
    window.show()
    
    sys.exit(app.exec_())
