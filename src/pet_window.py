#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
宠物窗口模块
Pet Window Module - 负责宠物的显示、动画和交互
"""

import sys
import os
from PyQt5.QtWidgets import QWidget, QLabel, QMenu, QAction
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QPixmap, QMovie, QCursor
import random

# 导入工具函数
try:
    from src.utils import get_resource_path
    from src.sound_manager import get_sound_manager
except ImportError:
    from utils import get_resource_path
    try:
        from sound_manager import get_sound_manager
    except ImportError:
        get_sound_manager = None


class PetWindow(QWidget):
    """桌面宠物窗口类"""
    
    # 信号 [v0.4.0]
    image_dropped = pyqtSignal(str)  # 图片拖放信号
    
    def __init__(self, config=None, pet_id=None):
        super().__init__()
        self.config = config or {}
        self.pet_id = pet_id  # [v0.4.0] 宠物ID，支持多宠物
        
        # 窗口属性
        self.is_dragging = False
        self.drag_position = QPoint()
        
        # 动画状态
        self.current_animation = "idle"
        self.animation_states = ["idle", "walk", "sleep", "happy"]
        self.movie = None  # 当前播放的动画
        
        # 定时器
        self.auto_move_timer = QTimer(self)
        self.random_action_timer = QTimer(self)
        
        # 动画对象
        self.move_animation = None
        
        # 其他窗口引用
        self.todo_window = None
        self.settings_window = None
        
        # v0.4.0 新窗口引用
        self.pomodoro_window = None
        self.chat_window = None
        self.achievements_window = None
        self.inventory_window = None
        self.shop_window = None
        
        # 音效管理器
        self.sound_manager = get_sound_manager() if get_sound_manager else None
        
        # 初始化UI
        self.init_ui()
        
        # 启动自动行为
        self.start_auto_behavior()
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标志：无边框、置顶、工具窗口
        self.setWindowFlags(
            Qt.FramelessWindowHint |      # 无边框
            Qt.WindowStaysOnTopHint |     # 窗口置顶
            Qt.Tool                        # 工具窗口（不显示在任务栏）
        )
        
        # 设置透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 启用拖放 [v0.4.0]
        self.setAcceptDrops(True)
        
        # 设置窗口大小（支持嵌套配置）
        if isinstance(self.config, dict) and 'Pet' in self.config:
            pet_size = int(self.config['Pet'].get('size', 128))
        else:
            pet_size = self.config.get('size', 128)
        self.setFixedSize(pet_size, pet_size)
        
        # 创建标签用于显示宠物图片/动画
        self.pet_label = QLabel(self)
        self.pet_label.setAlignment(Qt.AlignCenter)
        self.pet_label.setGeometry(0, 0, pet_size, pet_size)
        
        # 加载默认动画
        if not self.load_animation("idle"):
            # 如果加载失败，显示文字提示
            self.pet_label.setText("🐱\n宠物")
            self.pet_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(255, 255, 255, 200);
                    border-radius: 10px;
                    font-size: 24px;
                    color: #333;
                }
            """)
        
        # 设置初始位置（支持嵌套配置）
        if isinstance(self.config, dict) and 'Window' in self.config:
            start_x = int(self.config['Window'].get('start_position_x', 100))
            start_y = int(self.config['Window'].get('start_position_y', 100))
        else:
            start_x = self.config.get('start_position_x', 100)
            start_y = self.config.get('start_position_y', 100)
        self.move(start_x, start_y)
    
    def load_animation(self, animation_name):
        """
        加载指定的动画
        
        Args:
            animation_name: 动画名称（如 'idle', 'walk'）
        
        Returns:
            bool: 是否加载成功
        """
        try:
            # 尝试加载GIF动画（使用资源路径函数）
            gif_path = get_resource_path(f"assets/images/default/{animation_name}.gif")
            if os.path.exists(gif_path):
                if self.movie:
                    self.movie.stop()
                self.movie = QMovie(gif_path)
                self.pet_label.setMovie(self.movie)
                self.pet_label.setStyleSheet("")  # 清除样式
                self.movie.start()
                self.current_animation = animation_name
                print(f"[宠物] 加载动画: {animation_name}.gif")
                return True
            
            # 尝试加载PNG图片
            png_path = get_resource_path(f"assets/images/default/{animation_name}.png")
            if os.path.exists(png_path):
                pixmap = QPixmap(png_path)
                if not pixmap.isNull():
                    self.pet_label.setPixmap(pixmap.scaled(
                        self.pet_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    ))
                    self.pet_label.setStyleSheet("")  # 清除样式
                    self.current_animation = animation_name
                    print(f"[宠物] 加载图片: {animation_name}.png")
                    return True
            
            print(f"[宠物] 未找到动画: {animation_name}")
            return False
        except Exception as e:
            print(f"[宠物] 加载动画失败: {e}")
            return False
    
    def start_auto_behavior(self):
        """启动自动行为"""
        # 获取行为配置（支持嵌套配置）
        if isinstance(self.config, dict) and 'Behavior' in self.config:
            behavior_config = self.config['Behavior']
            auto_move = behavior_config.get('auto_move', True)
            if isinstance(auto_move, str):
                auto_move = auto_move.lower() == 'true'
            random_action = behavior_config.get('random_action', True)
            if isinstance(random_action, str):
                random_action = random_action.lower() == 'true'
            action_interval = int(behavior_config.get('action_interval', 10))
        else:
            auto_move = self.config.get('auto_move', True)
            random_action = self.config.get('random_action', True)
            action_interval = self.config.get('action_interval', 10)
        
        # 自动移动计时器
        if auto_move:
            move_interval = action_interval * 1000
            self.auto_move_timer.timeout.connect(self.random_move)
            self.auto_move_timer.start(move_interval)
        
        # 随机动作计时器
        if random_action:
            self.random_action_timer.timeout.connect(self.random_action)
            self.random_action_timer.start(action_interval * 1000)
    
    def smooth_move(self, target_x, target_y, duration=1000):
        """
        平滑移动到目标位置
        
        Args:
            target_x: 目标X坐标
            target_y: 目标Y坐标  
            duration: 动画时长（毫秒）
        """
        # 停止之前的动画
        if self.move_animation:
            self.move_animation.stop()
        
        # 创建位置动画
        self.move_animation = QPropertyAnimation(self, b"pos")
        self.move_animation.setDuration(duration)
        self.move_animation.setStartValue(self.pos())
        self.move_animation.setEndValue(QPoint(target_x, target_y))
        self.move_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.move_animation.start()
    
    def random_move(self):
        """随机移动宠物"""
        # 获取屏幕尺寸
        screen = self.screen().geometry()
        
        # 生成随机位置（确保不超出屏幕）
        max_x = screen.width() - self.width()
        max_y = screen.height() - self.height()
        
        new_x = random.randint(0, max_x)
        new_y = random.randint(0, max_y)
        
        # 使用平滑移动
        self.smooth_move(new_x, new_y, duration=2000)
    
    def random_action(self):
        """执行随机动作"""
        # 随机选择一个动画状态
        action = random.choice(self.animation_states)
        # 播放对应动画
        self.load_animation(action)
        print(f"[宠物] 执行动作: {action}")
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 开始拖拽
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
            # 播放点击反馈
            print("[宠物] 被点击了！")
            
            # 播放点击音效 [v0.3.0]
            if self.sound_manager:
                self.sound_manager.play_click()
            
        elif event.button() == Qt.RightButton:
            # 显示右键菜单
            self.show_context_menu()
            event.accept()
            
            # 播放点击音效 [v0.3.0]
            if self.sound_manager:
                self.sound_manager.play_click()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            # 拖动窗口
            new_pos = event.globalPos() - self.drag_position
            
            # 限制在屏幕范围内（边界检测）
            screen = self.screen().geometry()
            x = max(0, min(new_pos.x(), screen.width() - self.width()))
            y = max(0, min(new_pos.y(), screen.height() - self.height()))
            
            self.move(x, y)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        if event.button() == Qt.LeftButton:
            print("[宠物] 被双击了！")
            # TODO: 播放特殊动画
            event.accept()
    
    def show_context_menu(self):
        """显示右键菜单"""
        menu = QMenu(self)
        
        # 添加菜单项
        todo_action = QAction("📝 待办事项", self)
        
        # v0.4.0 新增菜单项
        pomodoro_action = QAction("🍅 番茄钟", self)
        chat_action = QAction("💬 AI对话", self)
        
        # 宠物相关子菜单
        pet_menu = menu.addMenu("🐾 宠物")
        achievements_action = QAction("🏆 成就", self)
        inventory_action = QAction("🎒 背包", self)
        shop_action = QAction("🛒 商店", self)
        pet_menu.addAction(achievements_action)
        pet_menu.addAction(inventory_action)
        pet_menu.addAction(shop_action)
        
        settings_action = QAction("⚙️ 设置", self)
        hide_action = QAction("👻 隐藏", self)
        quit_action = QAction("❌ 退出", self)
        
        # 连接信号
        todo_action.triggered.connect(self.open_todo_window)
        pomodoro_action.triggered.connect(self.open_pomodoro_window)
        chat_action.triggered.connect(self.open_chat_window)
        achievements_action.triggered.connect(self.open_achievements_window)
        inventory_action.triggered.connect(self.open_inventory_window)
        shop_action.triggered.connect(self.open_shop_window)
        settings_action.triggered.connect(self.open_settings_window)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self.close_application)
        
        # 添加到菜单
        menu.addAction(todo_action)
        menu.addAction(pomodoro_action)
        menu.addAction(chat_action)
        menu.addSeparator()
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(hide_action)
        menu.addAction(quit_action)
        
        # 显示菜单
        menu.exec_(QCursor.pos())
    
    def open_todo_window(self):
        """打开待办事项窗口"""
        print("[系统] 打开待办事项窗口")
        if self.todo_window:
            self.todo_window.show()
            self.todo_window.raise_()
            self.todo_window.activateWindow()
        else:
            print("[警告] 待办窗口未初始化")
    
    def open_settings_window(self):
        """打开设置窗口"""
        print("[系统] 打开设置窗口")
        if self.settings_window:
            self.settings_window.show()
            self.settings_window.raise_()
            self.settings_window.activateWindow()
        else:
            print("[警告] 设置窗口未初始化")
    
    # ========== v0.4.0 新增打开窗口方法 ==========
    
    def open_pomodoro_window(self):
        """打开番茄钟窗口"""
        print("[系统] 打开番茄钟窗口")
        if self.pomodoro_window:
            self.pomodoro_window.show()
            self.pomodoro_window.raise_()
            self.pomodoro_window.activateWindow()
        else:
            print("[警告] 番茄钟窗口未初始化")
    
    def open_chat_window(self):
        """打开AI对话窗口"""
        print("[系统] 打开AI对话窗口")
        if self.chat_window:
            self.chat_window.show()
            self.chat_window.raise_()
            self.chat_window.activateWindow()
        else:
            print("[警告] AI对话窗口未初始化")
    
    def open_achievements_window(self):
        """打开成就窗口"""
        print("[系统] 打开成就窗口")
        if self.achievements_window:
            self.achievements_window.show()
            self.achievements_window.raise_()
            self.achievements_window.activateWindow()
        else:
            print("[警告] 成就窗口未初始化")
    
    def open_inventory_window(self):
        """打开背包窗口"""
        print("[系统] 打开背包窗口")
        if self.inventory_window:
            self.inventory_window.show()
            self.inventory_window.raise_()
            self.inventory_window.activateWindow()
        else:
            print("[警告] 背包窗口未初始化")
    
    def open_shop_window(self):
        """打开商店窗口"""
        print("[系统] 打开商店窗口")
        if self.shop_window:
            self.shop_window.show()
            self.shop_window.raise_()
            self.shop_window.activateWindow()
        else:
            print("[警告] 商店窗口未初始化")
    
    def close_application(self):
        """关闭应用程序"""
        print("[系统] 退出应用")
        # TODO: 清理资源，保存配置
        sys.exit(0)
    
    def show_reminder(self, task_info):
        """
        显示提醒动画
        
        Args:
            task_info: 任务信息字典
        """
        print(f"[提醒] 任务提醒: {task_info.get('title', '未知任务')}")
        
        # 播放提醒动画
        self.load_animation("alert")
        
        # 确保窗口可见
        if not self.isVisible():
            self.show()
    
    # ========== 拖放功能 [v0.4.0] ==========
    
    def dragEnterEvent(self, event):
        """拖放进入事件"""
        # 检查是否包含文件
        if event.mimeData().hasUrls():
            # 检查是否是图片文件
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                # 检查文件扩展名
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    event.acceptProposedAction()
                    print(f"[宠物窗口] 拖放进入: {file_path}")
                    # 播放欢迎动画
                    self.load_animation("happy")
                    return
        
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖放离开事件"""
        # 恢复默认动画
        self.load_animation("idle")
    
    def dropEvent(self, event):
        """拖放释放事件 - 图片被拖放到宠物上"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                
                # 检查是否是图片
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    print(f"[宠物窗口] 收到图片: {file_path}")
                    
                    # 播放快乐动画
                    self.load_animation("happy")
                    
                    # 处理图片识别（通过信号传递给主程序）
                    if hasattr(self, 'image_dropped'):
                        self.image_dropped.emit(file_path)
                    else:
                        # 如果没有信号，直接处理
                        self.process_image(file_path)
                    
                    event.acceptProposedAction()
                    return
        
        event.ignore()
    
    def process_image(self, image_path: str):
        """
        处理拖放的图片
        
        Args:
            image_path: 图片路径
        """
        print(f"[宠物窗口] 处理图片: {image_path}")
        
        # 这里应该调用图片识别服务
        # 由于需要数据库和其他依赖，实际处理应该在主程序中进行
        # 这里只是一个占位方法
        
        # 窗口置顶并闪烁效果
        self.raise_()
        self.activateWindow()


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 测试配置
    test_config = {
        'size': 128,
        'start_position_x': 200,
        'start_position_y': 200,
        'auto_move': True,
        'random_action': True,
        'action_interval': 10,
    }
    
    pet = PetWindow(config=test_config)
    pet.show()
    
    print("=" * 50)
    print("桌面宠物窗口测试")
    print("=" * 50)
    print("操作说明：")
    print("  - 左键拖动：移动宠物")
    print("  - 左键单击：触发互动")
    print("  - 左键双击：特殊动画")
    print("  - 右键：打开菜单")
    print("=" * 50)
    
    sys.exit(app.exec_())

