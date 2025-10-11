#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多宠物管理器模块
Pet Manager Module - 多宠物实例管理和切换
"""

from PyQt5.QtCore import QObject, pyqtSignal
from typing import List, Dict, Optional
import sys

class PetManager(QObject):
    """多宠物管理器"""
    
    # 信号
    pet_added = pyqtSignal(int)  # 添加宠物
    pet_removed = pyqtSignal(int)  # 移除宠物
    active_pet_changed = pyqtSignal(int)  # 切换激活宠物
    
    def __init__(self, database=None):
        super().__init__()
        
        self.database = database
        self.pets = []  # 宠物列表
        self.active_pet_id = None
        self.pet_windows = {}  # pet_id -> PetWindow实例
        
        # 加载所有宠物
        if self.database:
            self.load_pets()
        
        print("[宠物管理器] 初始化完成")
    
    def load_pets(self):
        """从数据库加载所有宠物"""
        if not self.database:
            return
        
        self.pets = self.database.get_all_pets()
        
        # 获取激活的宠物
        active_pet = self.database.get_active_pet()
        if active_pet:
            self.active_pet_id = active_pet['id']
        elif self.pets:
            # 如果没有激活的宠物，激活第一个
            self.active_pet_id = self.pets[0]['id']
            self.database.update_pet(self.active_pet_id, is_active=1)
        
        print(f"[宠物管理器] 已加载 {len(self.pets)} 只宠物")
        if self.active_pet_id:
            print(f"[宠物管理器] 当前激活宠物: ID={self.active_pet_id}")
    
    def create_pet(self, name: str, pet_type: str = 'cat') -> Optional[int]:
        """
        创建新宠物
        
        Args:
            name: 宠物名称
            pet_type: 宠物类型
        
        Returns:
            宠物ID
        """
        if not self.database:
            return None
        
        # 检查宠物数量限制（最多5只）
        if len(self.pets) >= 5:
            print("[宠物管理器] 已达到宠物数量上限（5只）")
            return None
        
        # 创建宠物
        pet_id = self.database.create_pet(name, pet_type)
        
        if pet_id:
            # 重新加载宠物列表
            self.load_pets()
            
            # 发送信号
            self.pet_added.emit(pet_id)
            
            print(f"[宠物管理器] 创建宠物成功: {name} (ID={pet_id})")
            return pet_id
        
        return None
    
    def get_pet(self, pet_id: int) -> Optional[Dict]:
        """获取宠物信息"""
        if not self.database:
            return None
        
        return self.database.get_pet(pet_id)
    
    def get_active_pet(self) -> Optional[Dict]:
        """获取当前激活的宠物"""
        if not self.database or not self.active_pet_id:
            return None
        
        return self.database.get_pet(self.active_pet_id)
    
    def set_active_pet(self, pet_id: int) -> bool:
        """
        设置激活宠物
        
        Args:
            pet_id: 宠物ID
        
        Returns:
            是否成功
        """
        if not self.database:
            return False
        
        # 取消当前激活宠物
        if self.active_pet_id:
            self.database.update_pet(self.active_pet_id, is_active=0)
        
        # 激活新宠物
        if self.database.update_pet(pet_id, is_active=1):
            self.active_pet_id = pet_id
            self.active_pet_changed.emit(pet_id)
            print(f"[宠物管理器] 切换激活宠物: ID={pet_id}")
            return True
        
        return False
    
    def update_pet_position(self, pet_id: int, x: int, y: int) -> bool:
        """
        更新宠物位置
        
        Args:
            pet_id: 宠物ID
            x: X坐标
            y: Y坐标
        
        Returns:
            是否成功
        """
        if not self.database:
            return False
        
        return self.database.update_pet(pet_id, position_x=x, position_y=y)
    
    def get_pet_count(self) -> int:
        """获取宠物数量"""
        return len(self.pets)
    
    def get_all_pets(self) -> List[Dict]:
        """获取所有宠物"""
        return self.pets.copy()
    
    def register_pet_window(self, pet_id: int, window):
        """
        注册宠物窗口实例
        
        Args:
            pet_id: 宠物ID
            window: PetWindow实例
        """
        self.pet_windows[pet_id] = window
        print(f"[宠物管理器] 注册宠物窗口: ID={pet_id}")
    
    def get_pet_window(self, pet_id: int):
        """获取宠物窗口实例"""
        return self.pet_windows.get(pet_id)
    
    def show_all_pets(self):
        """显示所有宠物"""
        for pet_id, window in self.pet_windows.items():
            if window:
                window.show()
        print("[宠物管理器] 显示所有宠物")
    
    def hide_all_pets(self):
        """隐藏所有宠物"""
        for pet_id, window in self.pet_windows.items():
            if window:
                window.hide()
        print("[宠物管理器] 隐藏所有宠物")
    
    def save_all_positions(self):
        """保存所有宠物位置"""
        for pet_id, window in self.pet_windows.items():
            if window:
                pos = window.pos()
                self.update_pet_position(pet_id, pos.x(), pos.y())
        print("[宠物管理器] 保存所有宠物位置")


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    print("=" * 60)
    print("多宠物管理器测试")
    print("=" * 60)
    
    # 创建管理器
    manager = PetManager()
    
    print(f"\n当前宠物数量: {manager.get_pet_count()}")
    print(f"激活宠物ID: {manager.active_pet_id}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

