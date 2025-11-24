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
    from src.modern_ui import COLORS
except ImportError:
    from utils import get_resource_path
    try:
        from sound_manager import get_sound_manager
        from modern_ui import COLORS
    except ImportError:
        get_sound_manager = None
        COLORS = {'background': '#e0e5ec', 'surface': '#e0e5ec', 'primary': '#6366f1', 'primary_dark': '#4f46e5', 
                  'primary_light': '#a5b4fc', 'text_primary': '#4a5568', 'text_secondary': '#718096', 
                  'shadow_dark': '#a3b1c6', 'shadow_light': '#ffffff', 'divider': '#cbd5e0'}


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
        self.animation_states = ["idle", "walk", "sleep", "happy", "alert", "eat", "stretch", "excited", "sad"]
        self.movie = None  # 当前播放的动画
        self.animation_cache = {}  # 动画缓存字典
        self.animation_paused = False  # 动画是否暂停
        
        # 交互状态
        self.is_hovered = False  # 鼠标是否悬停
        self.hover_timer = QTimer(self)  # 悬停定时器
        self.hover_timer.timeout.connect(self._on_hover_timeout)
        self.hover_timer.setSingleShot(True)
        
        # 定时器
        self.auto_move_timer = QTimer(self)
        self.random_action_timer = QTimer(self)
        self.idle_check_timer = QTimer(self)  # 检查是否停止移动
        
        # 动画对象
        self.move_animation = None
        self.is_moving = False  # 是否正在移动
        self.last_pos = QPoint()  # 上一次的位置
        
        # 其他窗口引用
        self.todo_window = None
        self.settings_window = None
        
        # v0.4.0 新窗口引用
        self.pomodoro_window = None
        self.chat_window = None
        self.achievements_window = None
        self.inventory_window = None
        self.shop_window = None
        
        # 主程序引用（用于调用主程序的方法）
        self.main_app = None
        
        # 音效管理器
        self.sound_manager = get_sound_manager() if get_sound_manager else None
        
        # 动画配置
        self.animation_config = self._load_animation_config()
        
        # 初始化UI
        self.init_ui()
        
        # 启动自动行为
        self.start_auto_behavior()
        
        # 启动空闲检测
        self.idle_check_timer.timeout.connect(self.check_idle_state)
        self.idle_check_timer.start(500)  # 每500ms检查一次
    
    def _load_animation_config(self):
        """加载动画配置"""
        config = {
            'enable_animation': True,
            'animation_speed': 1.0,
            'enable_random_action': True,
            'enable_auto_move': True,
            'durations': {
                'idle': 200,
                'walk': 150,
                'happy': 100,
                'sleep': 800,
                'alert': 120
            }
        }
        
        # 尝试从配置文件加载
        try:
            if isinstance(self.config, dict) and 'Animation' in self.config:
                anim_config = self.config['Animation']
                config['enable_animation'] = anim_config.get('enable_animation', 'true').lower() == 'true'
                config['animation_speed'] = float(anim_config.get('animation_speed', 1.0))
                config['enable_random_action'] = anim_config.get('enable_random_action', 'true').lower() == 'true'
                config['enable_auto_move'] = anim_config.get('enable_auto_move', 'true').lower() == 'true'
                
                # 加载持续时间配置
                for anim_name in ['idle', 'walk', 'happy', 'sleep', 'alert']:
                    key = f'{anim_name}_animation_duration'
                    if key in anim_config:
                        config['durations'][anim_name] = int(anim_config[key])
        except Exception as e:
            print(f"[宠物] 加载动画配置失败: {e}")
        
        return config
    
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
        
        # 启用鼠标追踪（用于悬停效果）
        self.setMouseTracking(True)
        
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
        
        # 让标签不接收鼠标事件，事件由父窗口处理
        self.pet_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        # 预加载所有动画
        self._preload_animations()
        
        # 加载默认动画
        if not self.load_animation("idle"):
            # 如果加载失败，显示文字提示
            self.pet_label.setText("🐱\n宠物")
            self.pet_label.setStyleSheet(f"""
                QLabel {{
                    background-color: rgba(255, 255, 255, 200);
                    border-radius: 12px;
                    font-size: 24px;
                    color: {COLORS['text_primary']};
                    border: 2px solid {COLORS['primary']};
                    padding: 8px;
                }}
            """)
        
        # 设置初始位置（支持嵌套配置）
        if isinstance(self.config, dict) and 'Window' in self.config:
            start_x = int(self.config['Window'].get('start_position_x', 100))
            start_y = int(self.config['Window'].get('start_position_y', 100))
        else:
            start_x = self.config.get('start_position_x', 100)
            start_y = self.config.get('start_position_y', 100)
        self.move(start_x, start_y)
    
    def _preload_animations(self):
        """预加载所有动画到缓存"""
        print("[宠物] 预加载动画...")
        
        if not self.animation_config.get('enable_animation', True):
            print("  [跳过] 动画已禁用")
            return
        
        for animation_name in self.animation_states:
            try:
                # 尝试加载GIF动画
                gif_path = get_resource_path(f"assets/images/default/{animation_name}.gif")
                if os.path.exists(gif_path):
                    movie = QMovie(gif_path)
                    if movie.isValid():
                        # 应用速度设置
                        speed = int(100 * self.animation_config.get('animation_speed', 1.0))
                        movie.setSpeed(speed)
                        
                        self.animation_cache[animation_name] = {
                            'type': 'gif',
                            'path': gif_path,
                            'movie': movie
                        }
                        print(f"  [OK] 预加载GIF: {animation_name}")
                        continue
                
                # 尝试加载PNG图片
                png_path = get_resource_path(f"assets/images/default/{animation_name}.png")
                if os.path.exists(png_path):
                    pixmap = QPixmap(png_path)
                    if not pixmap.isNull():
                        self.animation_cache[animation_name] = {
                            'type': 'png',
                            'pixmap': pixmap
                        }
                        print(f"  [OK] 预加载PNG: {animation_name}")
                        continue
                
                print(f"  [WARN] 未找到动画: {animation_name}")
            except Exception as e:
                print(f"  [ERROR] 预加载{animation_name}失败: {e}")
        
        print(f"[宠物] 预加载完成，共{len(self.animation_cache)}个动画")
    
    def load_animation(self, animation_name):
        """
        加载指定的动画（从缓存）
        
        Args:
            animation_name: 动画名称（如 'idle', 'walk'）
        
        Returns:
            bool: 是否加载成功
        """
        if not self.animation_config.get('enable_animation', True):
            print(f"[宠物] 动画已禁用，跳过加载: {animation_name}")
            return False
        
        try:
            # 检查是否已缓存
            if animation_name in self.animation_cache:
                cached = self.animation_cache[animation_name]
                
                # 停止当前动画
                if self.movie:
                    self.movie.stop()
                
                if cached['type'] == 'gif':
                    # 使用缓存的GIF
                    self.movie = cached['movie']
                    self.pet_label.setMovie(self.movie)
                    self.pet_label.setStyleSheet("")
                    self.movie.start()
                    self.current_animation = animation_name
                    print(f"[宠物] 加载动画(缓存): {animation_name}.gif")
                    return True
                    
                elif cached['type'] == 'png':
                    # 使用缓存的PNG
                    self.pet_label.setPixmap(cached['pixmap'].scaled(
                        self.pet_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    ))
                    self.pet_label.setStyleSheet("")
                    self.movie = None
                    self.current_animation = animation_name
                    print(f"[宠物] 加载图片(缓存): {animation_name}.png")
                    return True
            
            # 如果缓存中没有，尝试直接加载（降级方案）
            print(f"[宠物] 未缓存，尝试直接加载: {animation_name}")
            
            # 尝试加载GIF动画
            gif_path = get_resource_path(f"assets/images/default/{animation_name}.gif")
            if os.path.exists(gif_path):
                if self.movie:
                    self.movie.stop()
                self.movie = QMovie(gif_path)
                
                if not self.movie.isValid():
                    print(f"[宠物] GIF文件无效: {animation_name}.gif")
                    return self._load_fallback_image(animation_name)
                
                # 应用速度设置
                speed = int(100 * self.animation_config.get('animation_speed', 1.0))
                self.movie.setSpeed(speed)
                
                self.pet_label.setMovie(self.movie)
                self.pet_label.setStyleSheet("")
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
                    self.pet_label.setStyleSheet("")
                    self.movie = None
                    self.current_animation = animation_name
                    print(f"[宠物] 加载图片: {animation_name}.png")
                    return True
            
            # 所有尝试失败，使用降级方案
            print(f"[宠物] 警告：未找到动画文件: {animation_name}")
            return self._load_fallback_image(animation_name)
            
        except Exception as e:
            print(f"[宠物] 错误：加载动画失败 ({animation_name}): {e}")
            import traceback
            traceback.print_exc()
            # 尝试降级方案
            return self._load_fallback_image(animation_name)
    
    def _load_fallback_image(self, animation_name):
        """
        降级方案：加载备用图片或显示文字
        
        Args:
            animation_name: 动画名称
        
        Returns:
            bool: 是否加载成功
        """
        try:
            # 尝试加载idle作为备用
            if animation_name != 'idle' and 'idle' in self.animation_cache:
                print(f"[宠物] 使用idle作为{animation_name}的备用")
                cached = self.animation_cache['idle']
                if cached['type'] == 'gif':
                    self.movie = cached['movie']
                    self.pet_label.setMovie(self.movie)
                    self.movie.start()
                    return True
                elif cached['type'] == 'png':
                    self.pet_label.setPixmap(cached['pixmap'].scaled(
                        self.pet_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    ))
                    return True
            
            # 最终降级：显示文字
            print(f"[宠物] 最终降级：显示文字表情")
            emoji_map = {
                'idle': '😊',
                'walk': '🚶',
                'happy': '😄',
                'sleep': '😴',
                'alert': '😲',
                'eat': '😋',
                'stretch': '🥱',
                'excited': '🤩',
                'sad': '😢'
            }
            emoji = emoji_map.get(animation_name, '🐱')
            
            self.pet_label.setText(f"{emoji}\n{animation_name}")
            self.pet_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(255, 255, 255, 200);
                    border-radius: 10px;
                    font-size: 24px;
                    color: #333;
                }
            """)
            return True
            
        except Exception as e:
            print(f"[宠物] 错误：降级方案也失败了: {e}")
            return False
    
    def pause_animation(self):
        """暂停当前动画"""
        if self.movie and self.movie.state() == QMovie.Running:
            self.movie.setPaused(True)
            self.animation_paused = True
            print("[宠物] 动画已暂停")
            return True
        return False
    
    def resume_animation(self):
        """恢复动画播放"""
        if self.movie and self.animation_paused:
            self.movie.setPaused(False)
            self.animation_paused = False
            print("[宠物] 动画已恢复")
            return True
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
        
        # 标记为正在移动
        self.is_moving = True
        self.last_pos = self.pos()
        
        # 切换到行走动画
        if self.current_animation != "walk":
            self.load_animation("walk")
        
        # 创建位置动画
        self.move_animation = QPropertyAnimation(self, b"pos")
        self.move_animation.setDuration(duration)
        self.move_animation.setStartValue(self.pos())
        self.move_animation.setEndValue(QPoint(target_x, target_y))
        self.move_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 移动完成后的回调
        self.move_animation.finished.connect(self.on_move_finished)
        
        self.move_animation.start()
    
    def on_move_finished(self):
        """移动完成回调"""
        self.is_moving = False
        # 切换回闲置动画
        if self.current_animation == "walk":
            self.load_animation("idle")
    
    def check_idle_state(self):
        """检查空闲状态 - 如果在移动但没有动画，切换到行走动画"""
        current_pos = self.pos()
        
        # 如果位置改变了（正在移动）
        if current_pos != self.last_pos:
            if not self.is_moving and not self.is_dragging:
                self.is_moving = True
                if self.current_animation != "walk":
                    self.load_animation("walk")
        else:
            # 位置没变，确保显示闲置动画
            if self.is_moving and not self.is_dragging:
                self.is_moving = False
                if self.current_animation == "walk":
                    self.load_animation("idle")
        
        self.last_pos = current_pos
    
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
        # 如果正在移动或拖拽，不执行随机动作
        if self.is_moving or self.is_dragging:
            return
        
        # 随机选择一个动画状态（排除walk，因为walk只在移动时播放）
        idle_actions = ["idle", "sleep", "happy", "alert", "eat", "stretch"]
        action = random.choice(idle_actions)
        
        # 播放对应动画
        self.load_animation(action)
        print(f"[宠物] 执行动作: {action}")
        
        # 如果是happy动画，可能会跳跃
        if action == "happy" and random.random() < 0.3:  # 30%概率跳跃
            QTimer.singleShot(200, self.bounce_jump)
        
        # 动画播放一段时间后，恢复idle
        if action != "idle":
            duration_map = {
                "sleep": 3000,
                "stretch": 3000,
                "eat": 2000,
                "alert": 2000,
                "happy": 2000
            }
            duration = duration_map.get(action, 2000)
            QTimer.singleShot(duration, lambda: self.load_animation("idle"))
    
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
            
            # 拖动时播放行走动画
            if self.current_animation != "walk":
                self.load_animation("walk")
            
            # 拖动时增加轻微透明效果（可选）
            # if self.windowOpacity() > 0.85:
            #     self.setWindowOpacity(0.85)
            
            event.accept()
        else:
            # 处理悬停移动
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.is_moving = False
            
            # 拖动结束后，恢复闲置动画
            QTimer.singleShot(300, lambda: self.load_animation("idle"))
            
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        if event.button() == Qt.LeftButton:
            print("[宠物] 被双击了！")
            # 播放开心动画并跳跃
            self.load_animation("happy")
            self.bounce_jump()
            
            # 播放音效
            if self.sound_manager:
                self.sound_manager.play_success()
            
            event.accept()
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self.is_hovered = True
        # 启动悬停计时器（1秒后触发）
        self.hover_timer.start(1000)
        
        # 轻微放大效果（可选）
        # self.setWindowOpacity(0.9)
        
        event.accept()
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.is_hovered = False
        # 停止悬停计时器
        self.hover_timer.stop()
        
        # 恢复透明度
        # self.setWindowOpacity(1.0)
        
        event.accept()
    
    def _on_hover_timeout(self):
        """悬停超时回调 - 鼠标悬停超过1秒"""
        if self.is_hovered and not self.is_dragging:
            # 显示一个友好的动画
            if self.current_animation == "idle":
                # 可以播放一个轻微的反应动画
                print("[宠物] 悬停检测 - 显示友好反应")
                # 暂时不改变动画，避免过度打扰
    
    def bounce_jump(self):
        """弹跳效果"""
        # 保存当前位置
        start_pos = self.pos()
        jump_height = 30
        
        # 向上跳
        up_animation = QPropertyAnimation(self, b"pos")
        up_animation.setDuration(200)
        up_animation.setStartValue(start_pos)
        up_animation.setEndValue(QPoint(start_pos.x(), start_pos.y() - jump_height))
        up_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # 落下
        down_animation = QPropertyAnimation(self, b"pos")
        down_animation.setDuration(200)
        down_animation.setStartValue(QPoint(start_pos.x(), start_pos.y() - jump_height))
        down_animation.setEndValue(start_pos)
        down_animation.setEasingCurve(QEasingCurve.InQuad)
        
        # 连接动画
        up_animation.finished.connect(down_animation.start)
        down_animation.finished.connect(lambda: self.load_animation("idle"))
        
        up_animation.start()
        
        # 保存动画引用，避免被垃圾回收
        self._bounce_animations = (up_animation, down_animation)
    
    def show_context_menu(self):
        """显示右键菜单"""
        menu = QMenu(self)
        # 应用Neumorphism样式
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS['surface']};
                border: none;
                border-radius: 16px;
                padding: 8px;
                font-size: 14px;
                box-shadow: 8px 8px 16px {COLORS['shadow_dark']}, 
                           -8px -8px 16px {COLORS['shadow_light']};
            }}
            QMenu::item {{
                background-color: transparent;
                padding: 10px 20px;
                border-radius: 10px;
                color: {COLORS['text_primary']};
                margin: 2px 4px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['surface']};
                box-shadow: inset 2px 2px 4px {COLORS['shadow_dark']}, 
                           inset -2px -2px 4px {COLORS['shadow_light']};
            }}
            QMenu::item:disabled {{
                color: {COLORS['text_secondary']};
            }}
            QMenu::separator {{
                height: 2px;
                background-color: {COLORS['divider']};
                margin: 6px 12px;
            }}
        """)
        
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
        try:
            # 优先使用已有的窗口引用
            if self.achievements_window:
                self.achievements_window.show()
                self.achievements_window.raise_()
                self.achievements_window.activateWindow()
            # 如果窗口不存在，尝试通过主程序打开
            elif self.main_app and hasattr(self.main_app, 'show_achievements'):
                self.main_app.show_achievements()
                # 更新窗口引用
                if hasattr(self.main_app, 'achievements_window'):
                    self.achievements_window = self.main_app.achievements_window
            # 如果主程序也不可用，尝试延迟创建
            else:
                try:
                    from src.pet_achievements import AchievementsWindow
                    from PyQt5.QtWidgets import QApplication
                    
                    # 获取数据库和宠物ID（需要从主程序获取）
                    if self.main_app and hasattr(self.main_app, 'database'):
                        database = self.main_app.database
                        pet_id = self.pet_id
                        if not pet_id and hasattr(self.main_app, 'pet_manager'):
                            active_pet = self.main_app.pet_manager.get_active_pet() if self.main_app.pet_manager else None
                            pet_id = active_pet['id'] if active_pet else None
                        
                        self.achievements_window = AchievementsWindow(database=database, pet_id=pet_id)
                        if hasattr(self.achievements_window, 'load_achievements'):
                            self.achievements_window.load_achievements()
                        self.achievements_window.show()
                        self.achievements_window.raise_()
                        self.achievements_window.activateWindow()
                    else:
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.warning(self, "错误", "无法打开成就窗口：数据库未初始化")
                        print("[警告] 成就窗口未初始化，且无法延迟创建")
                except Exception as e:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "错误", f"打开成就窗口失败：\n{str(e)}")
                    print(f"[错误] 打开成就窗口失败: {e}")
                    import traceback
                    traceback.print_exc()
        except Exception as e:
            print(f"[错误] 打开成就窗口异常: {e}")
            import traceback
            traceback.print_exc()
    
    def open_inventory_window(self):
        """打开背包窗口"""
        print("[系统] 打开背包窗口")
        try:
            # 优先使用已有的窗口引用
            if self.inventory_window:
                self.inventory_window.show()
                self.inventory_window.raise_()
                self.inventory_window.activateWindow()
            # 如果窗口不存在，尝试通过主程序打开
            elif self.main_app and hasattr(self.main_app, 'show_inventory'):
                self.main_app.show_inventory()
                # 更新窗口引用
                if hasattr(self.main_app, 'inventory_window'):
                    self.inventory_window = self.main_app.inventory_window
            # 如果主程序也不可用，尝试延迟创建
            else:
                try:
                    from src.pet_inventory import InventoryWindow
                    
                    # 获取数据库和宠物ID（需要从主程序获取）
                    if self.main_app and hasattr(self.main_app, 'database'):
                        database = self.main_app.database
                        pet_id = self.pet_id
                        if not pet_id and hasattr(self.main_app, 'pet_manager'):
                            active_pet = self.main_app.pet_manager.get_active_pet() if self.main_app.pet_manager else None
                            pet_id = active_pet['id'] if active_pet else None
                        
                        growth_system = None
                        if hasattr(self.main_app, 'pet_growth'):
                            growth_system = self.main_app.pet_growth
                        
                        self.inventory_window = InventoryWindow(
                            database=database,
                            pet_id=pet_id,
                            growth_system=growth_system
                        )
                        if hasattr(self.inventory_window, 'load_inventory'):
                            self.inventory_window.load_inventory()
                        self.inventory_window.show()
                        self.inventory_window.raise_()
                        self.inventory_window.activateWindow()
                    else:
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.warning(self, "错误", "无法打开背包窗口：数据库未初始化")
                        print("[警告] 背包窗口未初始化，且无法延迟创建")
                except Exception as e:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "错误", f"打开背包窗口失败：\n{str(e)}")
                    print(f"[错误] 打开背包窗口失败: {e}")
                    import traceback
                    traceback.print_exc()
        except Exception as e:
            print(f"[错误] 打开背包窗口异常: {e}")
            import traceback
            traceback.print_exc()
    
    def open_shop_window(self):
        """打开商店窗口"""
        print("[系统] 打开商店窗口")
        try:
            # 优先使用已有的窗口引用
            if self.shop_window:
                self.shop_window.show()
                self.shop_window.raise_()
                self.shop_window.activateWindow()
            # 如果窗口不存在，尝试通过主程序打开
            elif self.main_app and hasattr(self.main_app, 'show_shop'):
                self.main_app.show_shop()
                # 更新窗口引用
                if hasattr(self.main_app, 'shop_window'):
                    self.shop_window = self.main_app.shop_window
            # 如果主程序也不可用，尝试延迟创建
            else:
                try:
                    from src.pet_shop import PetShopWindow
                    
                    # 获取数据库和宠物ID（需要从主程序获取）
                    if self.main_app and hasattr(self.main_app, 'database'):
                        database = self.main_app.database
                        pet_id = self.pet_id
                        if not pet_id and hasattr(self.main_app, 'pet_manager'):
                            active_pet = self.main_app.pet_manager.get_active_pet() if self.main_app.pet_manager else None
                            pet_id = active_pet['id'] if active_pet else None
                        
                        self.shop_window = PetShopWindow(
                            database=database,
                            pet_id=pet_id
                        )
                        if hasattr(self.shop_window, 'load_points'):
                            self.shop_window.load_points()
                        self.shop_window.show()
                        self.shop_window.raise_()
                        self.shop_window.activateWindow()
                    else:
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.warning(self, "错误", "无法打开商店窗口：数据库未初始化")
                        print("[警告] 商店窗口未初始化，且无法延迟创建")
                except Exception as e:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "错误", f"打开商店窗口失败：\n{str(e)}")
                    print(f"[错误] 打开商店窗口失败: {e}")
                    import traceback
                    traceback.print_exc()
        except Exception as e:
            print(f"[错误] 打开商店窗口异常: {e}")
            import traceback
            traceback.print_exc()
    
    def close_application(self):
        """关闭应用程序"""
        print("[系统] 退出应用")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """清理资源"""
        print("[宠物窗口] 清理资源...")
        
        try:
            # 停止所有定时器
            if hasattr(self, 'auto_move_timer') and self.auto_move_timer:
                self.auto_move_timer.stop()
                print("  [OK] 自动移动定时器已停止")
            
            if hasattr(self, 'random_action_timer') and self.random_action_timer:
                self.random_action_timer.stop()
                print("  [OK] 随机动作定时器已停止")
            
            if hasattr(self, 'idle_check_timer') and self.idle_check_timer:
                self.idle_check_timer.stop()
                print("  [OK] 空闲检测定时器已停止")
            
            # 停止动画
            if hasattr(self, 'movie') and self.movie:
                self.movie.stop()
                self.movie = None
                print("  [OK] 动画已停止")
            
            # 停止位置动画
            if hasattr(self, 'move_animation') and self.move_animation:
                self.move_animation.stop()
                self.move_animation = None
                print("  [OK] 位置动画已停止")
            
            # 停止弹跳动画
            if hasattr(self, '_bounce_animations'):
                for anim in self._bounce_animations:
                    if anim:
                        anim.stop()
                self._bounce_animations = None
                print("  [OK] 弹跳动画已停止")
            
            # 停止悬停定时器
            if hasattr(self, 'hover_timer') and self.hover_timer:
                self.hover_timer.stop()
                print("  [OK] 悬停定时器已停止")
            
            # 保存配置（如果需要）
            # TODO: 实现配置保存逻辑
            
            print("[宠物窗口] 资源清理完成")
            
        except Exception as e:
            print(f"[宠物窗口] 清理资源时发生错误: {e}")
    
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

