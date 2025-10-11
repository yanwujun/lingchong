#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
宠物成长系统模块
Pet Growth System Module - 经验、等级、属性和进化管理
"""

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from datetime import datetime, timedelta
from typing import Optional, Dict
import math

class PetGrowthSystem(QObject):
    """宠物成长系统"""
    
    # 信号
    level_up = pyqtSignal(int, int)  # 升级信号（旧等级，新等级）
    evolution = pyqtSignal(int)  # 进化信号（进化阶段）
    attribute_changed = pyqtSignal(str, int)  # 属性变化信号（属性名，新值）
    achievement_unlocked = pyqtSignal(str)  # 成就解锁信号
    
    # 经验值配置
    EXP_PER_TASK = 5  # 完成任务获得的经验
    EXP_PER_POMODORO = 3  # 完成番茄钟获得的经验
    EXP_PER_LEVEL = 100  # 每级所需经验
    
    # 进化阶段配置
    EVOLUTION_STAGES = {
        1: {'name': '幼年期', 'level': 1},
        2: {'name': '成长期', 'level': 10},
        3: {'name': '成熟期', 'level': 25},
        4: {'name': '完全体', 'level': 50}
    }
    
    # 属性衰减配置
    ATTRIBUTE_DECAY_RATE = 5  # 每小时衰减5点
    ATTRIBUTE_DECAY_INTERVAL = 3600  # 1小时（秒）
    
    def __init__(self, database=None, pet_id=None):
        super().__init__()
        
        self.database = database
        self.pet_id = pet_id
        self.pet_data = None
        
        # 属性衰减定时器
        self.decay_timer = QTimer()
        self.decay_timer.timeout.connect(self.apply_attribute_decay)
        
        # 加载宠物数据
        if self.pet_id and self.database:
            self.load_pet_data()
            # 启动衰减定时器（每10分钟检查一次，实际测试可以调整）
            self.decay_timer.start(600000)  # 10分钟
        
        print("[宠物成长] 系统初始化完成")
    
    def load_pet_data(self):
        """加载宠物数据"""
        if not self.database or not self.pet_id:
            return False
        
        self.pet_data = self.database.get_pet(self.pet_id)
        
        if self.pet_data:
            print(f"[宠物成长] 已加载宠物: {self.pet_data['name']} Lv.{self.pet_data['level']}")
            return True
        return False
    
    def add_experience(self, amount: int, source: str = "unknown") -> bool:
        """
        增加经验值
        
        Args:
            amount: 经验值数量
            source: 经验来源
        
        Returns:
            是否升级
        """
        if not self.pet_data or not self.database:
            return False
        
        old_exp = self.pet_data['experience']
        old_level = self.pet_data['level']
        
        # 增加经验
        new_exp = old_exp + amount
        self.pet_data['experience'] = new_exp
        
        # 计算新等级
        new_level = self.calculate_level(new_exp)
        level_up_occurred = False
        
        if new_level > old_level:
            self.pet_data['level'] = new_level
            level_up_occurred = True
            
            # 更新数据库
            self.database.update_pet(
                self.pet_id,
                experience=new_exp,
                level=new_level
            )
            
            # 发送升级信号
            self.level_up.emit(old_level, new_level)
            print(f"[宠物成长] 升级! {old_level} → {new_level}")
            
            # 检查进化
            self.check_evolution(new_level)
            
            # 检查成就
            self.check_level_achievements(new_level)
        else:
            # 只更新经验
            self.database.update_pet(self.pet_id, experience=new_exp)
        
        print(f"[宠物成长] +{amount}EXP (来源:{source}) 当前:{new_exp}/{self.exp_for_next_level()}")
        
        return level_up_occurred
    
    def calculate_level(self, experience: int) -> int:
        """
        根据经验值计算等级
        
        Args:
            experience: 经验值
        
        Returns:
            等级
        """
        return (experience // self.EXP_PER_LEVEL) + 1
    
    def exp_for_next_level(self) -> int:
        """获取升级所需经验"""
        if not self.pet_data:
            return self.EXP_PER_LEVEL
        
        current_level = self.pet_data['level']
        return current_level * self.EXP_PER_LEVEL
    
    def exp_progress(self) -> float:
        """
        获取当前等级的经验进度
        
        Returns:
            0.0 到 1.0
        """
        if not self.pet_data:
            return 0.0
        
        current_exp = self.pet_data['experience']
        current_level = self.pet_data['level']
        
        exp_for_current = (current_level - 1) * self.EXP_PER_LEVEL
        exp_for_next = current_level * self.EXP_PER_LEVEL
        
        progress = (current_exp - exp_for_current) / (exp_for_next - exp_for_current)
        return max(0.0, min(1.0, progress))
    
    def check_evolution(self, level: int):
        """检查是否可以进化"""
        if not self.pet_data:
            return
        
        current_stage = self.pet_data.get('evolution_stage', 1)
        
        # 遍历进化阶段，找到应该进化到的阶段
        for stage, config in self.EVOLUTION_STAGES.items():
            if stage > current_stage and level >= config['level']:
                # 可以进化
                self.pet_data['evolution_stage'] = stage
                self.database.update_pet(self.pet_id, evolution_stage=stage)
                
                self.evolution.emit(stage)
                print(f"[宠物成长] 进化! 进入{config['name']}")
                
                # 进化奖励
                self.evolution_reward(stage)
                break
    
    def evolution_reward(self, stage: int):
        """进化奖励"""
        # 恢复所有属性
        self.set_attribute('hunger', 100)
        self.set_attribute('happiness', 100)
        self.set_attribute('health', 100)
        self.set_attribute('energy', 100)
        
        print(f"[宠物成长] 进化奖励：所有属性已恢复！")
    
    def set_attribute(self, attr_name: str, value: int) -> bool:
        """
        设置属性值
        
        Args:
            attr_name: 属性名称
            value: 属性值
        
        Returns:
            是否成功
        """
        if not self.pet_data or not self.database:
            return False
        
        # 限制属性范围 0-100
        value = max(0, min(100, value))
        
        if attr_name in ['hunger', 'happiness', 'health', 'energy']:
            self.pet_data[attr_name] = value
            self.database.update_pet(self.pet_id, **{attr_name: value})
            self.attribute_changed.emit(attr_name, value)
            return True
        
        return False
    
    def modify_attribute(self, attr_name: str, delta: int) -> int:
        """
        修改属性值（相对变化）
        
        Args:
            attr_name: 属性名称
            delta: 变化量
        
        Returns:
            新的属性值
        """
        if not self.pet_data:
            return 0
        
        current_value = self.pet_data.get(attr_name, 100)
        new_value = max(0, min(100, current_value + delta))
        
        self.set_attribute(attr_name, new_value)
        
        return new_value
    
    def apply_attribute_decay(self):
        """应用属性自然衰减"""
        if not self.pet_data or not self.database:
            return
        
        # 检查上次更新时间
        last_update = self.pet_data.get('last_played_at')
        if not last_update:
            # 首次，设置当前时间
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.database.update_pet(self.pet_id, last_played_at=now)
            return
        
        try:
            last_time = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            elapsed_hours = (now - last_time).total_seconds() / 3600
            
            # 如果超过1小时，应用衰减
            if elapsed_hours >= 1:
                decay_amount = int(elapsed_hours * self.ATTRIBUTE_DECAY_RATE)
                
                # 应用衰减到所有属性
                self.modify_attribute('hunger', -decay_amount)
                self.modify_attribute('happiness', -decay_amount)
                self.modify_attribute('health', -decay_amount)
                self.modify_attribute('energy', -decay_amount)
                
                # 更新时间
                self.database.update_pet(self.pet_id, last_played_at=now.strftime("%Y-%m-%d %H:%M:%S"))
                
                print(f"[宠物成长] 属性衰减: -{decay_amount} (经过{elapsed_hours:.1f}小时)")
        except Exception as e:
            print(f"[宠物成长] 属性衰减计算错误: {e}")
    
    def feed(self, food_value: int = 20) -> bool:
        """
        喂食
        
        Args:
            food_value: 食物恢复值
        
        Returns:
            是否成功
        """
        if not self.pet_data or not self.database:
            return False
        
        self.modify_attribute('hunger', food_value)
        self.modify_attribute('happiness', 5)  # 喂食也增加一点心情
        
        # 更新喂食时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.database.update_pet(self.pet_id, last_fed_at=now)
        
        print(f"[宠物成长] 喂食完成 +{food_value}饱食度")
        return True
    
    def play(self, play_value: int = 15) -> bool:
        """
        玩耍
        
        Args:
            play_value: 玩耍恢复值
        
        Returns:
            是否成功
        """
        if not self.pet_data or not self.database:
            return False
        
        self.modify_attribute('happiness', play_value)
        self.modify_attribute('energy', -10)  # 玩耍消耗能量
        
        # 更新玩耍时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.database.update_pet(self.pet_id, last_played_at=now)
        
        # 可能获得经验
        self.add_experience(2, "玩耍")
        
        print(f"[宠物成长] 玩耍完成 +{play_value}心情")
        return True
    
    def rest(self, rest_value: int = 25) -> bool:
        """
        休息
        
        Args:
            rest_value: 休息恢复值
        
        Returns:
            是否成功
        """
        if not self.pet_data:
            return False
        
        self.modify_attribute('energy', rest_value)
        self.modify_attribute('health', 10)  # 休息也恢复一点健康
        
        print(f"[宠物成长] 休息完成 +{rest_value}能量")
        return True
    
    def check_level_achievements(self, level: int):
        """检查等级相关成就"""
        achievements = [
            (5, "新手上路", "达到5级"),
            (10, "初露锋芒", "达到10级"),
            (25, "经验丰富", "达到25级"),
            (50, "大师级别", "达到50级"),
            (100, "传奇", "达到100级")
        ]
        
        for required_level, name, desc in achievements:
            if level == required_level:
                if self.database:
                    self.database.unlock_achievement(
                        self.pet_id,
                        'level',
                        name,
                        desc
                    )
                self.achievement_unlocked.emit(name)
    
    def get_status(self) -> Dict:
        """
        获取宠物状态
        
        Returns:
            状态字典
        """
        if not self.pet_data:
            return {}
        
        return {
            'name': self.pet_data.get('name', '未命名'),
            'level': self.pet_data.get('level', 1),
            'experience': self.pet_data.get('experience', 0),
            'exp_progress': self.exp_progress(),
            'evolution_stage': self.pet_data.get('evolution_stage', 1),
            'hunger': self.pet_data.get('hunger', 100),
            'happiness': self.pet_data.get('happiness', 100),
            'health': self.pet_data.get('health', 100),
            'energy': self.pet_data.get('energy', 100),
        }
    
    def get_evolution_name(self) -> str:
        """获取当前进化阶段名称"""
        if not self.pet_data:
            return "未知"
        
        stage = self.pet_data.get('evolution_stage', 1)
        return self.EVOLUTION_STAGES.get(stage, {}).get('name', '未知')


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("宠物成长系统测试")
    print("=" * 60)
    
    # 创建成长系统
    growth = PetGrowthSystem()
    
    # 模拟宠物数据
    growth.pet_data = {
        'id': 1,
        'name': '测试宠物',
        'level': 1,
        'experience': 0,
        'hunger': 100,
        'happiness': 100,
        'health': 100,
        'energy': 100,
        'evolution_stage': 1
    }
    
    # 测试增加经验
    print("\n测试经验系统:")
    for i in range(25):
        growth.add_experience(5, "任务")
    
    # 测试属性系统
    print("\n测试属性系统:")
    growth.feed(20)
    growth.play(15)
    growth.rest(25)
    
    # 显示状态
    print("\n当前状态:")
    status = growth.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

