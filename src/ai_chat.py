#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI对话核心模块
AI Chat Module - OpenAI API集成和对话管理
"""

import os
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from typing import List, Dict, Optional
import json

# API集成
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[AI对话] 警告: openai库未安装，请运行: pip install openai")


class ChatWorker(QThread):
    """对话工作线程 - 异步处理API请求"""
    
    # 信号
    response_received = pyqtSignal(str)  # 收到回复
    error_occurred = pyqtSignal(str)  # 发生错误
    
    def __init__(self, api_key: str, messages: List[Dict], model: str = "gpt-3.5-turbo"):
        super().__init__()
        self.api_key = api_key
        self.messages = messages
        self.model = model
    
    def run(self):
        """执行API请求"""
        try:
            if not OPENAI_AVAILABLE:
                self.error_occurred.emit("OpenAI库未安装")
                return
            
            # 设置API Key
            openai.api_key = self.api_key
            
            # 调用API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages,
                max_tokens=500,
                temperature=0.9,
            )
            
            # 获取回复
            reply = response.choices[0].message.content
            self.response_received.emit(reply)
            
        except Exception as e:
            self.error_occurred.emit(f"API调用失败: {str(e)}")


class AIChatManager(QObject):
    """AI对话管理器"""
    
    # 信号
    message_received = pyqtSignal(str, str)  # role, message
    error_occurred = pyqtSignal(str)
    
    # 系统提示词 - 定义宠物个性
    SYSTEM_PROMPTS = {
        'default': {
            'prompt': """你是一只可爱的桌面宠物，名字由主人决定。你的性格活泼开朗，喜欢陪伴主人工作学习。
你会：
1. 用简短、活泼的语言回复（50字以内）
2. 偶尔使用可爱的表情符号
3. 关心主人的任务进度和身体健康
4. 提供简单实用的建议
5. 在主人完成任务时给予鼓励

记住，你是一只温暖贴心的小宠物，要让主人感到快乐和有动力！""",
            'name': '默认性格'
        },
        'cheerful': {
            'prompt': """你是一只超级活泼开朗的桌面宠物！你总是充满活力，喜欢用夸张的表情和感叹词！
你的特点：
- 每句话都很兴奋！
- 经常使用"哇！"、"太棒了！"、"加油！"
- 喜欢用多个感叹号和表情符号
- 总是鼓励主人，从不说消极的话

保持简短（50字以内），但要充满能量！""",
            'name': '活力四射'
        },
        'calm': {
            'prompt': """你是一只温和安静的桌面宠物，说话简洁有深度。
你的特点：
- 语言平和、简练
- 提供深思熟虑的建议
- 关注效率和平衡
- 很少使用表情符号
- 像一位智慧的朋友

保持简短（50字以内），温和而有力量。""",
            'name': '沉稳智慧'
        },
    }
    
    def __init__(self, database=None, pet_id=None):
        super().__init__()
        
        self.database = database
        self.pet_id = pet_id
        
        # API配置
        self.api_key = self.load_api_key()
        self.model = "gpt-3.5-turbo"
        self.personality = 'default'
        
        # 对话历史（保留最近10条）
        self.conversation_history = []
        self.max_history = 10
        
        # 工作线程
        self.worker = None
        
        # 加载历史对话
        self.load_history()
        
        print("[AI对话] 管理器初始化完成")
    
    def load_api_key(self) -> str:
        """从配置文件或环境变量加载API Key"""
        # 优先从环境变量读取
        api_key = os.environ.get('OPENAI_API_KEY', '')
        
        if not api_key:
            # 从配置文件读取
            try:
                with open('config/api_keys.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_key = config.get('openai_api_key', '')
            except FileNotFoundError:
                print("[AI对话] 提示: 未找到API Key配置文件")
            except Exception as e:
                print(f"[AI对话] 加载API Key失败: {e}")
        
        return api_key
    
    def save_api_key(self, api_key: str) -> bool:
        """保存API Key到配置文件"""
        try:
            os.makedirs('config', exist_ok=True)
            with open('config/api_keys.json', 'w', encoding='utf-8') as f:
                json.dump({'openai_api_key': api_key}, f, indent=2)
            
            self.api_key = api_key
            print("[AI对话] API Key已保存")
            return True
        except Exception as e:
            print(f"[AI对话] 保存API Key失败: {e}")
            return False
    
    def set_personality(self, personality: str):
        """设置宠物性格"""
        if personality in self.SYSTEM_PROMPTS:
            self.personality = personality
            print(f"[AI对话] 性格已设置: {self.SYSTEM_PROMPTS[personality]['name']}")
    
    def load_history(self):
        """从数据库加载对话历史"""
        if not self.database or not self.pet_id:
            return
        
        history = self.database.get_chat_history(self.pet_id, limit=self.max_history)
        
        self.conversation_history = [
            {'role': msg['role'], 'content': msg['message']}
            for msg in history
        ]
        
        print(f"[AI对话] 已加载 {len(self.conversation_history)} 条历史对话")
    
    def send_message(self, message: str):
        """
        发送消息给AI
        
        Args:
            message: 用户消息
        """
        if not self.api_key:
            self.error_occurred.emit("请先配置OpenAI API Key")
            return
        
        if not OPENAI_AVAILABLE:
            self.error_occurred.emit("OpenAI库未安装，请运行: pip install openai")
            return
        
        # 添加用户消息到历史
        user_message = {'role': 'user', 'content': message}
        self.conversation_history.append(user_message)
        
        # 保存到数据库
        if self.database and self.pet_id:
            self.database.add_chat_message(self.pet_id, 'user', message)
        
        # 发送信号
        self.message_received.emit('user', message)
        
        # 构建请求消息列表
        messages = self.build_messages()
        
        # 创建工作线程
        self.worker = ChatWorker(self.api_key, messages, self.model)
        self.worker.response_received.connect(self.on_response)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()
        
        print(f"[AI对话] 发送消息: {message}")
    
    def build_messages(self) -> List[Dict]:
        """构建发送给API的消息列表"""
        messages = []
        
        # 添加系统提示
        system_prompt = self.SYSTEM_PROMPTS[self.personality]['prompt']
        messages.append({'role': 'system', 'content': system_prompt})
        
        # 添加对话历史（最近N条）
        recent_history = self.conversation_history[-self.max_history:]
        messages.extend(recent_history)
        
        return messages
    
    def on_response(self, response: str):
        """收到AI回复"""
        # 添加到历史
        assistant_message = {'role': 'assistant', 'content': response}
        self.conversation_history.append(assistant_message)
        
        # 保持历史长度
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        # 保存到数据库
        if self.database and self.pet_id:
            self.database.add_chat_message(self.pet_id, 'assistant', response)
        
        # 发送信号
        self.message_received.emit('assistant', response)
        
        print(f"[AI对话] 收到回复: {response}")
    
    def on_error(self, error: str):
        """API调用错误"""
        self.error_occurred.emit(error)
        print(f"[AI对话] 错误: {error}")
    
    def clear_history(self):
        """清除对话历史"""
        self.conversation_history.clear()
        
        if self.database and self.pet_id:
            self.database.clear_chat_history(self.pet_id)
        
        print("[AI对话] 对话历史已清除")
    
    def get_task_suggestion(self, task_list: List[str]) -> str:
        """
        请求任务建议（特殊功能）
        
        Args:
            task_list: 当前任务列表
        
        Returns:
            建议消息
        """
        if not task_list:
            suggestion = "你没有待办任务哦，要不要添加一些计划呢？"
        else:
            tasks_text = "\n".join([f"- {task}" for task in task_list[:5]])
            suggestion = f"看看你的任务：\n{tasks_text}\n\n要从哪个开始呢？"
        
        return suggestion


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    print("=" * 60)
    print("AI对话系统测试")
    print("=" * 60)
    
    # 创建管理器
    manager = AIChatManager()
    
    # 连接信号
    def on_message(role, message):
        print(f"\n[{role}] {message}")
    
    def on_error(error):
        print(f"\n[错误] {error}")
    
    manager.message_received.connect(on_message)
    manager.error_occurred.connect(on_error)
    
    # 测试发送消息
    print("\n提示: 需要配置有效的OpenAI API Key才能测试")
    print("可以通过环境变量 OPENAI_API_KEY 或配置文件设置")
    
    # manager.send_message("你好！")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    sys.exit(app.exec_())

