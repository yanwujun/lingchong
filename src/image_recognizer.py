#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图片识别模块
Image Recognizer Module - 使用OpenAI Vision API识别图片并生成任务
"""

import os
import base64
import hashlib
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from typing import Optional, Dict
import json

# API集成
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class ImageRecognitionWorker(QThread):
    """图片识别工作线程"""
    
    # 信号
    recognition_completed = pyqtSignal(str, dict)  # 识别完成（图片路径，结果）
    error_occurred = pyqtSignal(str)  # 错误
    
    def __init__(self, api_key: str, image_path: str):
        super().__init__()
        self.api_key = api_key
        self.image_path = image_path
    
    def run(self):
        """执行识别"""
        try:
            # 读取并编码图片
            with open(self.image_path, 'rb') as f:
                image_data = f.read()
            
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # 调用OpenAI Vision API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """请分析这张图片，识别其中的内容。如果图片中包含任务、待办事项、笔记或计划等信息，请提取出来。

请按以下格式返回JSON：
{
  "summary": "图片内容简要描述",
  "tasks": [
    {"title": "任务标题1", "description": "任务描述1", "priority": "高/中/低"},
    {"title": "任务标题2", "description": "任务描述2", "priority": "高/中/低"}
  ],
  "category": "建议的分类（工作/学习/生活/其他）"
}

如果图片中没有明确的任务信息，tasks数组可以为空。"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # 尝试解析JSON
                try:
                    # 提取JSON部分（可能包含在代码块中）
                    if '```json' in content:
                        json_start = content.find('```json') + 7
                        json_end = content.find('```', json_start)
                        json_str = content[json_start:json_end].strip()
                    elif '```' in content:
                        json_start = content.find('```') + 3
                        json_end = content.find('```', json_start)
                        json_str = content[json_start:json_end].strip()
                    else:
                        json_str = content
                    
                    recognition_result = json.loads(json_str)
                except json.JSONDecodeError:
                    # 如果不是JSON格式，创建简单结果
                    recognition_result = {
                        'summary': content,
                        'tasks': [],
                        'category': '其他'
                    }
                
                self.recognition_completed.emit(self.image_path, recognition_result)
            else:
                self.error_occurred.emit(f"API调用失败: {response.status_code} - {response.text}")
                
        except FileNotFoundError:
            self.error_occurred.emit(f"图片文件不存在: {self.image_path}")
        except Exception as e:
            self.error_occurred.emit(f"识别失败: {str(e)}")


class ImageRecognizer(QObject):
    """图片识别管理器"""
    
    # 信号
    recognition_completed = pyqtSignal(dict)  # 识别完成
    tasks_generated = pyqtSignal(list)  # 任务生成
    error_occurred = pyqtSignal(str)  # 错误
    
    def __init__(self, database=None):
        super().__init__()
        
        self.database = database
        self.api_key = self.load_api_key()
        self.worker = None
        
        print("[图片识别] 初始化完成")
    
    def load_api_key(self) -> str:
        """加载API Key"""
        # 从配置文件读取
        api_key = os.environ.get('OPENAI_API_KEY', '')
        
        if not api_key:
            try:
                with open('config/api_keys.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_key = config.get('openai_api_key', '')
            except:
                pass
        
        return api_key
    
    def recognize_image(self, image_path: str):
        """
        识别图片
        
        Args:
            image_path: 图片路径
        """
        if not self.api_key:
            self.error_occurred.emit("请先在AI对话设置中配置OpenAI API Key")
            return
        
        if not OPENAI_AVAILABLE or not REQUESTS_AVAILABLE:
            self.error_occurred.emit("请安装必要的库: pip install openai requests")
            return
        
        # 检查文件
        if not os.path.exists(image_path):
            self.error_occurred.emit(f"文件不存在: {image_path}")
            return
        
        # 检查文件大小（限制20MB）
        file_size = os.path.getsize(image_path)
        if file_size > 20 * 1024 * 1024:
            self.error_occurred.emit("图片文件过大（最大20MB）")
            return
        
        print(f"[图片识别] 开始识别: {image_path}")
        
        # 创建工作线程
        self.worker = ImageRecognitionWorker(self.api_key, image_path)
        self.worker.recognition_completed.connect(self.on_recognition_completed)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()
    
    def on_recognition_completed(self, image_path: str, result: Dict):
        """识别完成"""
        print(f"[图片识别] 识别完成")
        print(f"  摘要: {result.get('summary', '')}")
        print(f"  任务数: {len(result.get('tasks', []))}")
        
        # 计算图片哈希
        try:
            with open(image_path, 'rb') as f:
                image_hash = hashlib.md5(f.read()).hexdigest()
        except:
            image_hash = ""
        
        # 保存识别结果到数据库
        if self.database:
            self.database.add_image_task(
                image_path=image_path,
                image_hash=image_hash,
                recognition_result=json.dumps(result, ensure_ascii=False),
                task_id=None
            )
        
        # 发送信号
        self.recognition_completed.emit(result)
        
        # 生成任务
        tasks = result.get('tasks', [])
        if tasks:
            self.tasks_generated.emit(tasks)
            print(f"[图片识别] 生成 {len(tasks)} 个任务")
    
    def on_error(self, error: str):
        """错误处理"""
        self.error_occurred.emit(error)
        print(f"[图片识别] 错误: {error}")
    
    def get_supported_formats(self) -> list:
        """获取支持的图片格式"""
        return ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    def is_supported_image(self, file_path: str) -> bool:
        """检查是否支持的图片格式"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.get_supported_formats()


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    print("=" * 60)
    print("图片识别系统测试")
    print("=" * 60)
    
    recognizer = ImageRecognizer()
    
    # 连接信号
    def on_completed(result):
        print(f"\n识别结果: {result}")
    
    def on_tasks(tasks):
        print(f"\n生成的任务:")
        for task in tasks:
            print(f"  - {task['title']}")
    
    def on_error(error):
        print(f"\n错误: {error}")
    
    recognizer.recognition_completed.connect(on_completed)
    recognizer.tasks_generated.connect(on_tasks)
    recognizer.error_occurred.connect(on_error)
    
    print("\n提示: 需要配置OpenAI API Key并提供图片路径进行测试")
    print("支持的格式:", recognizer.get_supported_formats())
    
    # 测试示例（需要实际图片）
    # recognizer.recognize_image("path/to/image.jpg")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    sys.exit(app.exec_())

