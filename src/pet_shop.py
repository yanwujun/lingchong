#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
宠物商店模块
Pet Shop Module - 宠物和道具购买系统
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QPushButton,
                             QGroupBox, QApplication, QMessageBox, QTabWidget,
                             QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from typing import Dict

# 导入现代化UI组件
try:
    from src.modern_ui import ModernButton, ModernTabWidget, ModernCard, COLORS
except ImportError:
    try:
        from modern_ui import ModernButton, ModernTabWidget, ModernCard, COLORS
    except ImportError:
        # 回退到原始组件
        ModernButton = QPushButton
        ModernTabWidget = QTabWidget
        ModernCard = QFrame
        COLORS = {'background': '#e0e5ec', 'surface': '#e0e5ec', 'primary': '#6366f1', 'primary_light': '#a5b4fc', 'shadow_dark': '#a3b1c6', 'shadow_light': '#ffffff', 'divider': '#cbd5e0'}

# 导入道具定义
try:
    from src.pet_inventory import ITEMS
except ImportError:
    from pet_inventory import ITEMS


# 商店商品定义
SHOP_ITEMS = {
    # 食物
    'apple': {'price': 10, 'category': 'food'},
    'bread': {'price': 15, 'category': 'food'},
    'meat': {'price': 25, 'category': 'food'},
    'cake': {'price': 30, 'category': 'food'},
    
    # 玩具
    'ball': {'price': 20, 'category': 'toy'},
    'yarn': {'price': 25, 'category': 'toy'},
    'stick': {'price': 22, 'category': 'toy'},
    
    # 药品
    'medicine': {'price': 35, 'category': 'medicine'},
    'vitamin': {'price': 40, 'category': 'medicine'},
    
    # 恢复
    'energy_drink': {'price': 30, 'category': 'recovery'},
    'sleep_pillow': {'price': 50, 'category': 'recovery'},
    
    # 装备
    'collar': {'price': 100, 'category': 'equipment'},
    'hat': {'price': 120, 'category': 'equipment'},
    'scarf': {'price': 150, 'category': 'equipment'},
}

# 宠物商品定义
SHOP_PETS = {
    'cat': {'name': '小猫', 'icon': '🐱', 'price': 0, 'desc': '可爱的小猫咪'},
    'dog': {'name': '小狗', 'icon': '🐶', 'price': 200, 'desc': '忠诚的小狗狗'},
    'rabbit': {'name': '兔子', 'icon': '🐰', 'price': 250, 'desc': '软萌的小兔子'},
    'penguin': {'name': '企鹅', 'icon': '🐧', 'price': 300, 'desc': '呆萌的小企鹅'},
    'panda': {'name': '熊猫', 'icon': '🐼', 'price': 500, 'desc': '稀有的熊猫宝宝'},
}


class ShopItemCard(QFrame):
    """商店商品卡片"""
    
    clicked = pyqtSignal(str)  # 点击信号
    
    def __init__(self, item_key: str, item_data: Dict, price: int):
        super().__init__()
        self.item_key = item_key
        self.item_data = item_data
        self.price = price
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setFixedSize(140, 160)
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # 图标
        icon_label = QLabel(self.item_data.get('icon', '❓'))
        icon_label.setFont(QFont("", 40))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # 名称
        name_label = QLabel(self.item_data.get('name', '未知'))
        name_label.setFont(QFont("", 11, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # 价格
        price_label = QLabel(f"💰 {self.price}积分")
        price_label.setFont(QFont("", 10))
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        layout.addWidget(price_label)
        
        self.setLayout(layout)
        
        # 样式
        self.setStyleSheet(f"""
            ShopItemCard {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['divider']};
                border-radius: 12px;
            }}
            ShopItemCard:hover {{
                border: 2px solid {COLORS['primary']};
                background-color: {COLORS['primary_light']};
            }}
        """)
    
    def mousePressEvent(self, event):
        """鼠标点击"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.item_key)


class PetShopWindow(QWidget):
    """宠物商店窗口"""
    
    # 信号
    item_purchased = pyqtSignal(str)  # 购买道具
    pet_purchased = pyqtSignal(str)  # 购买宠物
    
    def __init__(self, database=None, pet_id=None):
        super().__init__()
        self.database = database
        self.pet_id = pet_id
        self.points = 0  # 积分
        self.init_ui()
        self.load_points()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("🛒 宠物商店")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        # 标题和积分
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🛒 宠物商店")
        title_label.setFont(QFont("", 18, QFont.Bold))
        
        self.points_label = QLabel("💰 积分: 0")
        self.points_label.setFont(QFont("", 14, QFont.Bold))
        self.points_label.setStyleSheet("color: #FF9800;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.points_label)
        
        layout.addLayout(header_layout)
        
        # 标签页
        tab_widget = ModernTabWidget()
        
        # 道具商店
        items_tab = self.create_items_tab()
        tab_widget.addTab(items_tab, "🎁 道具")
        
        # 宠物商店
        pets_tab = self.create_pets_tab()
        tab_widget.addTab(pets_tab, "🐾 宠物")
        
        layout.addWidget(tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        refresh_btn = ModernButton("🔄 刷新", style="secondary")
        refresh_btn.clicked.connect(self.load_points)
        
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
        """)
    
    def create_items_tab(self):
        """创建道具商店标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 商品网格容器
        scroll_area = self.create_scroll_area()
        
        from PyQt5.QtWidgets import QGridLayout
        container = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        # 添加商品卡片
        row = 0
        col = 0
        max_cols = 5
        
        for item_key, shop_data in SHOP_ITEMS.items():
            if item_key in ITEMS:
                item_info = ITEMS[item_key]
                card = ShopItemCard(item_key, item_info, shop_data['price'])
                card.clicked.connect(lambda key=item_key, price=shop_data['price']: 
                                   self.buy_item(key, price))
                
                grid_layout.addWidget(card, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
        container.setLayout(grid_layout)
        scroll_area.setWidget(container)
        
        layout.addWidget(scroll_area)
        widget.setLayout(layout)
        return widget
    
    def create_pets_tab(self):
        """创建宠物商店标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 商品网格容器
        scroll_area = self.create_scroll_area()
        
        from PyQt5.QtWidgets import QGridLayout
        container = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        # 添加宠物卡片
        row = 0
        col = 0
        max_cols = 4
        
        for pet_key, pet_data in SHOP_PETS.items():
            card = ShopItemCard(pet_key, pet_data, pet_data['price'])
            card.clicked.connect(lambda key=pet_key, price=pet_data['price']: 
                               self.buy_pet(key, price))
            
            grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        container.setLayout(grid_layout)
        scroll_area.setWidget(container)
        
        layout.addWidget(scroll_area)
        widget.setLayout(layout)
        return widget
    
    def create_scroll_area(self):
        """创建滚动区域"""
        from PyQt5.QtWidgets import QScrollArea
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f0f0f0;
            }
        """)
        return scroll
    
    def load_points(self):
        """加载积分"""
        # 积分计算规则：完成任务+10积分，完成番茄钟+5积分
        if not self.database:
            return
        
        # 获取完成任务数
        tasks = self.database.get_all_tasks()
        completed_tasks = sum(1 for t in tasks if t['status'] == '已完成')
        
        # 获取番茄钟数
        pomodoro_stats = self.database.get_pomodoro_stats(365)  # 一年内
        completed_pomodoros = pomodoro_stats.get('completed_sessions', 0)
        
        # 计算总积分
        self.points = (completed_tasks * 10) + (completed_pomodoros * 5)
        
        self.points_label.setText(f"💰 积分: {self.points}")
        print(f"[商店] 当前积分: {self.points}")
    
    def buy_item(self, item_key: str, price: int):
        """
        购买道具
        
        Args:
            item_key: 道具键
            price: 价格
        """
        if self.points < price:
            QMessageBox.warning(self, "积分不足", f"需要 {price} 积分，当前只有 {self.points} 积分")
            return
        
        # 确认购买
        item_name = ITEMS[item_key]['name']
        reply = QMessageBox.question(
            self, "确认购买",
            f"确定要花费 {price} 积分购买 {item_name} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 添加道具到背包
            if self.database and self.pet_id:
                try:
                    from src.pet_inventory import ItemManager
                except ImportError:
                    from pet_inventory import ItemManager
                
                item_mgr = ItemManager(self.database, self.pet_id)
                if item_mgr.add_item(item_key, 1):
                    # 扣除积分（这里简化处理，实际应该在数据库中记录积分）
                    self.points -= price
                    self.points_label.setText(f"💰 积分: {self.points}")
                    
                    QMessageBox.information(self, "购买成功", f"成功购买 {item_name}！")
                    self.item_purchased.emit(item_key)
                    
                    print(f"[商店] 购买道具: {item_name}, 花费{price}积分")
                else:
                    QMessageBox.warning(self, "错误", "购买失败")
    
    def buy_pet(self, pet_key: str, price: int):
        """
        购买宠物
        
        Args:
            pet_key: 宠物键
            price: 价格
        """
        # 小猫是免费的初始宠物
        if price > 0 and self.points < price:
            QMessageBox.warning(self, "积分不足", f"需要 {price} 积分，当前只有 {self.points} 积分")
            return
        
        # 确认购买
        pet_name = SHOP_PETS[pet_key]['name']
        
        if price == 0:
            QMessageBox.information(self, "提示", f"{pet_name}是免费的初始宠物，请在宠物管理中添加")
            return
        
        reply = QMessageBox.question(
            self, "确认购买",
            f"确定要花费 {price} 积分购买 {pet_name} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 创建新宠物
            if self.database:
                try:
                    from src.pet_manager import PetManager
                except ImportError:
                    from pet_manager import PetManager
                
                pet_mgr = PetManager(self.database)
                
                # 检查宠物数量
                if pet_mgr.get_pet_count() >= 5:
                    QMessageBox.warning(self, "无法购买", "最多只能拥有5只宠物！")
                    return
                
                new_pet_id = pet_mgr.create_pet(f"新{pet_name}", pet_key)
                
                if new_pet_id:
                    # 扣除积分
                    self.points -= price
                    self.points_label.setText(f"💰 积分: {self.points}")
                    
                    QMessageBox.information(self, "购买成功", 
                                          f"成功购买 {pet_name}！\n请重启应用查看新宠物。")
                    self.pet_purchased.emit(pet_key)
                    
                    print(f"[商店] 购买宠物: {pet_name}, 花费{price}积分")
                else:
                    QMessageBox.warning(self, "错误", "购买失败")
    
    def closeEvent(self, event):
        """关闭事件"""
        event.ignore()
        self.hide()


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = PetShopWindow()
    window.show()
    
    sys.exit(app.exec_())

