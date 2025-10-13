#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
成就系统模块
Pet Achievements Module - 成就定义、解锁检测和展示
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QGridLayout, QFrame, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from typing import List, Dict
import sys

# 导入现代化UI组件
try:
    from src.modern_ui import ModernButton, ModernCard, COLORS
except ImportError:
    try:
        from modern_ui import ModernButton, ModernCard, COLORS
    except ImportError:
        # 回退到原始组件
        ModernButton = QWidget  # 这里用QWidget代替，因为原始代码中没有按钮
        ModernCard = QFrame
        COLORS = {'background': '#e0e5ec', 'surface': '#e0e5ec', 'success': '#48bb78', 'shadow_dark': '#a3b1c6', 'shadow_light': '#ffffff', 'divider': '#cbd5e0'}

# 成就定义
ACHIEVEMENTS = {
    # 等级成就
    'level_5': {'name': '新手上路', 'desc': '达到5级', 'icon': '🌱', 'type': 'level'},
    'level_10': {'name': '初露锋芒', 'desc': '达到10级', 'icon': '🌿', 'type': 'level'},
    'level_25': {'name': '经验丰富', 'desc': '达到25级', 'icon': '🌳', 'type': 'level'},
    'level_50': {'name': '大师级别', 'desc': '达到50级', 'icon': '🏆', 'type': 'level'},
    'level_100': {'name': '传奇', 'desc': '达到100级', 'icon': '👑', 'type': 'level'},
    
    # 任务成就
    'task_10': {'name': '小有成就', 'desc': '完成10个任务', 'icon': '📝', 'type': 'task'},
    'task_50': {'name': '勤奋工作', 'desc': '完成50个任务', 'icon': '📚', 'type': 'task'},
    'task_100': {'name': '任务达人', 'desc': '完成100个任务', 'icon': '🎯', 'type': 'task'},
    'task_500': {'name': '工作狂', 'desc': '完成500个任务', 'icon': '💼', 'type': 'task'},
    
    # 番茄钟成就
    'pomodoro_10': {'name': '专注新手', 'desc': '完成10个番茄钟', 'icon': '🍅', 'type': 'pomodoro'},
    'pomodoro_50': {'name': '专注达人', 'desc': '完成50个番茄钟', 'icon': '🎓', 'type': 'pomodoro'},
    'pomodoro_100': {'name': '专注大师', 'desc': '完成100个番茄钟', 'icon': '🧘', 'type': 'pomodoro'},
    
    # 连续成就
    'streak_7': {'name': '坚持一周', 'desc': '连续签到7天', 'icon': '📅', 'type': 'streak'},
    'streak_30': {'name': '坚持一月', 'desc': '连续签到30天', 'icon': '📆', 'type': 'streak'},
    'streak_100': {'name': '百日坚持', 'desc': '连续签到100天', 'icon': '🎊', 'type': 'streak'},
    
    # 互动成就
    'feed_100': {'name': '美食家', 'desc': '喂食100次', 'icon': '🍖', 'type': 'interact'},
    'play_100': {'name': '玩乐达人', 'desc': '玩耍100次', 'icon': '🎮', 'type': 'interact'},
    
    # 特殊成就
    'first_task': {'name': '第一步', 'desc': '完成第一个任务', 'icon': '✨', 'type': 'special'},
    'first_pomodoro': {'name': '番茄初体验', 'desc': '完成第一个番茄钟', 'icon': '🎉', 'type': 'special'},
    'all_attributes_100': {'name': '完美状态', 'desc': '所有属性达到100', 'icon': '💯', 'type': 'special'},
    'evolution_complete': {'name': '终极进化', 'desc': '达到完全体', 'icon': '🦋', 'type': 'special'},
}


class AchievementCard(QFrame):
    """成就卡片"""
    
    def __init__(self, achievement_id: str, achievement_data: Dict, unlocked: bool = False):
        super().__init__()
        self.achievement_id = achievement_id
        self.achievement_data = achievement_data
        self.unlocked = unlocked
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedSize(150, 180)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # 图标
        icon_label = QLabel(self.achievement_data['icon'])
        icon_label.setFont(QFont("", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # 名称
        name_label = QLabel(self.achievement_data['name'])
        name_label.setFont(QFont("", 12, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # 描述
        desc_label = QLabel(self.achievement_data['desc'])
        desc_label.setFont(QFont("", 10))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # 状态
        if self.unlocked:
            status_label = QLabel("✅ 已解锁")
            status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            status_label = QLabel("🔒 未解锁")
            status_label.setStyleSheet("color: #999;")
        
        status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(status_label)
        
        self.setLayout(layout)
        
        # 样式
        if self.unlocked:
            self.setStyleSheet(f"""
                AchievementCard {{
                    background-color: {COLORS['surface']};
                    border: 2px solid {COLORS['success']};
                    border-radius: 12px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                AchievementCard {{
                    background-color: {COLORS['background']};
                    border: 2px solid {COLORS['divider']};
                    border-radius: 12px;
                    opacity: 0.6;
                }}
            """)


class AchievementsWindow(QWidget):
    """成就展示窗口"""
    
    def __init__(self, database=None, pet_id=None):
        super().__init__()
        self.database = database
        self.pet_id = pet_id
        self.init_ui()
        self.load_achievements()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("🏆 成就系统")
        self.setGeometry(100, 100, 900, 700)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("🏆 成就墙")
        title_label.setFont(QFont("", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 统计信息
        self.stats_label = QLabel("已解锁: 0 / 0")
        self.stats_label.setFont(QFont("", 14))
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #f0f0f0; }")
        
        # 成就网格容器
        container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        container.setLayout(self.grid_layout)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # 关闭按钮
        close_btn_layout = QHBoxLayout()
        close_btn = ModernButton("❌ 关闭", style="secondary")
        close_btn.clicked.connect(self.close)
        close_btn_layout.addStretch()
        close_btn_layout.addWidget(close_btn)
        layout.addLayout(close_btn_layout)
        
        self.setLayout(layout)
        
        # 窗口样式
        self.setStyleSheet(f"QWidget {{ background-color: {COLORS['background']}; }}")
    
    def load_achievements(self):
        """加载成就数据"""
        # 清空现有网格
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        # 获取已解锁的成就
        unlocked_achievements = set()
        if self.database and self.pet_id:
            achievements = self.database.get_pet_achievements(self.pet_id)
            unlocked_achievements = {ach['achievement_name'] for ach in achievements}
        
        # 按类型分组显示
        row = 0
        col = 0
        max_cols = 5
        
        for ach_id, ach_data in ACHIEVEMENTS.items():
            unlocked = ach_data['name'] in unlocked_achievements
            
            card = AchievementCard(ach_id, ach_data, unlocked)
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 更新统计
        total = len(ACHIEVEMENTS)
        unlocked_count = len(unlocked_achievements)
        self.stats_label.setText(f"已解锁: {unlocked_count} / {total}")
        
        print(f"[成就系统] 已加载 {total} 个成就，已解锁 {unlocked_count} 个")
    
    def closeEvent(self, event):
        """关闭事件"""
        event.ignore()
        self.hide()


class AchievementChecker:
    """成就检查器 - 检测成就解锁条件"""
    
    def __init__(self, database=None, pet_id=None):
        self.database = database
        self.pet_id = pet_id
    
    def check_task_achievements(self, task_count: int):
        """检查任务相关成就"""
        milestones = [
            (1, 'first_task'),
            (10, 'task_10'),
            (50, 'task_50'),
            (100, 'task_100'),
            (500, 'task_500'),
        ]
        
        for count, ach_id in milestones:
            if task_count == count:
                self.unlock_achievement(ach_id)
    
    def check_pomodoro_achievements(self, pomodoro_count: int):
        """检查番茄钟相关成就"""
        milestones = [
            (1, 'first_pomodoro'),
            (10, 'pomodoro_10'),
            (50, 'pomodoro_50'),
            (100, 'pomodoro_100'),
        ]
        
        for count, ach_id in milestones:
            if pomodoro_count == count:
                self.unlock_achievement(ach_id)
    
    def check_level_achievements(self, level: int):
        """检查等级相关成就"""
        milestones = [
            (5, 'level_5'),
            (10, 'level_10'),
            (25, 'level_25'),
            (50, 'level_50'),
            (100, 'level_100'),
        ]
        
        for lvl, ach_id in milestones:
            if level == lvl:
                self.unlock_achievement(ach_id)
    
    def check_attributes(self, hunger, happiness, health, energy):
        """检查属性相关成就"""
        if hunger == 100 and happiness == 100 and health == 100 and energy == 100:
            self.unlock_achievement('all_attributes_100')
    
    def unlock_achievement(self, achievement_id: str):
        """解锁成就"""
        if not self.database or not self.pet_id:
            return
        
        if achievement_id not in ACHIEVEMENTS:
            return
        
        ach_data = ACHIEVEMENTS[achievement_id]
        
        self.database.unlock_achievement(
            self.pet_id,
            ach_data['type'],
            ach_data['name'],
            ach_data['desc']
        )
        
        print(f"[成就系统] 🎉 解锁成就: {ach_data['icon']} {ach_data['name']}")


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = AchievementsWindow()
    window.show()
    
    sys.exit(app.exec_())

