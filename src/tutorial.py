#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
新手引导模块
Tutorial Module - 负责首次启动时的新手引导
"""

import sys
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QStackedWidget,
                             QApplication, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap


class TutorialWindow(QDialog):
    """新手引导窗口"""
    
    def __init__(self, database=None, parent=None):
        super().__init__(parent)
        self.database = database
        self.current_page = 0
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("🎓 欢迎使用桌面灵宠")
        self.setFixedSize(600, 450)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = QLabel("欢迎使用桌面灵宠！")
        title_label.setFont(QFont("", 22, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 页面容器
        self.pages_widget = QStackedWidget()
        
        # 创建各个页面
        self.pages_widget.addWidget(self.create_welcome_page())
        self.pages_widget.addWidget(self.create_features_page())
        self.pages_widget.addWidget(self.create_shortcuts_page())
        self.pages_widget.addWidget(self.create_final_page())
        
        layout.addWidget(self.pages_widget)
        
        # 底部导航
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("⬅️ 上一步")
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setEnabled(False)
        
        self.page_label = QLabel("1 / 4")
        self.page_label.setAlignment(Qt.AlignCenter)
        
        self.next_btn = QPushButton("下一步 ➡️")
        self.next_btn.clicked.connect(self.next_page)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.page_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        
        layout.addLayout(nav_layout)
        
        # 底部选项
        bottom_layout = QHBoxLayout()
        
        self.dont_show_again_check = QCheckBox("不再显示此引导")
        bottom_layout.addWidget(self.dont_show_again_check)
        
        bottom_layout.addStretch()
        
        skip_btn = QPushButton("跳过引导")
        skip_btn.clicked.connect(self.skip_tutorial)
        bottom_layout.addWidget(skip_btn)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        
        # 样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLabel {
                color: #333;
            }
        """)
    
    def create_welcome_page(self):
        """创建欢迎页"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 图标
        icon_label = QLabel("🐱")
        icon_label.setFont(QFont("", 64))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # 说明文字
        text = QLabel(
            "桌面灵宠是一个可爱的桌面助手，\n"
            "帮助您管理每日任务，提醒重要事项。\n\n"
            "让我们开始一个简短的引导，\n"
            "带您了解如何使用这个应用！"
        )
        text.setFont(QFont("", 14))
        text.setAlignment(Qt.AlignCenter)
        text.setWordWrap(True)
        layout.addWidget(text)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_features_page(self):
        """创建功能介绍页"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        subtitle = QLabel("✨ 主要功能")
        subtitle.setFont(QFont("", 16, QFont.Bold))
        layout.addWidget(subtitle)
        
        features = [
            ("📝", "任务管理", "添加、编辑、删除待办任务，设置优先级和截止时间"),
            ("⏰", "智能提醒", "任务到期前自动提醒，确保不错过任何重要事项"),
            ("🏷️", "标签系统", "使用标签分类管理任务，快速筛选和查找"),
            ("📊", "数据统计", "查看任务完成情况，了解您的工作效率"),
            ("🎨", "主题切换", "支持浅色和暗色主题，保护您的眼睛"),
            ("🐱", "可爱宠物", "桌面宠物陪伴您工作，点击互动更有趣"),
        ]
        
        for icon, title, desc in features:
            feature_layout = QHBoxLayout()
            
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("", 20))
            icon_label.setFixedWidth(40)
            
            text_layout = QVBoxLayout()
            text_layout.setSpacing(2)
            
            title_label = QLabel(title)
            title_label.setFont(QFont("", 12, QFont.Bold))
            
            desc_label = QLabel(desc)
            desc_label.setFont(QFont("", 10))
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666;")
            
            text_layout.addWidget(title_label)
            text_layout.addWidget(desc_label)
            
            feature_layout.addWidget(icon_label)
            feature_layout.addLayout(text_layout)
            
            layout.addLayout(feature_layout)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_shortcuts_page(self):
        """创建快捷键页"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        subtitle = QLabel("⌨️ 快捷键")
        subtitle.setFont(QFont("", 16, QFont.Bold))
        layout.addWidget(subtitle)
        
        shortcuts = [
            ("Ctrl + N", "添加新任务"),
            ("Ctrl + F", "搜索任务"),
            ("Ctrl + W", "关闭当前窗口"),
            ("Delete", "删除选中的任务"),
            ("Enter", "编辑选中的任务"),
        ]
        
        for key, desc in shortcuts:
            shortcut_layout = QHBoxLayout()
            
            key_label = QLabel(key)
            key_label.setFont(QFont("Consolas", 11, QFont.Bold))
            key_label.setStyleSheet("""
                background-color: #e0e0e0;
                padding: 5px 10px;
                border-radius: 3px;
                color: #333;
            """)
            key_label.setFixedWidth(120)
            
            desc_label = QLabel(desc)
            desc_label.setFont(QFont("", 11))
            
            shortcut_layout.addWidget(key_label)
            shortcut_layout.addWidget(desc_label)
            shortcut_layout.addStretch()
            
            layout.addLayout(shortcut_layout)
        
        # 提示
        tip_label = QLabel(
            "\n💡 提示：右键点击桌面宠物可以打开菜单，\n"
            "访问待办事项、设置和其他功能。"
        )
        tip_label.setFont(QFont("", 11))
        tip_label.setWordWrap(True)
        tip_label.setStyleSheet("color: #FF9800; padding: 10px;")
        layout.addWidget(tip_label)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_final_page(self):
        """创建最终页"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # 完成图标
        icon_label = QLabel("🎉")
        icon_label.setFont(QFont("", 64))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # 完成文字
        text = QLabel(
            "太好了！您已经了解了基本功能。\n\n"
            "现在让我们创建第一个任务吧！"
        )
        text.setFont(QFont("", 14))
        text.setAlignment(Qt.AlignCenter)
        text.setWordWrap(True)
        layout.addWidget(text)
        
        # 示例任务选项
        self.create_example_check = QCheckBox("创建示例任务（推荐）")
        self.create_example_check.setChecked(True)
        self.create_example_check.setFont(QFont("", 12))
        example_layout = QHBoxLayout()
        example_layout.addStretch()
        example_layout.addWidget(self.create_example_check)
        example_layout.addStretch()
        layout.addLayout(example_layout)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def next_page(self):
        """下一页"""
        if self.current_page < 3:
            self.current_page += 1
            self.pages_widget.setCurrentIndex(self.current_page)
            self.update_navigation()
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self.pages_widget.setCurrentIndex(self.current_page)
            self.update_navigation()
    
    def update_navigation(self):
        """更新导航按钮状态"""
        self.prev_btn.setEnabled(self.current_page > 0)
        self.page_label.setText(f"{self.current_page + 1} / 4")
        
        if self.current_page == 3:
            self.next_btn.setText("完成 ✓")
            self.next_btn.clicked.disconnect()
            self.next_btn.clicked.connect(self.finish_tutorial)
        else:
            self.next_btn.setText("下一步 ➡️")
            try:
                self.next_btn.clicked.disconnect()
            except:
                pass
            self.next_btn.clicked.connect(self.next_page)
    
    def skip_tutorial(self):
        """跳过引导"""
        self.reject()
    
    def finish_tutorial(self):
        """完成引导"""
        # 创建示例任务
        if self.create_example_check.isChecked() and self.database:
            self.create_example_tasks()
        
        # 标记不再显示
        if self.dont_show_again_check.isChecked():
            self.mark_tutorial_completed()
        
        self.accept()
    
    def create_example_tasks(self):
        """创建示例任务"""
        from datetime import datetime, timedelta
        
        if not self.database:
            return
        
        # 示例任务列表
        example_tasks = [
            {
                'title': '欢迎使用桌面灵宠！',
                'description': '这是一个示例任务。您可以点击"编辑"来修改它，或点击"完成"来标记完成。',
                'priority': 2,
                'category': '示例',
                'due_date': (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            },
            {
                'title': '探索应用功能',
                'description': '尝试添加新任务、设置提醒、查看统计数据等功能。',
                'priority': 1,
                'category': '示例',
                'due_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            },
            {
                'title': '自定义您的桌面宠物',
                'description': '在设置中调整宠物的大小、透明度和行为。',
                'priority': 1,
                'category': '示例',
                'due_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            },
        ]
        
        # 创建示例标签
        tag_id = self.database.add_tag('示例', '#FF9800')
        
        # 添加任务
        for task_data in example_tasks:
            task_id = self.database.add_task(**task_data)
            if task_id and tag_id:
                self.database.add_task_tag(task_id, tag_id)
        
        print("[新手引导] 已创建示例任务")
    
    def mark_tutorial_completed(self):
        """标记引导已完成"""
        try:
            # 在data目录创建标记文件
            os.makedirs('data', exist_ok=True)
            with open('data/.tutorial_completed', 'w') as f:
                f.write('1')
            print("[新手引导] 已标记为完成")
        except Exception as e:
            print(f"[新手引导] 标记失败: {e}")


def should_show_tutorial():
    """检查是否应该显示新手引导"""
    return not os.path.exists('data/.tutorial_completed')


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    tutorial = TutorialWindow()
    result = tutorial.exec_()
    
    if result == QDialog.Accepted:
        print("引导完成")
    else:
        print("引导跳过")
    
    sys.exit(0)

