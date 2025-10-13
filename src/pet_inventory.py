#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
道具系统模块
Pet Inventory Module - 道具定义、背包管理和使用效果
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QPushButton,
                             QGroupBox, QApplication, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from typing import Dict, List
import sys

# 导入现代化UI组件
try:
    from src.modern_ui import ModernButton, ModernCard, ModernListWidget, COLORS
except ImportError:
    try:
        from modern_ui import ModernButton, ModernCard, ModernListWidget, COLORS
    except ImportError:
        # 回退到原始组件
        ModernButton = QPushButton
        ModernCard = QGroupBox
        ModernListWidget = QListWidget
        COLORS = {'background': '#e0e5ec', 'surface': '#e0e5ec', 'primary': '#6366f1'}

# 道具定义
ITEMS = {
    # 食物类
    'apple': {'name': '苹果', 'type': 'food', 'icon': '🍎', 'effect': {'hunger': 15}, 'desc': '新鲜的苹果，恢复15点饱食度'},
    'bread': {'name': '面包', 'type': 'food', 'icon': '🍞', 'effect': {'hunger': 20}, 'desc': '香喷喷的面包，恢复20点饱食度'},
    'meat': {'name': '肉类', 'type': 'food', 'icon': '🍖', 'effect': {'hunger': 30}, 'desc': '营养丰富的肉类，恢复30点饱食度'},
    'cake': {'name': '蛋糕', 'type': 'food', 'icon': '🍰', 'effect': {'hunger': 25, 'happiness': 10}, 'desc': '美味的蛋糕，恢复饱食度和心情'},
    
    # 玩具类
    'ball': {'name': '小球', 'type': 'toy', 'icon': '⚽', 'effect': {'happiness': 15, 'energy': -5}, 'desc': '有趣的小球，增加心情但消耗能量'},
    'yarn': {'name': '毛线球', 'type': 'toy', 'icon': '🧶', 'effect': {'happiness': 20, 'energy': -8}, 'desc': '猫咪最爱的毛线球'},
    'stick': {'name': '木棍', 'type': 'toy', 'icon': '🦴', 'effect': {'happiness': 18, 'energy': -10}, 'desc': '狗狗最爱的木棍'},
    
    # 药品类
    'medicine': {'name': '药品', 'type': 'medicine', 'icon': '💊', 'effect': {'health': 30}, 'desc': '治疗疾病，恢复30点健康'},
    'vitamin': {'name': '维生素', 'type': 'medicine', 'icon': '💉', 'effect': {'health': 20, 'energy': 15}, 'desc': '增强体质，恢复健康和能量'},
    
    # 恢复类
    'energy_drink': {'name': '能量饮料', 'type': 'recovery', 'icon': '🥤', 'effect': {'energy': 40}, 'desc': '快速恢复40点能量'},
    'sleep_pillow': {'name': '睡眠枕头', 'type': 'recovery', 'icon': '🛏️', 'effect': {'energy': 50, 'health': 15}, 'desc': '舒适的睡眠，大幅恢复能量'},
    
    # 装备类
    'collar': {'name': '项圈', 'type': 'equipment', 'icon': '📿', 'effect': {'happiness': 5}, 'desc': '漂亮的项圈，永久+5心情（装备时）'},
    'hat': {'name': '帽子', 'type': 'equipment', 'icon': '🎩', 'effect': {'happiness': 8}, 'desc': '时尚的帽子，永久+8心情（装备时）'},
    'scarf': {'name': '围巾', 'type': 'equipment', 'icon': '🧣', 'effect': {'health': 10}, 'desc': '温暖的围巾，永久+10健康（装备时）'},
}


class InventoryWindow(QWidget):
    """背包窗口"""
    
    # 信号
    item_used = pyqtSignal(str)  # 道具使用信号
    
    def __init__(self, database=None, pet_id=None, growth_system=None):
        super().__init__()
        self.database = database
        self.pet_id = pet_id
        self.growth_system = growth_system
        self.init_ui()
        self.load_inventory()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("🎒 背包")
        self.setGeometry(100, 100, 600, 500)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("🎒 道具背包")
        title_label.setFont(QFont("", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 主要内容区域
        content_layout = QHBoxLayout()
        
        # 左侧：道具列表
        list_group = ModernCard()
        list_layout = QVBoxLayout(list_group)
        
        list_title = QLabel("道具列表")
        list_title.setFont(QFont("", 14, QFont.Bold))
        list_layout.addWidget(list_title)
        
        self.item_list = ModernListWidget()
        self.item_list.itemClicked.connect(self.on_item_selected)
        list_layout.addWidget(self.item_list)
        
        content_layout.addWidget(list_group, 2)
        
        # 右侧：道具详情
        detail_group = ModernCard()
        detail_layout = QVBoxLayout()
        
        self.item_icon = QLabel("❓")
        self.item_icon.setFont(QFont("", 64))
        self.item_icon.setAlignment(Qt.AlignCenter)
        detail_layout.addWidget(self.item_icon)
        
        self.item_name = QLabel("选择一个道具")
        self.item_name.setFont(QFont("", 14, QFont.Bold))
        self.item_name.setAlignment(Qt.AlignCenter)
        detail_layout.addWidget(self.item_name)
        
        self.item_desc = QLabel("")
        self.item_desc.setWordWrap(True)
        self.item_desc.setAlignment(Qt.AlignCenter)
        detail_layout.addWidget(self.item_desc)
        
        self.item_effect = QLabel("")
        self.item_effect.setWordWrap(True)
        self.item_effect.setAlignment(Qt.AlignCenter)
        self.item_effect.setStyleSheet("color: #4CAF50; font-weight: bold;")
        detail_layout.addWidget(self.item_effect)
        
        # 使用按钮
        self.use_btn = ModernButton("✨ 使用", style="primary")
        self.use_btn.clicked.connect(self.use_item)
        self.use_btn.setEnabled(False)
        detail_layout.addWidget(self.use_btn)
        
        detail_layout.addStretch()
        detail_group.setLayout(detail_layout)
        content_layout.addWidget(detail_group, 1)
        
        layout.addLayout(content_layout)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        refresh_btn = ModernButton("🔄 刷新", style="secondary")
        refresh_btn.clicked.connect(self.load_inventory)
        
        close_btn = ModernButton("❌ 关闭", style="secondary")
        close_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 样式
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-size: 13px;
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
            QGroupBox {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
        """)
    
    def load_inventory(self):
        """加载背包数据"""
        self.item_list.clear()
        
        if not self.database or not self.pet_id:
            return
        
        inventory = self.database.get_inventory(self.pet_id)
        
        if not inventory:
            item = QListWidgetItem("背包是空的")
            self.item_list.addItem(item)
            return
        
        for item_data in inventory:
            item_name = item_data['item_name']
            quantity = item_data['quantity']
            
            # 获取道具信息
            item_info = ITEMS.get(item_name.lower().replace(' ', '_'), {})
            icon = item_info.get('icon', '❓')
            display_name = item_info.get('name', item_name)
            
            item_text = f"{icon} {display_name} x{quantity}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, item_data)
            self.item_list.addItem(item)
        
        print(f"[背包] 已加载 {len(inventory)} 种道具")
    
    def on_item_selected(self, item):
        """选中道具"""
        item_data = item.data(Qt.UserRole)
        
        if not item_data:
            return
        
        item_name = item_data['item_name']
        item_key = item_name.lower().replace(' ', '_')
        item_info = ITEMS.get(item_key, {})
        
        # 更新详情显示
        self.item_icon.setText(item_info.get('icon', '❓'))
        self.item_name.setText(item_info.get('name', item_name))
        self.item_desc.setText(item_info.get('desc', '无描述'))
        
        # 显示效果
        effect = item_info.get('effect', {})
        effect_text = "效果: "
        for attr, value in effect.items():
            attr_names = {
                'hunger': '饱食度',
                'happiness': '心情',
                'health': '健康',
                'energy': '能量'
            }
            attr_name = attr_names.get(attr, attr)
            sign = '+' if value > 0 else ''
            effect_text += f"{attr_name}{sign}{value}  "
        
        self.item_effect.setText(effect_text)
        
        # 启用使用按钮
        self.use_btn.setEnabled(True)
        self.use_btn.setProperty('item_data', item_data)
    
    def use_item(self):
        """使用道具"""
        if not self.growth_system or not self.database:
            QMessageBox.warning(self, "提示", "无法使用道具")
            return
        
        item_data = self.use_btn.property('item_data')
        if not item_data:
            return
        
        item_name = item_data['item_name']
        item_key = item_name.lower().replace(' ', '_')
        item_info = ITEMS.get(item_key, {})
        
        # 应用效果
        effect = item_info.get('effect', {})
        for attr, value in effect.items():
            self.growth_system.modify_attribute(attr, value)
        
        # 减少数量
        if self.database.use_item(self.pet_id, item_name, 1):
            QMessageBox.information(self, "成功", f"使用了 {item_info.get('name', item_name)}！")
            
            # 发送信号
            self.item_used.emit(item_name)
            
            # 刷新列表
            self.load_inventory()
            
            # 清空选择
            self.use_btn.setEnabled(False)
            self.reset_details()
        else:
            QMessageBox.warning(self, "错误", "使用道具失败")
    
    def reset_details(self):
        """重置详情显示"""
        self.item_icon.setText("❓")
        self.item_name.setText("选择一个道具")
        self.item_desc.setText("")
        self.item_effect.setText("")
    
    def closeEvent(self, event):
        """关闭事件"""
        event.ignore()
        self.hide()


class ItemManager:
    """道具管理器 - 便捷的道具操作接口"""
    
    def __init__(self, database=None, pet_id=None):
        self.database = database
        self.pet_id = pet_id
    
    def add_item(self, item_key: str, quantity: int = 1) -> bool:
        """
        添加道具
        
        Args:
            item_key: 道具键名
            quantity: 数量
        
        Returns:
            是否成功
        """
        if not self.database or not self.pet_id:
            return False
        
        if item_key not in ITEMS:
            print(f"[道具管理] 未知道具: {item_key}")
            return False
        
        item_info = ITEMS[item_key]
        
        return self.database.add_item(
            self.pet_id,
            item_info['name'],
            item_info['type'],
            str(item_info.get('effect', {})),
            quantity
        ) > 0
    
    def give_reward(self, reward_type: str):
        """
        给予奖励
        
        Args:
            reward_type: 奖励类型（task_complete, level_up, achievement等）
        """
        rewards = {
            'task_complete': [('apple', 1)],
            'level_up': [('bread', 2), ('medicine', 1)],
            'achievement': [('cake', 1), ('vitamin', 1)],
            'pomodoro': [('energy_drink', 1)],
        }
        
        items = rewards.get(reward_type, [])
        for item_key, quantity in items:
            self.add_item(item_key, quantity)
        
        if items:
            print(f"[道具管理] 获得奖励: {reward_type}")


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = InventoryWindow()
    window.show()
    
    sys.exit(app.exec_())

