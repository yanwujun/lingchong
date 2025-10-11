#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设置窗口模块
Settings Window Module - 负责应用设置界面
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QCheckBox, QSlider, QComboBox,
                             QGroupBox, QFormLayout, QTabWidget, QApplication,
                             QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal

# 导入主题和音效管理器
try:
    from src.themes import apply_theme_to_widget
    from src.sound_manager import get_sound_manager
except ImportError:
    try:
        from themes import apply_theme_to_widget
        from sound_manager import get_sound_manager
    except ImportError:
        apply_theme_to_widget = None
        get_sound_manager = None


class SettingsWindow(QWidget):
    """设置窗口"""
    
    # 信号
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.current_theme = 'light'  # 默认主题
        self.sound_manager = get_sound_manager() if get_sound_manager else None
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("⚙️ 设置")
        self.setGeometry(100, 100, 600, 500)
        
        # 主布局
        layout = QVBoxLayout()
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 各个设置页面
        tab_widget.addTab(self.create_pet_settings(), "🐱 宠物设置")
        tab_widget.addTab(self.create_behavior_settings(), "🎮 行为设置")
        tab_widget.addTab(self.create_reminder_settings(), "⏰ 提醒设置")
        tab_widget.addTab(self.create_system_settings(), "🔧 系统设置")
        
        layout.addWidget(tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 保存设置")
        save_btn.clicked.connect(self.save_settings)
        
        reset_btn = QPushButton("🔄 恢复默认")
        reset_btn.clicked.connect(self.reset_settings)
        
        close_btn = QPushButton("❌ 关闭")
        close_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 应用主题 [v0.3.0]
        self.apply_theme(self.current_theme)
    
    def create_pet_settings(self):
        """创建宠物设置页面"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 外观设置
        appearance_group = QGroupBox("外观设置")
        appearance_layout = QFormLayout()
        
        # 宠物皮肤
        self.skin_combo = QComboBox()
        self.skin_combo.addItems(["默认宠物", "小猫", "小狗", "兔子", "企鹅"])
        appearance_layout.addRow("宠物皮肤:", self.skin_combo)
        
        # 宠物大小
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(64)
        self.size_slider.setMaximum(256)
        self.size_slider.setValue(128)
        self.size_slider.setTickPosition(QSlider.TicksBelow)
        self.size_slider.setTickInterval(32)
        
        size_label = QLabel("128 px")
        self.size_slider.valueChanged.connect(
            lambda v: size_label.setText(f"{v} px")
        )
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(self.size_slider)
        size_layout.addWidget(size_label)
        
        appearance_layout.addRow("宠物大小:", size_layout)
        
        # 不透明度
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(50)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(100)
        
        opacity_label = QLabel("100%")
        self.opacity_slider.valueChanged.connect(
            lambda v: opacity_label.setText(f"{v}%")
        )
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(opacity_label)
        
        appearance_layout.addRow("不透明度:", opacity_layout)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # 动画设置
        animation_group = QGroupBox("动画设置")
        animation_layout = QFormLayout()
        
        # 动画速度
        self.anim_speed_slider = QSlider(Qt.Horizontal)
        self.anim_speed_slider.setMinimum(50)
        self.anim_speed_slider.setMaximum(200)
        self.anim_speed_slider.setValue(100)
        
        anim_speed_label = QLabel("100%")
        self.anim_speed_slider.valueChanged.connect(
            lambda v: anim_speed_label.setText(f"{v}%")
        )
        
        anim_speed_layout = QHBoxLayout()
        anim_speed_layout.addWidget(self.anim_speed_slider)
        anim_speed_layout.addWidget(anim_speed_label)
        
        animation_layout.addRow("动画速度:", anim_speed_layout)
        
        animation_group.setLayout(animation_layout)
        layout.addWidget(animation_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        return widget
    
    def create_behavior_settings(self):
        """创建行为设置页面"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 自动行为
        behavior_group = QGroupBox("自动行为")
        behavior_layout = QVBoxLayout()
        
        self.auto_move_check = QCheckBox("自动移动")
        self.auto_move_check.setChecked(True)
        
        self.random_action_check = QCheckBox("随机动作")
        self.random_action_check.setChecked(True)
        
        self.follow_mouse_check = QCheckBox("跟随鼠标")
        
        self.enable_gravity_check = QCheckBox("启用重力效果")
        
        self.edge_bounce_check = QCheckBox("边缘反弹")
        self.edge_bounce_check.setChecked(True)
        
        behavior_layout.addWidget(self.auto_move_check)
        behavior_layout.addWidget(self.random_action_check)
        behavior_layout.addWidget(self.follow_mouse_check)
        behavior_layout.addWidget(self.enable_gravity_check)
        behavior_layout.addWidget(self.edge_bounce_check)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        # 行为频率
        frequency_group = QGroupBox("行为频率")
        frequency_layout = QFormLayout()
        
        # 动作间隔
        self.action_interval_slider = QSlider(Qt.Horizontal)
        self.action_interval_slider.setMinimum(5)
        self.action_interval_slider.setMaximum(60)
        self.action_interval_slider.setValue(10)
        
        interval_label = QLabel("10 秒")
        self.action_interval_slider.valueChanged.connect(
            lambda v: interval_label.setText(f"{v} 秒")
        )
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(self.action_interval_slider)
        interval_layout.addWidget(interval_label)
        
        frequency_layout.addRow("动作间隔:", interval_layout)
        
        # 移动速度
        self.move_speed_slider = QSlider(Qt.Horizontal)
        self.move_speed_slider.setMinimum(1)
        self.move_speed_slider.setMaximum(10)
        self.move_speed_slider.setValue(2)
        
        speed_label = QLabel("2")
        self.move_speed_slider.valueChanged.connect(
            lambda v: speed_label.setText(str(v))
        )
        
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(self.move_speed_slider)
        speed_layout.addWidget(speed_label)
        
        frequency_layout.addRow("移动速度:", speed_layout)
        
        frequency_group.setLayout(frequency_layout)
        layout.addWidget(frequency_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        return widget
    
    def create_reminder_settings(self):
        """创建提醒设置页面"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 提醒方式
        method_group = QGroupBox("提醒方式")
        method_layout = QVBoxLayout()
        
        self.reminder_animation_check = QCheckBox("宠物动画提醒")
        self.reminder_animation_check.setChecked(True)
        
        self.reminder_popup_check = QCheckBox("弹窗提醒")
        self.reminder_popup_check.setChecked(True)
        
        self.reminder_sound_check = QCheckBox("声音提醒")
        self.reminder_sound_check.setChecked(True)
        
        self.system_notification_check = QCheckBox("系统通知")
        
        method_layout.addWidget(self.reminder_animation_check)
        method_layout.addWidget(self.reminder_popup_check)
        method_layout.addWidget(self.reminder_sound_check)
        method_layout.addWidget(self.system_notification_check)
        
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)
        
        # 提醒设置
        reminder_group = QGroupBox("提醒配置")
        reminder_layout = QFormLayout()
        
        # 默认提前时间
        self.advance_time_combo = QComboBox()
        self.advance_time_combo.addItems([
            "不提前", "5分钟", "15分钟", "30分钟", 
            "1小时", "2小时", "1天"
        ])
        self.advance_time_combo.setCurrentIndex(2)
        
        reminder_layout.addRow("默认提前时间:", self.advance_time_combo)
        
        # 延后时间
        self.snooze_time_combo = QComboBox()
        self.snooze_time_combo.addItems([
            "5分钟", "10分钟", "15分钟", "30分钟", "1小时"
        ])
        
        reminder_layout.addRow("延后时间:", self.snooze_time_combo)
        
        reminder_group.setLayout(reminder_layout)
        layout.addWidget(reminder_group)
        
        # 音量设置
        sound_group = QGroupBox("音效设置")
        sound_layout = QFormLayout()
        
        # 音量
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        
        volume_label = QLabel("50%")
        self.volume_slider.valueChanged.connect(
            lambda v: volume_label.setText(f"{v}%")
        )
        self.volume_slider.valueChanged.connect(self.on_volume_changed)  # [v0.3.0]
        
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(volume_label)
        
        sound_layout.addRow("音量:", volume_layout)
        
        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        return widget
    
    def create_system_settings(self):
        """创建系统设置页面"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 系统设置
        system_group = QGroupBox("系统设置")
        system_layout = QVBoxLayout()
        
        self.auto_start_check = QCheckBox("开机自启动")
        
        self.minimize_to_tray_check = QCheckBox("最小化到托盘")
        self.minimize_to_tray_check.setChecked(True)
        
        self.always_on_top_check = QCheckBox("窗口始终置顶")
        self.always_on_top_check.setChecked(True)
        
        system_layout.addWidget(self.auto_start_check)
        system_layout.addWidget(self.minimize_to_tray_check)
        system_layout.addWidget(self.always_on_top_check)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # 语言和主题
        appearance_group = QGroupBox("外观")
        appearance_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "English"])
        
        appearance_layout.addRow("语言:", self.language_combo)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色", "深色", "跟随系统"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)  # [v0.3.0]
        
        appearance_layout.addRow("主题:", self.theme_combo)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # 数据管理
        data_group = QGroupBox("数据管理")
        data_layout = QVBoxLayout()
        
        self.auto_backup_check = QCheckBox("自动备份数据")
        self.auto_backup_check.setChecked(True)
        
        data_layout.addWidget(self.auto_backup_check)
        
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 导出数据")
        export_btn.clicked.connect(self.export_data)
        
        import_btn = QPushButton("📥 导入数据")
        import_btn.clicked.connect(self.import_data)
        
        button_layout.addWidget(export_btn)
        button_layout.addWidget(import_btn)
        
        data_layout.addLayout(button_layout)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        return widget
    
    def load_settings(self):
        """加载设置"""
        # TODO: 从配置文件加载设置并应用到UI
        pass
    
    def save_settings(self):
        """保存设置"""
        # 收集所有设置
        settings = {
            'pet': {
                'skin': self.skin_combo.currentText(),
                'size': self.size_slider.value(),
                'opacity': self.opacity_slider.value() / 100.0,
                'animation_speed': self.anim_speed_slider.value() / 100.0,
            },
            'behavior': {
                'auto_move': self.auto_move_check.isChecked(),
                'random_action': self.random_action_check.isChecked(),
                'follow_mouse': self.follow_mouse_check.isChecked(),
                'enable_gravity': self.enable_gravity_check.isChecked(),
                'edge_bounce': self.edge_bounce_check.isChecked(),
                'action_interval': self.action_interval_slider.value(),
                'move_speed': self.move_speed_slider.value(),
            },
            'reminder': {
                'animation': self.reminder_animation_check.isChecked(),
                'popup': self.reminder_popup_check.isChecked(),
                'sound': self.reminder_sound_check.isChecked(),
                'notification': self.system_notification_check.isChecked(),
                'advance_time': self.advance_time_combo.currentText(),
                'snooze_time': self.snooze_time_combo.currentText(),
                'volume': self.volume_slider.value() / 100.0,
            },
            'system': {
                'auto_start': self.auto_start_check.isChecked(),
                'minimize_to_tray': self.minimize_to_tray_check.isChecked(),
                'always_on_top': self.always_on_top_check.isChecked(),
                'language': self.language_combo.currentText(),
                'theme': self.theme_combo.currentText(),
                'auto_backup': self.auto_backup_check.isChecked(),
            }
        }
        
        # TODO: 保存到配置文件
        # save_config(settings)
        
        # 发送信号
        self.settings_changed.emit(settings)
        
        QMessageBox.information(self, "成功", "设置已保存！")
        print("[设置] 保存成功:", settings)
    
    def reset_settings(self):
        """恢复默认设置"""
        reply = QMessageBox.question(
            self, "确认", "确定要恢复默认设置吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # TODO: 加载默认设置
            QMessageBox.information(self, "成功", "已恢复默认设置！")
    
    def export_data(self):
        """导出数据"""
        # TODO: 实现数据导出
        QMessageBox.information(self, "提示", "数据导出功能开发中...")
    
    def import_data(self):
        """导入数据"""
        # TODO: 实现数据导入
        QMessageBox.information(self, "提示", "数据导入功能开发中...")
    
    def apply_theme(self, theme_name='light'):
        """
        应用主题 [v0.3.0]
        
        Args:
            theme_name: 主题名称（'浅色'/'深色'/'跟随系统'）
        """
        # 转换主题名称
        theme_map = {
            '浅色': 'light',
            '深色': 'dark',
            '跟随系统': 'light'  # 暂时默认为浅色
        }
        
        theme = theme_map.get(theme_name, 'light')
        
        if apply_theme_to_widget:
            apply_theme_to_widget(self, 'settings_window', theme)
            self.current_theme = theme
        else:
            print("[设置窗口] 主题模块不可用")
    
    def on_theme_changed(self, theme_name):
        """
        主题切换回调 [v0.3.0]
        
        Args:
            theme_name: 主题名称
        """
        self.apply_theme(theme_name)
        print(f"[设置窗口] 主题已切换: {theme_name}")
        
        # 播放点击音效
        if self.sound_manager:
            self.sound_manager.play_click()
    
    def on_volume_changed(self, value):
        """
        音量更改回调 [v0.3.0]
        
        Args:
            value: 音量值（0-100）
        """
        if self.sound_manager:
            volume = value / 100.0
            self.sound_manager.set_volume(volume)
    
    def closeEvent(self, event):
        """关闭事件 - 隐藏窗口而不是退出"""
        event.ignore()  # 忽略关闭事件
        self.hide()     # 隐藏窗口
        print("[设置窗口] 窗口已隐藏")


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = SettingsWindow()
    window.show()
    
    sys.exit(app.exec_())

