#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
桌面灵宠 - 主程序入口
Desktop Pet Assistant - Main Entry Point

Author: Your Name
Date: 2025-10-11
Version: 0.4.0
"""

import sys
import os
import io

# 修复Qt平台插件路径问题（必须在导入PyQt5之前）
if sys.platform == 'win32':
    # 方法1: 查找虚拟环境中的插件路径
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pack_env')
    if os.path.exists(venv_path):
        venv_plugin = os.path.join(venv_path, 'Lib', 'site-packages', 'PyQt5', 'Qt5', 'plugins')
        if os.path.exists(venv_plugin):
            os.environ['QT_PLUGIN_PATH'] = venv_plugin
            print(f"[系统] Qt插件路径（虚拟环境）: {venv_plugin}")
    
    # 方法2: 如果虚拟环境没找到，尝试从site-packages查找
    if 'QT_PLUGIN_PATH' not in os.environ:
        try:
            import site
            for sitepack in site.getsitepackages():
                plugin_path = os.path.join(sitepack, 'PyQt5', 'Qt5', 'plugins')
                if os.path.exists(plugin_path):
                    os.environ['QT_PLUGIN_PATH'] = plugin_path
                    print(f"[系统] Qt插件路径: {plugin_path}")
                    break
        except Exception as e:
            print(f"[警告] 查找Qt插件路径失败: {e}")
    
    # 方法3: 如果还是没找到，尝试从PyQt5包目录查找（作为最后的后备方案）
    if 'QT_PLUGIN_PATH' not in os.environ:
        try:
            # 先导入PyQt5来获取路径（虽然可能已经太晚了，但作为后备方案）
            import PyQt5
            pyqt5_dir = os.path.dirname(PyQt5.__file__)
            plugin_path = os.path.join(pyqt5_dir, 'Qt5', 'plugins')
            if os.path.exists(plugin_path):
                os.environ['QT_PLUGIN_PATH'] = plugin_path
                print(f"[系统] Qt插件路径（后备方案）: {plugin_path}")
        except Exception as e:
            print(f"[警告] 设置Qt插件路径失败: {e}")

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass  # 在某些环境下可能不支持

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入各个模块
from src.utils import load_config
from src.database import Database
from src.pet_window import PetWindow
from src.todo_window import TodoWindow
from src.settings_window import SettingsWindow
from src.reminder import ReminderSystem
from src.tray_icon import SystemTray
from src.logger import get_logger


class DesktopPetApp:
    """桌面灵宠应用主类"""
    
    def __init__(self, app):
        """初始化应用"""
        self.app = app
        self.config = None
        self.database = None
        self.pet_window = None
        self.todo_window = None
        self.settings_window = None
        self.reminder_system = None
        self.tray_icon = None
        
        # v0.4.0 新增组件
        self.pet_manager = None  # 多宠物管理器
        self.pet_growth = None  # 宠物成长系统
        self.pomodoro_window = None  # 番茄钟窗口
        self.pomodoro_widget = None  # 番茄钟小组件
        self.chat_window = None  # AI对话窗口
        self.achievements_window = None  # 成就窗口
        self.inventory_window = None  # 背包窗口
        self.shop_window = None  # 商店窗口
        self.image_recognizer = None  # 图片识别器
        
        # v0.5.0 敬业签功能新增组件
        self.note_window = None  # 便签窗口
        self.view_manager = None  # 视图管理器
        self.global_hotkey = None  # 全局快捷键
        self.command_palette = None  # 命令面板
        self.data_exporter = None  # 数据导出器
        self.data_importer = None  # 数据导入器
        self.recurring_reminder = None  # 重复提醒
        
        # 初始化日志系统
        self.logger = get_logger("Main")
        
        try:
            # 初始化各个组件（包含信号连接）
            self.init_components()
        except Exception as e:
            self.logger.exception("应用初始化失败")
            QMessageBox.critical(
                None,
                "启动失败",
                f"应用初始化失败：\n{str(e)}\n\n请查看日志文件获取详细信息。"
            )
            raise
    
    def init_components(self):
        """初始化各个组件"""
        print("\n" + "=" * 60)
        print("桌面灵宠 v0.5.0 - 启动中...")
        print("=" * 60)
        
        # 1. 加载配置
        print("\n[1/15] 加载配置文件...")
        try:
            self.config = load_config("config.ini")
            print("  [OK] 配置加载完成")
            self.logger.info("配置文件加载成功")
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")
            self.config = {}  # 使用空配置
            print(f"  [WARN] 配置加载失败，使用默认配置: {e}")
        
        # 2. 初始化数据库
        print("\n[2/15] 初始化数据库...")
        try:
            db_path = self.config.get('Database', {}).get('db_path', 'data/tasks.db')
            self.database = Database(db_path)
            print("  [OK] 数据库初始化完成")
            self.logger.info(f"数据库初始化成功: {db_path}")
            
            # 自动备份数据库
            auto_backup = self.config.get('Database', {}).get('auto_backup', True)
            if isinstance(auto_backup, str):
                auto_backup = auto_backup.lower() == 'true'
            if auto_backup and os.path.exists(db_path):
                if self.database.auto_backup():
                    print("  [OK] 数据备份完成")
                    self.logger.info("数据库自动备份成功")
        except Exception as e:
            self.logger.exception("数据库初始化失败")
            print(f"  [ERROR] 数据库初始化失败: {e}")
            raise
        
        # 3. 初始化宠物管理器 [v0.4.0]
        print("\n[3/15] 初始化宠物管理器...")
        try:
            from src.pet_manager import PetManager
            self.pet_manager = PetManager(database=self.database)
            
            # 如果没有宠物，创建默认宠物
            if self.pet_manager.get_pet_count() == 0:
                default_pet_id = self.database.create_pet("小宠物", "cat")
                print(f"  [OK] 创建默认宠物: ID={default_pet_id}")
            
            print("  [OK] 宠物管理器初始化完成")
            self.logger.info("宠物管理器初始化成功")
        except Exception as e:
            self.logger.error(f"宠物管理器初始化失败: {e}")
            print(f"  [WARN] 宠物管理器初始化失败: {e}")
        # 4. 初始化宠物成长系统 [v0.4.0]
        print("\n[4/15] 初始化宠物成长系统...")
        try:
            from src.pet_growth import PetGrowthSystem
            active_pet = self.pet_manager.get_active_pet() if self.pet_manager else None
            if active_pet:
                self.pet_growth = PetGrowthSystem(database=self.database, pet_id=active_pet['id'])
                print("  [OK] 宠物成长系统初始化完成")
                self.logger.info("宠物成长系统初始化成功")
            else:
                print("  [WARN] 没有激活的宠物，跳过成长系统初始化")
        except Exception as e:
            self.logger.error(f"宠物成长系统初始化失败: {e}")
            print(f"  [WARN] 宠物成长系统初始化失败: {e}")
        
        # 5. 创建宠物窗口
        print("\n[5/15] 创建宠物窗口...")
        try:
            active_pet = self.pet_manager.get_active_pet() if self.pet_manager else None
            pet_id = active_pet['id'] if active_pet else None
            self.pet_window = PetWindow(config=self.config, pet_id=pet_id)
            print("  [OK] 宠物窗口创建完成")
            self.logger.info("宠物窗口创建成功")
        except Exception as e:
            self.logger.exception("宠物窗口创建失败")
            print(f"  [ERROR] 宠物窗口创建失败: {e}")
            raise
        
        # 6. 创建待办窗口（初始隐藏）
        print("\n[6/15] 创建待办事项窗口...")
        try:
            self.todo_window = TodoWindow(database=self.database)
            print("  [OK] 待办窗口创建完成")
            self.logger.info("待办窗口创建成功")
        except Exception as e:
            self.logger.exception("待办窗口创建失败")
            print(f"  [ERROR] 待办窗口创建失败: {e}")
            # 待办窗口不是必需的，可以继续
            self.todo_window = None
        
        # 7. 创建设置窗口（初始隐藏）
        print("\n[7/15] 创建设置窗口...")
        try:
            self.settings_window = SettingsWindow(config=self.config)
            print("  [OK] 设置窗口创建完成")
            self.logger.info("设置窗口创建成功")
        except Exception as e:
            self.logger.exception("设置窗口创建失败")
            print(f"  [ERROR] 设置窗口创建失败: {e}")
            # 设置窗口不是必需的，可以继续
            self.settings_window = None
        
        # 8. 启动提醒系统
        print("\n[8/15] 启动提醒系统...")
        try:
            self.reminder_system = ReminderSystem(
                database=self.database,
                pet_window=self.pet_window
            )
            self.reminder_system.start(interval=60000)  # 60秒检查一次
            print("  [OK] 提醒系统启动完成")
            self.logger.info("提醒系统启动成功")
        except Exception as e:
            self.logger.exception("提醒系统启动失败")
            print(f"  [ERROR] 提醒系统启动失败: {e}")
            # 提醒系统不是必需的，可以继续
            self.reminder_system = None
        
        # 9. 创建系统托盘
        print("\n[9/15] 创建系统托盘...")
        try:
            self.tray_icon = SystemTray(icon_path="assets/icons/tray_icon.png")
            self.tray_icon.show()
            print("  [OK] 系统托盘创建完成")
            self.logger.info("系统托盘创建成功")
        except Exception as e:
            self.logger.exception("系统托盘创建失败")
            print(f"  [ERROR] 系统托盘创建失败: {e}")
            # 托盘不是必需的，可以继续
            self.tray_icon = None
        
        # ========== v0.4.0 新功能初始化 ==========
        
        # 10. 创建番茄钟系统 [v0.4.0]
        print("\n[10/15] 创建番茄钟系统...")
        try:
            from src.pomodoro_window import PomodoroWindow
            from src.pomodoro_widget import PomodoroWidget
            
            self.pomodoro_window = PomodoroWindow(database=self.database)
            self.pomodoro_widget = PomodoroWidget(pomodoro_manager=self.pomodoro_window.pomodoro_manager)
            
            print("  [OK] 番茄钟系统创建完成")
            self.logger.info("番茄钟系统创建成功")
        except Exception as e:
            self.logger.error(f"番茄钟系统创建失败: {e}")
            print(f"  [WARN] 番茄钟系统创建失败: {e}")
            self.pomodoro_window = None
            self.pomodoro_widget = None
        
        # 11. 创建成就/背包/商店窗口 [v0.4.0]
        print("\n[11/15] 创建成就/背包/商店窗口...")
        try:
            from src.pet_achievements import AchievementsWindow
            from src.pet_inventory import InventoryWindow
            from src.pet_shop import PetShopWindow
            
            active_pet = self.pet_manager.get_active_pet() if self.pet_manager else None
            pet_id = active_pet['id'] if active_pet else None
            
            # 成就窗口
            self.achievements_window = AchievementsWindow(database=self.database, pet_id=pet_id)
            print("  [OK] 成就窗口创建完成")
            
            # 背包窗口
            self.inventory_window = InventoryWindow(
                database=self.database, 
                pet_id=pet_id,
                growth_system=self.pet_growth
            )
            print("  [OK] 背包窗口创建完成")
            
            # 商店窗口
            self.shop_window = PetShopWindow(
                database=self.database,
                pet_id=pet_id
            )
            print("  [OK] 商店窗口创建完成")
            
            self.logger.info("成就/背包/商店窗口创建成功")
        except Exception as e:
            self.logger.error(f"成就/背包/商店窗口创建失败: {e}")
            print(f"  [ERROR] 成就/背包/商店窗口创建失败: {e}")
            self.achievements_window = None
            self.inventory_window = None
            self.shop_window = None
        
        # 12. 创建AI对话窗口 [v0.4.0]
        print("\n[12/15] 创建AI对话窗口...")
        try:
            from src.chat_window import ChatWindow
            active_pet = self.pet_manager.get_active_pet() if self.pet_manager else None
            pet_id = active_pet['id'] if active_pet else None
            
            self.chat_window = ChatWindow(database=self.database, pet_id=pet_id)
            print("  [OK] AI对话窗口创建完成")
            self.logger.info("AI对话窗口创建成功")
        except Exception as e:
            self.logger.error(f"AI对话窗口创建失败: {e}")
            print(f"  [WARN] AI对话窗口创建失败: {e}")
            self.chat_window = None
        
        # 13. 创建图片识别器 [v0.4.0]
        print("\n[13/15] 创建图片识别器...")
        try:
            from src.image_recognizer import ImageRecognizer
            self.image_recognizer = ImageRecognizer(database=self.database)
            print("  [OK] 图片识别器创建完成")
            self.logger.info("图片识别器创建成功")
        except Exception as e:
            self.logger.error(f"图片识别器创建失败: {e}")
            print(f"  [WARN] 图片识别器创建失败: {e}")
            self.image_recognizer = None
        
        # ========== v0.5.0 敬业签功能初始化 ==========
        
        # 14. 创建便签窗口 [v0.5.0]
        print("\n[14/20] 创建便签窗口...")
        try:
            from src.note_window import NoteWindow
            self.note_window = NoteWindow(database=self.database)
            print("  [OK] 便签窗口创建完成")
            self.logger.info("便签窗口创建成功")
        except Exception as e:
            self.logger.error(f"便签窗口创建失败: {e}")
            print(f"  [WARN] 便签窗口创建失败: {e}")
            self.note_window = None
        
        # 15. 创建视图管理器 [v0.5.0]
        print("\n[15/20] 创建视图管理器...")
        try:
            from src.view_manager import ViewManager
            self.view_manager = ViewManager(database=self.database)
            print("  [OK] 视图管理器创建完成")
            self.logger.info("视图管理器创建成功")
        except Exception as e:
            self.logger.error(f"视图管理器创建失败: {e}")
            print(f"  [WARN] 视图管理器创建失败: {e}")
            self.view_manager = None
        
        # 16. 创建全局快捷键 [v0.5.0]
        print("\n[16/20] 创建全局快捷键...")
        try:
            from src.global_hotkey import GlobalHotkeyManager
            self.global_hotkey = GlobalHotkeyManager()
            
            # 注册默认快捷键
            callbacks = {
                'new_note': lambda: self.show_note_window(),
                'open_notes': lambda: self.show_note_window(),
                'command_palette': lambda: self.show_command_palette(),
            }
            self.global_hotkey.register_default_hotkeys(callbacks)
            
            print("  [OK] 全局快捷键创建完成")
            self.logger.info("全局快捷键创建成功")
        except Exception as e:
            self.logger.error(f"全局快捷键创建失败: {e}")
            print(f"  [WARN] 全局快捷键创建失败: {e}")
            self.global_hotkey = None
        
        # 17. 创建数据导入导出器 [v0.5.0]
        print("\n[17/20] 创建数据导入导出器...")
        try:
            from src.data_export import DataExporter
            from src.data_import import DataImporter
            self.data_exporter = DataExporter(self.database)
            self.data_importer = DataImporter(self.database)
            print("  [OK] 数据导入导出器创建完成")
            self.logger.info("数据导入导出器创建成功")
        except Exception as e:
            self.logger.error(f"数据导入导出器创建失败: {e}")
            print(f"  [WARN] 数据导入导出器创建失败: {e}")
            self.data_exporter = None
            self.data_importer = None
        
        # 18. 创建重复提醒系统 [v0.5.0]
        print("\n[18/20] 创建重复提醒系统...")
        try:
            from src.recurring_reminder import RecurringReminder
            self.recurring_reminder = RecurringReminder(self.database)
            print("  [OK] 重复提醒系统创建完成")
            self.logger.info("重复提醒系统创建成功")
        except Exception as e:
            self.logger.error(f"重复提醒系统创建失败: {e}")
            print(f"  [WARN] 重复提醒系统创建失败: {e}")
            self.recurring_reminder = None
        
        # 19. 连接信号
        print("\n[19/20] 连接组件信号...")
        try:
            self.connect_signals()
            print("  [OK] 信号连接完成")
            self.logger.info("信号连接成功")
        except Exception as e:
            self.logger.error(f"信号连接失败: {e}")
            print(f"  [ERROR] 信号连接失败: {e}")
        
        # 20. 检查并显示新手引导 [v0.3.0]
        print("\n[20/20] 检查新手引导...")
        self.show_tutorial_if_needed()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] 所有组件初始化完成！")
        print("=" * 60)
    
    def show_tutorial_if_needed(self):
        """显示新手引导（如果是首次启动）[v0.3.0]"""
        try:
            from src.tutorial import should_show_tutorial, TutorialWindow
            
            if should_show_tutorial():
                print("\n[新手引导] 检测到首次启动，显示引导...")
                tutorial = TutorialWindow(database=self.database)
                tutorial.exec_()
                print("  [OK] 新手引导完成")
                self.logger.info("新手引导已完成")
            else:
                print("\n[新手引导] 跳过（已完成）")
        except Exception as e:
            self.logger.warning(f"新手引导显示失败: {e}")
            print(f"  [WARN] 新手引导显示失败: {e}")
    
    def connect_signals(self):
        """连接各个组件的信号与槽"""
        print("\n[信号连接] 连接各模块信号...")
        
        # 宠物窗口引用其他窗口
        self.pet_window.todo_window = self.todo_window
        self.pet_window.settings_window = self.settings_window
        
        # v0.4.0 新窗口引用
        self.pet_window.pomodoro_window = self.pomodoro_window
        self.pet_window.chat_window = self.chat_window
        self.pet_window.achievements_window = self.achievements_window
        self.pet_window.inventory_window = self.inventory_window
        self.pet_window.shop_window = self.shop_window
        
        # 传递主程序引用（用于延迟创建窗口）
        self.pet_window.main_app = self
        
        # 托盘图标信号
        if self.tray_icon:
            self.tray_icon.show_pet_signal.connect(self.show_pet)
            self.tray_icon.hide_pet_signal.connect(self.hide_pet)
            self.tray_icon.show_todo_signal.connect(self.show_todo)
            self.tray_icon.show_settings_signal.connect(self.show_settings)
            self.tray_icon.quit_signal.connect(self.quit_app)
            
            # v0.5.0 新功能信号
            if hasattr(self.tray_icon, 'show_note_signal'):
                self.tray_icon.show_note_signal.connect(self.show_note_window)
            if hasattr(self.tray_icon, 'show_view_signal'):
                self.tray_icon.show_view_signal.connect(self.show_view_manager)
            if hasattr(self.tray_icon, 'export_signal'):
                self.tray_icon.export_signal.connect(self.export_data)
            if hasattr(self.tray_icon, 'import_signal'):
                self.tray_icon.import_signal.connect(self.import_data)
        
        # 提醒系统信号
        self.reminder_system.completed.connect(self.on_task_completed)
        self.reminder_system.snoozed.connect(self.on_task_snoozed)
        
        # 待办窗口信号
        self.todo_window.task_added.connect(self.on_task_added)
        self.todo_window.task_deleted.connect(self.on_task_deleted)
        
        # 设置窗口信号
        self.settings_window.settings_changed.connect(self.on_settings_changed)
        
        # 主题切换信号 [v0.3.0]
        if hasattr(self.settings_window, 'theme_combo'):
            self.settings_window.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        
        # ========== v0.4.0 新功能信号连接 ==========
        
        # 宠物窗口图片拖放信号
        if self.pet_window and self.image_recognizer:
            self.pet_window.image_dropped.connect(self.on_image_dropped)
        
        # 图片识别信号
        if self.image_recognizer:
            self.image_recognizer.recognition_completed.connect(self.on_image_recognized)
            self.image_recognizer.tasks_generated.connect(self.on_tasks_generated)
            self.image_recognizer.error_occurred.connect(self.on_image_error)
        
        # 宠物成长系统信号
        if self.pet_growth:
            self.pet_growth.level_up.connect(self.on_pet_level_up)
            self.pet_growth.evolution.connect(self.on_pet_evolution)
            self.pet_growth.achievement_unlocked.connect(self.on_achievement_unlocked)
        
        # 番茄钟信号
        if self.pomodoro_window:
            pomodoro_timer = self.pomodoro_window.pomodoro_manager.timer
            pomodoro_timer.session_completed.connect(self.on_pomodoro_completed)
        
        # ========== v0.5.0 新功能信号连接 ==========
        
        # 便签窗口信号
        if self.note_window:
            # 便签窗口的信号连接（如果需要）
            pass
        
        print("  [OK] 信号连接完成")
    
    def show_pet(self):
        """显示宠物窗口"""
        if self.pet_window:
            self.pet_window.show()
            self.pet_window.raise_()
            self.pet_window.activateWindow()
    
    def hide_pet(self):
        """隐藏宠物窗口"""
        if self.pet_window:
            self.pet_window.hide()
    
    def show_todo(self):
        """显示待办窗口"""
        if self.todo_window:
            self.todo_window.show()
            self.todo_window.raise_()
            self.todo_window.activateWindow()
    
    def show_settings(self):
        """显示设置窗口"""
        if self.settings_window:
            self.settings_window.show()
            self.settings_window.raise_()
            self.settings_window.activateWindow()
    
    # ========== v0.5.0 敬业签功能方法 ==========
    
    def show_note_window(self):
        """显示便签窗口 [v0.5.0]"""
        if self.note_window:
            self.note_window.show()
            self.note_window.raise_()
            self.note_window.activateWindow()
    
    def show_view_manager(self):
        """显示视图管理器 [v0.5.0]"""
        if self.view_manager:
            self.view_manager.show()
            self.view_manager.raise_()
            self.view_manager.activateWindow()
    
    def show_command_palette(self):
        """显示命令面板 [v0.5.0]"""
        try:
            from src.command_palette import CommandPalette
            palette = CommandPalette(self.pet_window if self.pet_window else None)
            palette.command_selected.connect(self.handle_command)
            palette.exec_()
        except Exception as e:
            print(f"[命令面板] 显示失败: {e}")
            self.logger.error(f"命令面板显示失败: {e}")
    
    def handle_command(self, command_id: str):
        """处理命令面板命令 [v0.5.0]"""
        command_map = {
            'new_task': self.show_todo,
            'new_note': self.show_note_window,
            'open_todo': self.show_todo,
            'open_notes': self.show_note_window,
            'open_pomodoro': lambda: self.pomodoro_window.show() if self.pomodoro_window else None,
            'open_settings': self.show_settings,
            'export_data': self.export_data,
            'import_data': self.import_data,
            'show_statistics': lambda: self.todo_window.show_statistics() if self.todo_window and hasattr(self.todo_window, 'show_statistics') else None,
        }
        
        handler = command_map.get(command_id)
        if handler:
            try:
                handler()
            except Exception as e:
                print(f"[命令处理] 执行命令 {command_id} 失败: {e}")
                self.logger.error(f"执行命令失败: {command_id} - {e}")
    
    def export_data(self):
        """导出数据 [v0.5.0]"""
        if self.data_exporter:
            try:
                self.data_exporter.export_to_json(parent_widget=self.pet_window if self.pet_window else None)
            except Exception as e:
                print(f"[数据导出] 失败: {e}")
                self.logger.error(f"数据导出失败: {e}")
        else:
            QMessageBox.warning(
                self.pet_window if self.pet_window else None,
                "功能不可用",
                "数据导出功能未初始化"
            )
    
    def import_data(self):
        """导入数据 [v0.5.0]"""
        if self.data_importer:
            try:
                if self.data_importer.import_from_json(parent_widget=self.pet_window if self.pet_window else None):
                    # 刷新窗口
                    if self.todo_window:
                        self.todo_window.load_tasks()
                    if self.note_window:
                        self.note_window.load_notes()
            except Exception as e:
                print(f"[数据导入] 失败: {e}")
                self.logger.error(f"数据导入失败: {e}")
        else:
            QMessageBox.warning(
                self.pet_window if self.pet_window else None,
                "功能不可用",
                "数据导入功能未初始化"
            )
    
    # ========== v0.4.0 新窗口显示方法 ==========
    
    def show_pomodoro(self):
        """显示番茄钟窗口 [v0.4.0]"""
        if self.pomodoro_window:
            self.pomodoro_window.show()
            self.pomodoro_window.raise_()
            self.pomodoro_window.activateWindow()
    
    def show_chat(self):
        """显示AI对话窗口 [v0.4.0]"""
        if self.chat_window:
            self.chat_window.show()
            self.chat_window.raise_()
            self.chat_window.activateWindow()
    
    def show_achievements(self):
        """显示成就窗口 [v0.4.0]"""
        try:
            if not self.achievements_window:
                from src.pet_achievements import AchievementsWindow
                active_pet = self.pet_manager.get_active_pet() if self.pet_manager else None
                pet_id = active_pet['id'] if active_pet else None
                self.achievements_window = AchievementsWindow(database=self.database, pet_id=pet_id)
            
            self.achievements_window.load_achievements()
            self.achievements_window.show()
            self.achievements_window.raise_()
            self.achievements_window.activateWindow()
        except Exception as e:
            print(f"[应用] 打开成就窗口失败: {e}")
    
    def show_inventory(self):
        """显示背包窗口 [v0.4.0]"""
        try:
            if not self.inventory_window:
                from src.pet_inventory import InventoryWindow
                active_pet = self.pet_manager.get_active_pet() if self.pet_manager else None
                pet_id = active_pet['id'] if active_pet else None
                self.inventory_window = InventoryWindow(
                    database=self.database,
                    pet_id=pet_id,
                    growth_system=self.pet_growth
                )
            
            self.inventory_window.load_inventory()
            self.inventory_window.show()
            self.inventory_window.raise_()
            self.inventory_window.activateWindow()
        except Exception as e:
            print(f"[应用] 打开背包窗口失败: {e}")
    
    def show_shop(self):
        """显示商店窗口 [v0.4.0]"""
        try:
            if not self.shop_window:
                print("[应用] 创建商店窗口")
                from src.pet_shop import PetShopWindow
                active_pet = self.pet_manager.get_active_pet() if self.pet_manager else None
                pet_id = active_pet['id'] if active_pet else None
                self.shop_window = PetShopWindow(
                    database=self.database,
                    pet_id=pet_id
                )
                print(f"[应用] 商店窗口已创建，pet_id={pet_id}")
            
            if hasattr(self.shop_window, 'load_points'):
                self.shop_window.load_points()
            self.shop_window.show()
            self.shop_window.raise_()
            self.shop_window.activateWindow()
            print("[应用] 商店窗口已显示")
        except ImportError as e:
            print(f"[应用] 无法导入商店窗口模块: {e}")
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(None, "错误", f"无法导入商店窗口模块：\n{str(e)}")
        except Exception as e:
            print(f"[应用] 打开商店窗口失败: {e}")
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(None, "错误", f"打开商店窗口失败：\n{str(e)}")
    
    def quit_app(self):
        """退出应用"""
        try:
            reply = QMessageBox.question(
                None,
                "确认退出",
                "确定要退出桌面灵宠吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                print("\n[系统] 正在退出...")
                self.logger.info("用户请求退出应用")
                
                # 停止提醒系统
                if self.reminder_system:
                    try:
                        self.reminder_system.stop()
                        self.logger.info("提醒系统已停止")
                    except Exception as e:
                        self.logger.error(f"停止提醒系统失败: {e}")
                
                # 关闭数据库
                if self.database:
                    try:
                        self.database.close()
                        self.logger.info("数据库已关闭")
                    except Exception as e:
                        self.logger.error(f"关闭数据库失败: {e}")
                
                print("[系统] 再见！")
                self.logger.info("应用正常退出")
                self.app.quit()
        except Exception as e:
            self.logger.exception("退出应用时发生错误")
            # 强制退出
            self.app.quit()
    
    def on_task_completed(self, task_id):
        """任务完成回调"""
        try:
            print(f"[应用] 任务 {task_id} 已完成")
            self.logger.info(f"任务完成: ID={task_id}")
            
            # 播放兴奋动画
            if self.pet_window:
                self.pet_window.load_animation("excited")
                # 2秒后恢复
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(2000, lambda: self.pet_window.load_animation("idle"))
            
            # 刷新待办窗口
            if self.todo_window:
                self.todo_window.load_tasks()
            
            # [v0.4.0] 奖励经验和道具
            if self.pet_growth:
                self.pet_growth.add_experience(5, "完成任务")
                
                from src.pet_inventory import ItemManager
                item_mgr = ItemManager(self.database, self.pet_growth.pet_id)
                item_mgr.give_reward('task_complete')
                
                print("  [奖励] +5经验，获得道具奖励")
        except Exception as e:
            self.logger.exception(f"处理任务完成失败: {task_id}")
    
    def on_task_snoozed(self, task_id, minutes):
        """任务延后回调"""
        try:
            print(f"[应用] 任务 {task_id} 延后 {minutes} 分钟")
            self.logger.info(f"任务延后: ID={task_id}, 延后{minutes}分钟")
        except Exception as e:
            self.logger.exception(f"处理任务延后失败: {task_id}")
    
    def on_task_added(self, task_data):
        """任务添加回调"""
        try:
            print(f"[应用] 新增任务: {task_data.get('title')}")
            self.logger.info(f"新增任务: {task_data.get('title')}")
            # 显示托盘通知
            if self.tray_icon:
                self.tray_icon.show_notification(
                    "任务已添加",
                    task_data.get('title', '新任务')
                )
        except Exception as e:
            self.logger.exception("处理任务添加失败")
    
    def on_task_deleted(self, task_id):
        """任务删除回调"""
        try:
            print(f"[应用] 删除任务: {task_id}")
            self.logger.info(f"删除任务: ID={task_id}")
        except Exception as e:
            self.logger.exception(f"处理任务删除失败: {task_id}")
    
    def on_settings_changed(self, settings):
        """设置改变回调"""
        try:
            print(f"[应用] 设置已更改")
            self.logger.info("用户更改了设置")
            # TODO: 应用新设置
        except Exception as e:
            self.logger.exception("处理设置更改失败")
    
    def on_theme_changed(self, theme_name):
        """
        主题切换回调 [v0.3.0]
        
        Args:
            theme_name: 主题名称（'浅色'/'深色'）
        """
        try:
            # 转换主题名称
            theme_map = {
                '浅色': 'light',
                '深色': 'dark',
                '跟随系统': 'light'
            }
            
            theme = theme_map.get(theme_name, 'light')
            
            print(f"[应用] 切换主题: {theme_name} -> {theme}")
            self.logger.info(f"主题切换: {theme}")
            
            # 应用到所有窗口
            if self.todo_window and hasattr(self.todo_window, 'apply_theme'):
                self.todo_window.apply_theme(theme)
            
            if self.settings_window and hasattr(self.settings_window, 'apply_theme'):
                self.settings_window.apply_theme(theme_name)
                
        except Exception as e:
            self.logger.exception("主题切换失败")
            print(f"  [ERROR] 主题切换失败: {e}")
    
    # ========== v0.4.0 新功能回调方法 ==========
    
    def on_image_dropped(self, image_path: str):
        """
        图片拖放回调 [v0.4.0]
        
        Args:
            image_path: 图片路径
        """
        try:
            print(f"[应用] 收到拖放图片: {image_path}")
            self.logger.info(f"图片拖放: {image_path}")
            
            # 使用图片识别器处理
            if self.image_recognizer:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(
                    self.pet_window,
                    "图片识别",
                    "正在识别图片内容，请稍候...\n\n这可能需要几秒钟时间。"
                )
                self.image_recognizer.recognize_image(image_path)
            else:
                print("  [ERROR] 图片识别器未初始化")
        except Exception as e:
            self.logger.exception("处理图片拖放失败")
            print(f"  [ERROR] 处理图片拖放失败: {e}")
    
    def on_image_recognized(self, result: dict):
        """
        图片识别完成回调 [v0.4.0]
        
        Args:
            result: 识别结果
        """
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            summary = result.get('summary', '')
            tasks = result.get('tasks', [])
            
            print(f"[应用] 图片识别完成: {summary}")
            self.logger.info(f"图片识别完成，识别到{len(tasks)}个任务")
            
            if not tasks:
                QMessageBox.information(
                    self.pet_window,
                    "识别完成",
                    f"图片内容：{summary}\n\n未识别到明确的任务信息。"
                )
        except Exception as e:
            self.logger.exception("处理识别结果失败")
    
    def on_tasks_generated(self, tasks: list):
        """
        任务生成回调 [v0.4.0]
        
        Args:
            tasks: 任务列表
        """
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            print(f"[应用] 从图片生成 {len(tasks)} 个任务")
            
            # 询问是否添加任务
            task_titles = "\n".join([f"• {task['title']}" for task in tasks[:5]])
            
            reply = QMessageBox.question(
                self.pet_window,
                "识别到任务",
                f"识别到以下任务：\n\n{task_titles}\n\n是否添加到待办列表？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes and self.database:
                # 添加任务
                added_count = 0
                for task_data in tasks:
                    # 转换优先级
                    priority_map = {'高': 3, '中': 2, '低': 1}
                    priority = priority_map.get(task_data.get('priority', '中'), 2)
                    
                    task_id = self.database.add_task(
                        title=task_data['title'],
                        description=task_data.get('description', ''),
                        priority=priority,
                        category='图片识别'
                    )
                    
                    if task_id:
                        added_count += 1
                
                # 刷新待办窗口
                if self.todo_window:
                    self.todo_window.load_tasks()
                
                QMessageBox.information(
                    self.pet_window,
                    "添加成功",
                    f"成功添加 {added_count} 个任务！"
                )
                
                print(f"[应用] 已添加 {added_count} 个任务")
                self.logger.info(f"从图片添加了{added_count}个任务")
        except Exception as e:
            self.logger.exception("生成任务失败")
    
    def on_image_error(self, error: str):
        """
        图片识别错误回调 [v0.4.0]
        
        Args:
            error: 错误信息
        """
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(self.pet_window, "识别失败", f"图片识别失败：\n{error}")
        print(f"[应用] 图片识别错误: {error}")
    
    def on_pet_level_up(self, old_level: int, new_level: int):
        """
        宠物升级回调 [v0.4.0]
        
        Args:
            old_level: 旧等级
            new_level: 新等级
        """
        try:
            from PyQt5.QtWidgets import QMessageBox
            from src.pet_inventory import ItemManager
            
            print(f"[应用] 宠物升级: {old_level} → {new_level}")
            self.logger.info(f"宠物升级到{new_level}级")
            
            # 显示升级提示
            QMessageBox.information(
                self.pet_window,
                "恭喜升级！",
                f"🎉 宠物升级啦！\n\n等级：{old_level} → {new_level}"
            )
            
            # 奖励道具
            if self.pet_growth:
                item_mgr = ItemManager(self.database, self.pet_growth.pet_id)
                item_mgr.give_reward('level_up')
        except Exception as e:
            self.logger.exception("处理升级回调失败")
    
    def on_pet_evolution(self, stage: int):
        """
        宠物进化回调 [v0.4.0]
        
        Args:
            stage: 进化阶段
        """
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            stage_names = {1: '幼年期', 2: '成长期', 3: '成熟期', 4: '完全体'}
            stage_name = stage_names.get(stage, '未知')
            
            print(f"[应用] 宠物进化: {stage_name}")
            self.logger.info(f"宠物进化到{stage_name}")
            
            QMessageBox.information(
                self.pet_window,
                "宠物进化！",
                f"🦋 宠物进化啦！\n\n进入：{stage_name}"
            )
        except Exception as e:
            self.logger.exception("处理进化回调失败")
    
    def on_achievement_unlocked(self, achievement_name: str):
        """
        成就解锁回调 [v0.4.0]
        
        Args:
            achievement_name: 成就名称
        """
        try:
            print(f"[应用] 解锁成就: {achievement_name}")
            self.logger.info(f"解锁成就: {achievement_name}")
            
            # 可以在这里显示成就解锁动画或提示
        except Exception as e:
            self.logger.exception("处理成就解锁回调失败")
    
    def on_pomodoro_completed(self, session_type: str, duration: int):
        """
        番茄钟完成回调 [v0.4.0]
        
        Args:
            session_type: 会话类型
            duration: 持续时间
        """
        try:
            print(f"[应用] 番茄钟完成: {session_type}, {duration}秒")
            self.logger.info(f"番茄钟会话完成: {session_type}")
            
            # 播放伸懒腰动画（休息完成）
            if session_type == 'break' and self.pet_window:
                self.pet_window.load_animation("stretch")
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(3000, lambda: self.pet_window.load_animation("idle"))
            
            # 如果是工作会话，奖励经验和道具
            if session_type == 'work' and self.pet_growth:
                self.pet_growth.add_experience(3, "番茄钟")
                
                from src.pet_inventory import ItemManager
                item_mgr = ItemManager(self.database, self.pet_growth.pet_id)
                item_mgr.give_reward('pomodoro')
        except Exception as e:
            self.logger.exception("处理番茄钟完成回调失败")
    
    def run(self):
        """运行应用"""
        try:
            # 显示宠物窗口
            self.pet_window.show()
            self.logger.info("宠物窗口已显示")
            
            # 显示启动通知
            if self.tray_icon:
                self.tray_icon.show_notification(
                    "桌面灵宠",
                    "已成功启动！右键点击宠物或托盘图标查看菜单。"
                )
            
            print("\n[应用] 应用已启动！")
            print("[提示] 可以拖动宠物，右键查看菜单")
            print("\n" + "=" * 60 + "\n")
            
            self.logger.info("应用启动完成")
        except Exception as e:
            self.logger.exception("应用运行失败")
            print(f"[ERROR] 应用运行失败: {e}")


def main():
    """主函数"""
    logger = None
    
    try:
        # 设置高DPI支持（必须在创建QApplication之前）
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # 创建应用实例
        app = QApplication(sys.argv)
        app.setApplicationName("桌面灵宠")
        app.setApplicationVersion("0.2.0")
        app.setOrganizationName("Desktop Pet")
        
        # 设置应用不在关闭最后一个窗口时退出
        app.setQuitOnLastWindowClosed(False)
        
        # 初始化日志（在创建主应用之前）
        logger = get_logger("Startup")
        logger.info("=" * 60)
        logger.info("桌面灵宠 v0.2.0 Beta 启动")
        logger.info("=" * 60)
        
        # 创建并运行应用
        desktop_pet = DesktopPetApp(app)
        desktop_pet.run()
        
        # 启动事件循环
        logger.info("进入应用事件循环")
        exit_code = app.exec_()
        logger.info(f"应用退出，退出码: {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n[信息] 用户中断应用")
        if logger:
            logger.info("用户通过 Ctrl+C 中断应用")
        return 0
        
    except Exception as e:
        print(f"\n[错误] 应用启动失败: {e}")
        if logger:
            logger.exception("应用启动失败")
        else:
            import traceback
            traceback.print_exc()
        
        # 显示错误对话框
        try:
            QMessageBox.critical(
                None,
                "启动失败",
                f"桌面灵宠启动失败：\n\n{str(e)}\n\n请查看日志文件或联系开发者。"
            )
        except:
            pass
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

