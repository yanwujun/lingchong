#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI对话窗口模块
Chat Window Module - 与桌面宠物的AI对话界面
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTextEdit, QPushButton, QScrollArea, QLineEdit,
                             QGroupBox, QFrame, QApplication, QMessageBox,
                             QDialog, QFormLayout, QComboBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

# 导入AI管理器
try:
    from src.ai_chat import AIChatManager
    from src.modern_ui import ModernButton, ModernTextEdit, ModernInput, COLORS
except ImportError:
    from ai_chat import AIChatManager
    try:
        from modern_ui import ModernButton, ModernTextEdit, ModernInput, COLORS
    except ImportError:
        # 回退到原始组件
        ModernButton = QPushButton
        ModernTextEdit = QTextEdit
        ModernInput = QLineEdit
        COLORS = {'background': '#e0e5ec', 'surface': '#e0e5ec', 'primary': '#6366f1'}


class MessageBubble(QFrame):
    """消息气泡"""
    
    def __init__(self, role: str, message: str):
        super().__init__()
        self.role = role  # 'user' 或 'assistant'
        self.message = message
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 消息标签
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("", 11))
        
        if self.role == 'user':
            # 用户消息 - 蓝色气泡，右对齐
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #2196F3;
                    color: white;
                    padding: 10px;
                    border-radius: 10px;
                }
            """)
            message_label.setAlignment(Qt.AlignRight)
        else:
            # AI消息 - 绿色气泡，左对齐
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    border-radius: 10px;
                }
            """)
            message_label.setAlignment(Qt.AlignLeft)
        
        layout.addWidget(message_label)
        self.setLayout(layout)
        
        # 气泡样式
        self.setStyleSheet("QFrame { background-color: transparent; border: none; }")


class ChatWindow(QWidget):
    """AI对话窗口"""
    
    def __init__(self, database=None, pet_id=None):
        super().__init__()
        self.database = database
        self.pet_id = pet_id
        self.chat_manager = AIChatManager(database, pet_id)
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("💬 与宠物对话")
        self.setGeometry(100, 100, 500, 700)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 标题栏
        header_layout = QHBoxLayout()
        
        title_label = QLabel("💬 AI对话")
        title_label.setFont(QFont("", 16, QFont.Bold))
        
        # 设置按钮
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(30, 30)
        settings_btn.clicked.connect(self.show_settings)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(settings_btn)
        
        layout.addLayout(header_layout)
        
        # 消息显示区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        # 消息容器
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setSpacing(10)
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_widget.setLayout(self.messages_layout)
        
        self.scroll_area.setWidget(self.messages_widget)
        layout.addWidget(self.scroll_area)
        
        # 加载中提示
        self.loading_label = QLabel("AI正在思考中...")
        self.loading_label.setFont(QFont("", 11))
        self.loading_label.setStyleSheet("color: #999; padding: 5px;")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)
        
        # 输入区域
        input_layout = QHBoxLayout()
        
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("输入消息...")
        self.input_edit.setFont(QFont("", 12))
        self.input_edit.returnPressed.connect(self.send_message)
        self.input_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        self.send_btn = QPushButton("发送")
        self.send_btn.setFixedSize(80, 40)
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        # 底部工具栏
        toolbar_layout = QHBoxLayout()
        
        clear_btn = QPushButton("🗑️ 清除历史")
        clear_btn.clicked.connect(self.clear_history)
        clear_btn.setStyleSheet("QPushButton { padding: 5px 10px; }")
        
        close_btn = QPushButton("❌ 关闭")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("QPushButton { padding: 5px 10px; }")
        
        toolbar_layout.addWidget(clear_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(close_btn)
        
        layout.addLayout(toolbar_layout)
        
        self.setLayout(layout)
        
        # 窗口样式
        self.setStyleSheet("""
            QWidget {
                background-color: white;
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
        """)
        
        # 加载历史对话
        self.load_history_messages()
    
    def connect_signals(self):
        """连接信号"""
        self.chat_manager.message_received.connect(self.on_message_received)
        self.chat_manager.error_occurred.connect(self.on_error)
    
    def send_message(self):
        """发送消息"""
        message = self.input_edit.text().strip()
        
        if not message:
            return
        
        # 清空输入框
        self.input_edit.clear()
        
        # 显示加载提示
        self.loading_label.show()
        self.send_btn.setEnabled(False)
        
        # 发送到AI
        self.chat_manager.send_message(message)
    
    def on_message_received(self, role: str, message: str):
        """收到消息"""
        # 添加消息气泡
        bubble = MessageBubble(role, message)
        self.messages_layout.addWidget(bubble)
        
        # 滚动到底部
        QTimer.singleShot(100, self.scroll_to_bottom)
        
        # 隐藏加载提示
        if role == 'assistant':
            self.loading_label.hide()
            self.send_btn.setEnabled(True)
    
    def on_error(self, error: str):
        """错误处理"""
        self.loading_label.hide()
        self.send_btn.setEnabled(True)
        QMessageBox.warning(self, "错误", error)
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def load_history_messages(self):
        """加载历史消息"""
        for msg in self.chat_manager.conversation_history:
            bubble = MessageBubble(msg['role'], msg['content'])
            self.messages_layout.addWidget(bubble)
        
        self.scroll_to_bottom()
    
    def clear_history(self):
        """清除历史"""
        reply = QMessageBox.question(
            self, "确认", "确定要清除所有对话历史吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 清空UI
            while self.messages_layout.count():
                item = self.messages_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # 清空管理器
            self.chat_manager.clear_history()
            
            QMessageBox.information(self, "成功", "对话历史已清除")
    
    def show_settings(self):
        """显示设置对话框"""
        dialog = ChatSettingsDialog(self.chat_manager, self)
        dialog.exec_()
    
    def closeEvent(self, event):
        """关闭事件"""
        event.ignore()
        self.hide()


class ChatSettingsDialog(QDialog):
    """对话设置对话框"""
    
    def __init__(self, chat_manager, parent=None):
        super().__init__(parent)
        self.chat_manager = chat_manager
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("AI对话设置")
        self.setFixedSize(450, 300)
        
        layout = QFormLayout()
        
        # API Key输入
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setText(self.chat_manager.api_key if self.chat_manager.api_key else "")
        self.api_key_edit.setPlaceholderText("输入你的OpenAI API Key...")
        layout.addRow("API Key:", self.api_key_edit)
        
        # 模型选择
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"])
        self.model_combo.setCurrentText(self.chat_manager.model)
        layout.addRow("模型:", self.model_combo)
        
        # 性格选择
        self.personality_combo = QComboBox()
        personalities = [data['name'] for data in self.chat_manager.SYSTEM_PROMPTS.values()]
        self.personality_combo.addItems(personalities)
        layout.addRow("宠物性格:", self.personality_combo)
        
        # 说明
        info_label = QLabel(
            "\n💡 提示:\n"
            "• API Key可以在OpenAI官网获取\n"
            "• gpt-3.5-turbo速度快且便宜\n"
            "• 对话会保存在本地数据库\n"
            "• API Key安全存储在config目录"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addRow(info_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("❌ 取消")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow("", button_layout)
        
        self.setLayout(layout)
        
        # 样式
        self.setStyleSheet("""
            QDialog {
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
        """)
    
    def save_settings(self):
        """保存设置"""
        api_key = self.api_key_edit.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "警告", "请输入API Key！")
            return
        
        # 保存API Key
        if self.chat_manager.save_api_key(api_key):
            # 保存模型
            self.chat_manager.model = self.model_combo.currentText()
            
            # 保存性格
            personality_map = {v['name']: k for k, v in self.chat_manager.SYSTEM_PROMPTS.items()}
            personality_name = self.personality_combo.currentText()
            personality_key = personality_map.get(personality_name, 'default')
            self.chat_manager.set_personality(personality_key)
            
            QMessageBox.information(self, "成功", "设置已保存！")
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "保存API Key失败")


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = ChatWindow()
    window.show()
    
    sys.exit(app.exec_())

