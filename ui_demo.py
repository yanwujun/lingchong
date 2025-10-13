#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
界面风格演示程序
UI Style Demo - 展示不同的现代化界面风格
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# 导入不同的UI风格
from src.modern_ui import ModernWindow, ModernButton, ModernCard, ModernInput
from src.fluent_ui import FluentAcrylicWindow, FluentButton, FluentCard, FluentInput
from src.neumorphism_ui import NeumorphismWindow, NeumorphismButton, NeumorphismCard, NeumorphismInput

class UIDemoWindow(QWidget):
    """界面演示主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎨 界面风格演示 - 桌面灵宠")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("🎨 桌面灵宠 - 现代化界面升级方案")
        title_label.setFont(QFont("", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #333; margin: 20px 0;")
        layout.addWidget(title_label)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # Material Design风格
        material_tab = self.create_material_demo()
        tab_widget.addTab(material_tab, "🎨 Material Design")
        
        # Fluent Design风格
        fluent_tab = self.create_fluent_demo()
        tab_widget.addTab(fluent_tab, "💎 Fluent Design")
        
        # Neumorphism风格
        neumorphism_tab = self.create_neumorphism_demo()
        tab_widget.addTab(neumorphism_tab, "🌟 Neumorphism")
        
        layout.addWidget(tab_widget)
        
        # 底部说明
        info_label = QLabel("""
        <h3>界面升级说明：</h3>
        <p><b>Material Design:</b> Google设计语言，简洁现代，适合移动端和桌面端</p>
        <p><b>Fluent Design:</b> 微软设计语言，毛玻璃效果，适合Windows 11风格</p>
        <p><b>Neumorphism:</b> 新拟物化设计，柔和阴影，适合现代简约风格</p>
        """)
        info_label.setStyleSheet("background-color: #F5F5F5; padding: 15px; border-radius: 8px; margin: 10px 0;")
        layout.addWidget(info_label)
        
        self.setLayout(layout)
    
    def create_material_demo(self):
        """创建Material Design演示"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # 卡片示例
        card = ModernCard()
        card_layout = QVBoxLayout(card)
        
        card_title = QLabel("📱 Material Design 风格")
        card_title.setFont(QFont("", 18, QFont.Bold))
        card_layout.addWidget(card_title)
        
        # 输入框示例
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("任务名称:"))
        task_input = ModernInput("输入新的待办任务...")
        input_layout.addWidget(task_input)
        card_layout.addLayout(input_layout)
        
        # 按钮示例
        button_layout = QHBoxLayout()
        add_btn = ModernButton("添加任务", style="primary")
        cancel_btn = ModernButton("取消", style="secondary")
        button_layout.addWidget(add_btn)
        button_layout.addWidget(cancel_btn)
        card_layout.addLayout(button_layout)
        
        layout.addWidget(card)
        
        # 特点说明
        features_label = QLabel("""
        <h4>Material Design 特点：</h4>
        <ul>
        <li>🎯 简洁明快的设计语言</li>
        <li>🌈 丰富的色彩搭配</li>
        <li>📱 响应式交互设计</li>
        <li>✨ 流畅的动画效果</li>
        </ul>
        """)
        features_label.setStyleSheet("background-color: #E3F2FD; padding: 15px; border-radius: 8px;")
        layout.addWidget(features_label)
        
        layout.addStretch()
        return widget
    
    def create_fluent_demo(self):
        """创建Fluent Design演示"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # 卡片示例
        card = FluentCard()
        card_layout = QVBoxLayout(card)
        
        card_title = QLabel("💎 Fluent Design 风格")
        card_title.setFont(QFont("", 18, QFont.Bold))
        card_layout.addWidget(card_title)
        
        # 输入框示例
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("任务名称:"))
        task_input = FluentInput("输入新的待办任务...")
        input_layout.addWidget(task_input)
        card_layout.addLayout(input_layout)
        
        # 按钮示例
        button_layout = QHBoxLayout()
        add_btn = FluentButton("添加任务", style="primary")
        cancel_btn = FluentButton("取消", style="secondary")
        button_layout.addWidget(add_btn)
        button_layout.addWidget(cancel_btn)
        card_layout.addLayout(button_layout)
        
        layout.addWidget(card)
        
        # 特点说明
        features_label = QLabel("""
        <h4>Fluent Design 特点：</h4>
        <ul>
        <li>🔮 毛玻璃透明效果</li>
        <li>🎨 微软现代设计语言</li>
        <li>💫 优雅的视觉层次</li>
        <li>🪟 完美适配Windows 11</li>
        </ul>
        """)
        features_label.setStyleSheet("background-color: rgba(0, 120, 212, 0.1); padding: 15px; border-radius: 8px;")
        layout.addWidget(features_label)
        
        layout.addStretch()
        return widget
    
    def create_neumorphism_demo(self):
        """创建Neumorphism演示"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # 卡片示例
        card = NeumorphismCard()
        card_layout = QVBoxLayout(card)
        
        card_title = QLabel("🌟 Neumorphism 风格")
        card_title.setFont(QFont("", 18, QFont.Bold))
        card_layout.addWidget(card_title)
        
        # 输入框示例
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("任务名称:"))
        task_input = NeumorphismInput("输入新的待办任务...")
        input_layout.addWidget(task_input)
        card_layout.addLayout(input_layout)
        
        # 按钮示例
        button_layout = QHBoxLayout()
        add_btn = NeumorphismButton("添加任务", style="primary")
        cancel_btn = NeumorphismButton("取消", style="primary")
        button_layout.addWidget(add_btn)
        button_layout.addWidget(cancel_btn)
        card_layout.addLayout(button_layout)
        
        layout.addWidget(card)
        
        # 特点说明
        features_label = QLabel("""
        <h4>Neumorphism 特点：</h4>
        <ul>
        <li>🎭 新拟物化设计风格</li>
        <li>🌙 柔和的阴影效果</li>
        <li>🎨 低对比度配色</li>
        <li>👆 舒适的触觉反馈</li>
        </ul>
        """)
        features_label.setStyleSheet("background-color: #F0F0F0; padding: 15px; border-radius: 20px;")
        layout.addWidget(features_label)
        
        layout.addStretch()
        return widget

def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建演示窗口
    demo = UIDemoWindow()
    demo.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
