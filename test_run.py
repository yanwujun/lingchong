#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试运行脚本 - 快速测试应用是否能正常启动
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("测试桌面灵宠应用启动")
print("=" * 60)

try:
    print("\n[1/5] 测试导入模块...")
    from PyQt5.QtWidgets import QApplication
    from src.utils import load_config
    from src.database import Database
    from src.pet_window import PetWindow
    from src.todo_window import TodoWindow
    from src.settings_window import SettingsWindow
    from src.reminder import ReminderSystem
    from src.tray_icon import SystemTray
    print("  ✓ 所有模块导入成功")
    
    print("\n[2/5] 测试配置加载...")
    config = load_config("config.ini")
    print(f"  ✓ 配置加载成功，包含 {len(config)} 个配置段")
    
    print("\n[3/5] 测试数据库...")
    db = Database("data/test_tasks.db")
    print("  ✓ 数据库初始化成功")
    db.close()
    
    print("\n[4/5] 测试资源文件...")
    import os
    idle_exists = os.path.exists("assets/images/default/idle.png")
    tray_exists = os.path.exists("assets/icons/tray_icon.png")
    print(f"  idle.png: {'✓' if idle_exists else '✗'}")
    print(f"  tray_icon.png: {'✓' if tray_exists else '✗'}")
    
    print("\n[5/5] 测试启动应用...")
    print("  如果窗口正常显示，测试成功！")
    print("  按 Ctrl+C 或右键菜单退出")
    print("\n" + "=" * 60)
    
    # 实际启动应用
    from main import main
    sys.exit(main())
    
except Exception as e:
    print(f"\n[错误] 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

