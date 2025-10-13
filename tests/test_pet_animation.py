#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
宠物动画系统测试
Pet Animation System Tests
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QMovie, QPixmap

# 创建QApplication实例（测试PyQt需要）
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)


class TestPetAnimation(unittest.TestCase):
    """宠物动画系统测试类"""
    
    def setUp(self):
        """测试前准备"""
        from src.pet_window import PetWindow
        
        # 创建测试配置
        self.test_config = {
            'Pet': {'size': 128},
            'Window': {'start_position_x': 100, 'start_position_y': 100},
            'Behavior': {'auto_move': False, 'random_action': False},
            'Animation': {
                'enable_animation': 'true',
                'animation_speed': '1.0'
            }
        }
        
        # 创建宠物窗口实例
        self.pet_window = PetWindow(config=self.test_config)
    
    def tearDown(self):
        """测试后清理"""
        if hasattr(self, 'pet_window'):
            self.pet_window.cleanup()
            self.pet_window.close()
    
    def test_animation_loading(self):
        """测试动画加载功能"""
        # 测试加载闲置动画
        result = self.pet_window.load_animation("idle")
        self.assertTrue(result, "应该成功加载idle动画")
        self.assertEqual(self.pet_window.current_animation, "idle")
        
        # 测试加载行走动画
        result = self.pet_window.load_animation("walk")
        self.assertTrue(result, "应该成功加载walk动画")
        self.assertEqual(self.pet_window.current_animation, "walk")
        
        # 测试加载不存在的动画
        result = self.pet_window.load_animation("nonexistent")
        self.assertFalse(result, "不应该加载不存在的动画")
    
    def test_animation_states(self):
        """测试动画状态列表"""
        expected_states = ["idle", "walk", "sleep", "happy", "alert", "eat", "stretch", "excited", "sad"]
        self.assertEqual(self.pet_window.animation_states, expected_states, 
                        f"动画状态列表应该包含所有9个状态")
    
    def test_animation_cache(self):
        """测试动画缓存机制"""
        # 检查缓存是否已初始化
        self.assertIsInstance(self.pet_window.animation_cache, dict, 
                             "动画缓存应该是字典类型")
        
        # 预加载后应该有缓存
        if len(self.pet_window.animation_cache) > 0:
            # 检查缓存结构
            for name, cached in self.pet_window.animation_cache.items():
                self.assertIn('type', cached, f"{name}的缓存应该有type字段")
                self.assertIn(cached['type'], ['gif', 'png'], 
                             f"{name}的缓存类型应该是gif或png")
    
    def test_animation_switching(self):
        """测试动画切换逻辑"""
        # 从idle切换到walk
        self.pet_window.load_animation("idle")
        self.assertEqual(self.pet_window.current_animation, "idle")
        
        self.pet_window.load_animation("walk")
        self.assertEqual(self.pet_window.current_animation, "walk")
        
        # 从walk切换回idle
        self.pet_window.load_animation("idle")
        self.assertEqual(self.pet_window.current_animation, "idle")
    
    def test_movement_animation(self):
        """测试移动动画"""
        # 初始状态
        self.assertFalse(self.pet_window.is_moving, "初始状态应该不在移动")
        
        # 开始移动
        self.pet_window.smooth_move(200, 200, duration=100)
        self.assertTrue(self.pet_window.is_moving, "应该标记为正在移动")
        self.assertEqual(self.pet_window.current_animation, "walk", 
                        "移动时应该播放walk动画")
        
        # 等待移动完成（模拟）
        self.pet_window.on_move_finished()
        self.assertFalse(self.pet_window.is_moving, "移动完成后应该不再移动")
    
    def test_pause_resume_animation(self):
        """测试动画暂停和恢复"""
        # 加载动画
        self.pet_window.load_animation("walk")
        
        # 暂停
        if self.pet_window.movie:
            result = self.pet_window.pause_animation()
            # 只有在动画正在播放时才能暂停
            if self.pet_window.movie.state() == QMovie.Running:
                self.assertTrue(self.pet_window.animation_paused, 
                               "暂停后应该标记为已暂停")
        
            # 恢复
            result = self.pet_window.resume_animation()
            if result:
                self.assertFalse(self.pet_window.animation_paused, 
                                "恢复后应该取消暂停标记")
    
    def test_cleanup(self):
        """测试资源清理"""
        # 启动一些定时器
        self.pet_window.auto_move_timer.start(1000)
        self.pet_window.random_action_timer.start(1000)
        
        # 执行清理
        self.pet_window.cleanup()
        
        # 检查定时器是否已停止
        self.assertFalse(self.pet_window.auto_move_timer.isActive(), 
                        "清理后自动移动定时器应该停止")
        self.assertFalse(self.pet_window.random_action_timer.isActive(), 
                        "清理后随机动作定时器应该停止")
    
    def test_drag_animation(self):
        """测试拖动时的动画"""
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QMouseEvent
        
        # 模拟鼠标按下
        pos = QPoint(64, 64)
        event = QMouseEvent(QMouseEvent.MouseButtonPress, pos, Qt.LeftButton, 
                           Qt.LeftButton, Qt.NoModifier)
        self.pet_window.mousePressEvent(event)
        self.assertTrue(self.pet_window.is_dragging, "应该标记为正在拖动")
        
        # 模拟鼠标移动
        new_pos = QPoint(100, 100)
        move_event = QMouseEvent(QMouseEvent.MouseMove, new_pos, Qt.LeftButton, 
                                Qt.LeftButton, Qt.NoModifier)
        self.pet_window.mouseMoveEvent(move_event)
        self.assertEqual(self.pet_window.current_animation, "walk", 
                        "拖动时应该播放walk动画")
        
        # 模拟鼠标释放
        release_event = QMouseEvent(QMouseEvent.MouseButtonRelease, new_pos, 
                                   Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        self.pet_window.mouseReleaseEvent(release_event)
        self.assertFalse(self.pet_window.is_dragging, "释放后应该不再拖动")
    
    def test_animation_config(self):
        """测试动画配置"""
        config = self.pet_window.animation_config
        
        # 检查配置项
        self.assertIn('enable_animation', config, "应该有enable_animation配置")
        self.assertIn('animation_speed', config, "应该有animation_speed配置")
        self.assertIn('durations', config, "应该有durations配置")
        
        # 检查速度配置
        self.assertIsInstance(config['animation_speed'], float, 
                             "动画速度应该是浮点数")
        self.assertGreater(config['animation_speed'], 0, 
                          "动画速度应该大于0")
    
    def test_bounce_jump(self):
        """测试弹跳动画"""
        initial_pos = self.pet_window.pos()
        
        # 执行弹跳
        self.pet_window.bounce_jump()
        
        # 检查是否有弹跳动画引用
        self.assertTrue(hasattr(self.pet_window, '_bounce_animations'), 
                       "应该有弹跳动画引用")


class TestAnimationPerformance(unittest.TestCase):
    """动画性能测试"""
    
    def test_preload_speed(self):
        """测试预加载速度"""
        import time
        from src.pet_window import PetWindow
        
        test_config = {
            'Animation': {'enable_animation': 'true'}
        }
        
        start_time = time.time()
        pet_window = PetWindow(config=test_config)
        load_time = time.time() - start_time
        
        # 预加载应该在1秒内完成
        self.assertLess(load_time, 1.0, "预加载应该在1秒内完成")
        
        pet_window.cleanup()
        pet_window.close()
    
    def test_animation_switching_speed(self):
        """测试动画切换速度"""
        import time
        from src.pet_window import PetWindow
        
        pet_window = PetWindow()
        
        # 测试连续切换动画的速度
        animations = ["idle", "walk", "happy", "sleep", "alert"]
        start_time = time.time()
        
        for anim in animations * 10:  # 切换50次
            pet_window.load_animation(anim)
        
        switch_time = time.time() - start_time
        avg_time = switch_time / 50
        
        # 平均每次切换应该少于10ms
        self.assertLess(avg_time, 0.01, f"平均切换时间应该<10ms，实际{avg_time*1000:.2f}ms")
        
        pet_window.cleanup()
        pet_window.close()


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestPetAnimation))
    suite.addTests(loader.loadTestsFromTestCase(TestAnimationPerformance))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

