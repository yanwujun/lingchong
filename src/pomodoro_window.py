#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
番茄钟主窗口模块
Pomodoro Window Module - 番茄钟设置、统计和历史记录界面
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QSpinBox, QCheckBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QTabWidget, QApplication, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

# 导入番茄钟核心
try:
    from src.pomodoro_core import PomodoroManager
    from src.modern_ui import (ModernButton, ModernTabWidget, ModernCard, 
                              ModernProgressBar, ModernSpinBox, ModernCheckBox, COLORS)
except ImportError:
    from pomodoro_core import PomodoroManager
    try:
        from modern_ui import (ModernButton, ModernTabWidget, ModernCard, 
                              ModernProgressBar, ModernSpinBox, ModernCheckBox, COLORS)
    except ImportError:
        # 回退到原始组件
        ModernButton = QPushButton
        ModernTabWidget = QTabWidget
        ModernCard = QGroupBox
        ModernProgressBar = QProgressBar
        ModernSpinBox = QSpinBox
        ModernCheckBox = QCheckBox
        COLORS = {'background': '#e0e5ec', 'surface': '#e0e5ec', 'primary': '#6366f1'}


class PomodoroWindow(QWidget):
    """番茄钟主窗口"""
    
    # 信号
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, database=None, parent=None):
        super().__init__(parent)
        self.database = database
        self.pomodoro_manager = PomodoroManager(database)
        self.init_ui()
        
        # 连接信号
        self.connect_signals()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("🍅 番茄钟")
        self.setGeometry(100, 100, 700, 600)
        # 应用Neumorphism背景色
        self.setStyleSheet(f"QWidget {{ background-color: {COLORS['background']}; }}")
        
        # 主布局
        layout = QVBoxLayout()
        
        # 创建标签页
        self.tab_widget = ModernTabWidget()
        
        # 各个页面
        self.tab_widget.addTab(self.create_timer_page(), "⏱️ 计时器")
        self.tab_widget.addTab(self.create_settings_page(), "⚙️ 设置")
        self.tab_widget.addTab(self.create_stats_page(), "📊 统计")
        self.tab_widget.addTab(self.create_history_page(), "📝 历史")
        
        layout.addWidget(self.tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.close_btn = ModernButton("❌ 关闭", style="secondary")
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
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
    
    def create_timer_page(self):
        """创建计时器页面"""
        page = QWidget()
        layout = QVBoxLayout()
        
        # 当前状态
        status_group = QGroupBox("⏱️ 当前状态")
        status_layout = QVBoxLayout()
        
        # 会话类型
        self.session_type_label = QLabel("准备开始")
        self.session_type_label.setFont(QFont("", 18, QFont.Bold))
        self.session_type_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.session_type_label)
        
        # 时间显示
        self.time_label = QLabel("25:00")
        self.time_label.setFont(QFont("", 48, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: #4CAF50;")
        status_layout.addWidget(self.time_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: #f0f0f0;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        status_layout.addWidget(self.progress_bar)
        
        # 会话计数
        self.session_count_label = QLabel("已完成: 0 个工作会话")
        self.session_count_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.session_count_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # 控制按钮
        control_group = QGroupBox("🎮 控制")
        control_layout = QVBoxLayout()
        
        # 按钮行1
        button_row1 = QHBoxLayout()
        
        self.start_work_btn = QPushButton("🍅 开始工作")
        self.start_work_btn.clicked.connect(self.start_work)
        self.start_work_btn.setStyleSheet("QPushButton { padding: 15px; font-size: 14px; }")
        
        self.start_break_btn = QPushButton("☕ 开始休息")
        self.start_break_btn.clicked.connect(self.start_break)
        self.start_break_btn.setStyleSheet("QPushButton { padding: 15px; font-size: 14px; background-color: #2196F3; } QPushButton:hover { background-color: #1976D2; }")
        
        button_row1.addWidget(self.start_work_btn)
        button_row1.addWidget(self.start_break_btn)
        control_layout.addLayout(button_row1)
        
        # 按钮行2
        button_row2 = QHBoxLayout()
        
        self.pause_btn = QPushButton("⏸️ 暂停")
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setEnabled(False)
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; } QPushButton:hover { background-color: #da190b; }")
        
        self.skip_btn = QPushButton("⏭️ 跳过")
        self.skip_btn.clicked.connect(self.skip)
        self.skip_btn.setEnabled(False)
        
        button_row2.addWidget(self.pause_btn)
        button_row2.addWidget(self.stop_btn)
        button_row2.addWidget(self.skip_btn)
        control_layout.addLayout(button_row2)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_settings_page(self):
        """创建设置页面"""
        page = QWidget()
        layout = QVBoxLayout()
        
        # 时长设置
        duration_group = QGroupBox("⏰ 时长设置")
        duration_layout = QHBoxLayout()
        
        # 工作时长
        work_layout = QVBoxLayout()
        work_layout.addWidget(QLabel("工作时长（分钟）:"))
        self.work_spin = QSpinBox()
        self.work_spin.setMinimum(1)
        self.work_spin.setMaximum(60)
        self.work_spin.setValue(25)
        work_layout.addWidget(self.work_spin)
        duration_layout.addLayout(work_layout)
        
        # 短休息时长
        short_break_layout = QVBoxLayout()
        short_break_layout.addWidget(QLabel("短休息（分钟）:"))
        self.short_break_spin = QSpinBox()
        self.short_break_spin.setMinimum(1)
        self.short_break_spin.setMaximum(30)
        self.short_break_spin.setValue(5)
        short_break_layout.addWidget(self.short_break_spin)
        duration_layout.addLayout(short_break_layout)
        
        # 长休息时长
        long_break_layout = QVBoxLayout()
        long_break_layout.addWidget(QLabel("长休息（分钟）:"))
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setMinimum(1)
        self.long_break_spin.setMaximum(60)
        self.long_break_spin.setValue(15)
        long_break_layout.addWidget(self.long_break_spin)
        duration_layout.addLayout(long_break_layout)
        
        duration_group.setLayout(duration_layout)
        layout.addWidget(duration_group)
        
        # 行为设置
        behavior_group = QGroupBox("🎮 行为设置")
        behavior_layout = QVBoxLayout()
        
        self.auto_start_breaks_check = QCheckBox("休息结束后自动开始工作")
        self.auto_start_work_check = QCheckBox("工作结束后自动开始休息")
        self.auto_start_work_check.setChecked(True)
        
        self.focus_mode_check = QCheckBox("启用专注模式（屏蔽通知）")
        self.show_widget_check = QCheckBox("显示桌面小组件")
        self.show_widget_check.setChecked(True)
        
        behavior_layout.addWidget(self.auto_start_breaks_check)
        behavior_layout.addWidget(self.auto_start_work_check)
        behavior_layout.addWidget(self.focus_mode_check)
        behavior_layout.addWidget(self.show_widget_check)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        # 保存按钮
        save_btn = QPushButton("💾 保存设置")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_stats_page(self):
        """创建统计页面"""
        page = QWidget()
        layout = QVBoxLayout()
        
        # 统计概览
        stats_group = QGroupBox("📊 统计概览（最近7天）")
        stats_layout = QVBoxLayout()
        
        self.total_sessions_label = QLabel("总会话数: 0")
        self.total_sessions_label.setFont(QFont("", 14))
        
        self.completed_sessions_label = QLabel("完成会话数: 0")
        self.completed_sessions_label.setFont(QFont("", 14))
        
        self.work_time_label = QLabel("工作时间: 0 分钟")
        self.work_time_label.setFont(QFont("", 14))
        
        self.break_time_label = QLabel("休息时间: 0 分钟")
        self.break_time_label.setFont(QFont("", 14))
        
        stats_layout.addWidget(self.total_sessions_label)
        stats_layout.addWidget(self.completed_sessions_label)
        stats_layout.addWidget(self.work_time_label)
        stats_layout.addWidget(self.break_time_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新统计")
        refresh_btn.clicked.connect(self.refresh_stats)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_history_page(self):
        """创建历史记录页面"""
        page = QWidget()
        layout = QVBoxLayout()
        
        # 历史记录表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["类型", "开始时间", "持续时间", "状态", "任务"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.history_table)
        
        page.setLayout(layout)
        return page
    
    def connect_signals(self):
        """连接信号"""
        timer = self.pomodoro_manager.timer
        
        timer.tick.connect(self.on_tick)
        timer.session_started.connect(self.on_session_started)
        timer.session_completed.connect(self.on_session_completed)
        timer.session_cancelled.connect(self.on_session_cancelled)
    
    def start_work(self):
        """开始工作会话"""
        if self.pomodoro_manager.start_work_session():
            self.update_button_states(running=True)
    
    def start_break(self):
        """开始休息会话"""
        if self.pomodoro_manager.start_break_session():
            self.update_button_states(running=True)
    
    def toggle_pause(self):
        """切换暂停/继续"""
        if self.pomodoro_manager.toggle_pause():
            if self.pomodoro_manager.timer.is_paused:
                self.pause_btn.setText("▶️ 继续")
            else:
                self.pause_btn.setText("⏸️ 暂停")
    
    def stop(self):
        """停止"""
        if self.pomodoro_manager.stop_session():
            self.update_button_states(running=False)
            self.reset_display()
    
    def skip(self):
        """跳过"""
        self.pomodoro_manager.skip_session()
    
    def on_tick(self, remaining_seconds):
        """每秒更新"""
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        
        # 更新进度条
        progress = self.pomodoro_manager.timer.get_progress() * 100
        self.progress_bar.setValue(int(progress))
    
    def on_session_started(self, session_type):
        """会话开始"""
        names = {'work': '🍅 工作中', 'short_break': '☕ 短休息', 'long_break': '🌴 长休息'}
        self.session_type_label.setText(names.get(session_type, session_type))
    
    def on_session_completed(self, session_type, duration):
        """会话完成"""
        self.update_button_states(running=False)
        self.reset_display()
        
        # 更新会话计数
        count = self.pomodoro_manager.timer.get_session_count()
        self.session_count_label.setText(f"已完成: {count} 个工作会话")
    
    def on_session_cancelled(self):
        """会话取消"""
        self.update_button_states(running=False)
        self.reset_display()
    
    def update_button_states(self, running):
        """更新按钮状态"""
        self.start_work_btn.setEnabled(not running)
        self.start_break_btn.setEnabled(not running)
        self.pause_btn.setEnabled(running)
        self.stop_btn.setEnabled(running)
        self.skip_btn.setEnabled(running)
    
    def reset_display(self):
        """重置显示"""
        self.session_type_label.setText("准备开始")
        self.time_label.setText("25:00")
        self.progress_bar.setValue(0)
        self.pause_btn.setText("⏸️ 暂停")
    
    def save_settings(self):
        """保存设置"""
        work = self.work_spin.value()
        short_break = self.short_break_spin.value()
        long_break = self.long_break_spin.value()
        
        self.pomodoro_manager.timer.set_durations(work, short_break, long_break)
        
        # 重置显示
        self.time_label.setText(f"{work:02d}:00")
        
        print(f"[番茄钟] 设置已保存: 工作{work}分钟, 短休息{short_break}分钟, 长休息{long_break}分钟")
    
    def refresh_stats(self):
        """刷新统计"""
        stats = self.pomodoro_manager.get_statistics(7)
        
        if stats:
            self.total_sessions_label.setText(f"总会话数: {stats.get('total_sessions', 0)}")
            self.completed_sessions_label.setText(f"完成会话数: {stats.get('completed_sessions', 0)}")
            
            work_minutes = stats.get('work_time', 0) // 60
            break_minutes = stats.get('break_time', 0) // 60
            
            self.work_time_label.setText(f"工作时间: {work_minutes} 分钟")
            self.break_time_label.setText(f"休息时间: {break_minutes} 分钟")
    
    def closeEvent(self, event):
        """关闭事件"""
        event.ignore()
        self.hide()
        print("[番茄钟窗口] 窗口已隐藏")


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = PomodoroWindow()
    window.show()
    
    sys.exit(app.exec_())

