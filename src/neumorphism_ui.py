#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Neumorphism UI模块
Neumorphism UI Module - 提供新拟物化风格的现代化界面
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

class NeumorphismCard(QFrame):
    """新拟物化卡片组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            NeumorphismCard {
                background-color: #E6E6E6;
                border-radius: 20px;
                padding: 20px;
            }
            NeumorphismCard:hover {
                background-color: #F0F0F0;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(8)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

class NeumorphismButton(QPushButton):
    """新拟物化按钮组件"""
    
    def __init__(self, text="", parent=None, style="primary"):
        super().__init__(text, parent)
        self.style_type = style
        self.setMinimumHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.apply_style()
    
    def apply_style(self):
        if self.style_type == "primary":
            self.setStyleSheet("""
                NeumorphismButton {
                    background-color: #E6E6E6;
                    color: #333;
                    border: none;
                    border-radius: 15px;
                    padding: 12px 24px;
                    font-weight: 600;
                    font-size: 16px;
                }
                NeumorphismButton:hover {
                    background-color: #F0F0F0;
                }
                NeumorphismButton:pressed {
                    background-color: #DCDCDC;
                }
            """)
        
        # 添加内阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(5)
        shadow.setYOffset(5)
        shadow.setColor(QColor(255, 255, 255, 100))
        self.setGraphicsEffect(shadow)

class NeumorphismInput(QLineEdit):
    """新拟物化输入框组件"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(50)
        self.setStyleSheet("""
            NeumorphismInput {
                background-color: #E6E6E6;
                color: #333;
                border: none;
                border-radius: 15px;
                padding: 12px 20px;
                font-size: 16px;
            }
            NeumorphismInput:focus {
                background-color: #F0F0F0;
                outline: none;
            }
        """)
        
        # 添加内阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(3)
        shadow.setYOffset(3)
        shadow.setColor(QColor(255, 255, 255, 80))
        self.setGraphicsEffect(shadow)

class NeumorphismProgressBar(QProgressBar):
    """新拟物化进度条组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(20)
        self.setTextVisible(False)
        self.setStyleSheet("""
            NeumorphismProgressBar {
                background-color: #E6E6E6;
                border: none;
                border-radius: 10px;
            }
            NeumorphismProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 10px;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

class NeumorphismWindow(QWidget):
    """新拟物化窗口基类"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet("""
            NeumorphismWindow {
                background-color: #E6E6E6;
                color: #333;
            }
        """)

class NeumorphismPetWindow(NeumorphismWindow):
    """新拟物化宠物窗口"""
    
    def __init__(self, parent=None):
        super().__init__("🐱 桌面宠物", parent)
        self.setFixedSize(350, 450)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 宠物卡片
        pet_card = NeumorphismCard()
        pet_layout = QVBoxLayout(pet_card)
        
        # 宠物头像
        self.pet_label = QLabel("🐱")
        self.pet_label.setFont(QFont("", 80))
        self.pet_label.setAlignment(Qt.AlignCenter)
        pet_layout.addWidget(self.pet_label)
        
        # 宠物信息
        info_layout = QVBoxLayout()
        
        # 宠物名称
        name_label = QLabel("小宠物")
        name_label.setFont(QFont("", 20, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("color: #333; margin: 10px 0;")
        info_layout.addWidget(name_label)
        
        # 等级和经验
        level_layout = QVBoxLayout()
        
        level_label = QLabel("Level 5")
        level_label.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 16px;")
        level_label.setAlignment(Qt.AlignCenter)
        level_layout.addWidget(level_label)
        
        # 经验条
        self.exp_bar = NeumorphismProgressBar()
        self.exp_bar.setValue(65)
        level_layout.addWidget(self.exp_bar)
        
        info_layout.addLayout(level_layout)
        pet_layout.addLayout(info_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        feed_btn = NeumorphismButton("🍖 喂食")
        play_btn = NeumorphismButton("🎮 玩耍")
        
        button_layout.addWidget(feed_btn)
        button_layout.addWidget(play_btn)
        
        pet_layout.addLayout(button_layout)
        layout.addWidget(pet_card)
        self.setLayout(layout)

# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 测试新拟物化窗口
    window = NeumorphismPetWindow()
    window.show()
    
    sys.exit(app.exec_())
