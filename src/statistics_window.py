#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统计窗口模块
Statistics Window Module - 负责任务统计和数据展示
"""

import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGroupBox, QGridLayout,
                             QProgressBar, QApplication, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# 导入主题
try:
    from src.themes import apply_theme_to_widget
    from src.modern_ui import ModernButton, ModernCard, COLORS
except ImportError:
    try:
        from themes import apply_theme_to_widget
        from modern_ui import ModernButton, ModernCard, COLORS
    except ImportError:
        apply_theme_to_widget = None
        # 回退到原始组件
        ModernButton = QPushButton
        ModernCard = QGroupBox
        COLORS = {'background': '#e0e5ec', 'surface': '#e0e5ec', 'primary': '#6366f1'}


class StatisticsWindow(QWidget):
    """统计窗口"""
    
    def __init__(self, database=None):
        super().__init__()
        self.database = database
        self.current_theme = 'light'
        self.init_ui()
        self.load_statistics()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("📊 数据统计")
        self.setGeometry(100, 100, 700, 600)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("📊 任务统计分析")
        title_label.setFont(QFont("", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # 概览统计
        overview_group = self.create_overview_section()
        layout.addWidget(overview_group)
        
        # 时间段统计
        time_group = self.create_time_section()
        layout.addWidget(time_group)
        
        # 优先级统计
        priority_group = self.create_priority_section()
        layout.addWidget(priority_group)
        
        # 分类统计
        category_group = self.create_category_section()
        layout.addWidget(category_group)
        
        layout.addStretch()
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        refresh_btn = ModernButton("🔄 刷新数据", style="secondary")
        refresh_btn.clicked.connect(self.load_statistics)
        
        close_btn = ModernButton("❌ 关闭", style="secondary")
        close_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 应用主题
        self.apply_theme(self.current_theme)
    
    def create_overview_section(self):
        """创建概览统计部分"""
        group = QGroupBox("📈 任务概览")
        layout = QGridLayout()
        
        # 总任务数
        self.total_label = QLabel("0")
        self.total_label.setFont(QFont("", 24, QFont.Bold))
        self.total_label.setAlignment(Qt.AlignCenter)
        
        # 已完成任务数
        self.completed_label = QLabel("0")
        self.completed_label.setFont(QFont("", 24, QFont.Bold))
        self.completed_label.setAlignment(Qt.AlignCenter)
        self.completed_label.setStyleSheet("color: #4CAF50;")
        
        # 待完成任务数
        self.pending_label = QLabel("0")
        self.pending_label.setFont(QFont("", 24, QFont.Bold))
        self.pending_label.setAlignment(Qt.AlignCenter)
        self.pending_label.setStyleSheet("color: #FF9800;")
        
        # 已过期任务数
        self.overdue_label = QLabel("0")
        self.overdue_label.setFont(QFont("", 24, QFont.Bold))
        self.overdue_label.setAlignment(Qt.AlignCenter)
        self.overdue_label.setStyleSheet("color: #F44336;")
        
        # 添加到布局
        layout.addWidget(QLabel("总任务"), 0, 0)
        layout.addWidget(self.total_label, 1, 0)
        
        layout.addWidget(QLabel("已完成"), 0, 1)
        layout.addWidget(self.completed_label, 1, 1)
        
        layout.addWidget(QLabel("待完成"), 0, 2)
        layout.addWidget(self.pending_label, 1, 2)
        
        layout.addWidget(QLabel("已过期"), 0, 3)
        layout.addWidget(self.overdue_label, 1, 3)
        
        # 完成率进度条
        complete_rate_label = QLabel("完成率:")
        self.complete_rate_bar = QProgressBar()
        self.complete_rate_bar.setMinimum(0)
        self.complete_rate_bar.setMaximum(100)
        self.complete_rate_bar.setValue(0)
        self.complete_rate_bar.setFormat("%p%")
        
        layout.addWidget(complete_rate_label, 2, 0)
        layout.addWidget(self.complete_rate_bar, 2, 1, 1, 3)
        
        group.setLayout(layout)
        return group
    
    def create_time_section(self):
        """创建时间段统计部分"""
        group = QGroupBox("⏰ 时间段统计")
        layout = QGridLayout()
        
        # 今日完成
        layout.addWidget(QLabel("今日完成:"), 0, 0)
        self.today_completed_label = QLabel("0")
        self.today_completed_label.setFont(QFont("", 16, QFont.Bold))
        layout.addWidget(self.today_completed_label, 0, 1)
        
        # 本周完成
        layout.addWidget(QLabel("本周完成:"), 1, 0)
        self.week_completed_label = QLabel("0")
        self.week_completed_label.setFont(QFont("", 16, QFont.Bold))
        layout.addWidget(self.week_completed_label, 1, 1)
        
        # 本月完成
        layout.addWidget(QLabel("本月完成:"), 2, 0)
        self.month_completed_label = QLabel("0")
        self.month_completed_label.setFont(QFont("", 16, QFont.Bold))
        layout.addWidget(self.month_completed_label, 2, 1)
        
        group.setLayout(layout)
        return group
    
    def create_priority_section(self):
        """创建优先级统计部分"""
        group = QGroupBox("⚡ 优先级分布")
        layout = QGridLayout()
        
        # 高优先级
        layout.addWidget(QLabel("🔴 高优先级:"), 0, 0)
        self.high_priority_label = QLabel("0")
        self.high_priority_label.setFont(QFont("", 14))
        layout.addWidget(self.high_priority_label, 0, 1)
        
        self.high_priority_bar = QProgressBar()
        self.high_priority_bar.setMaximum(100)
        self.high_priority_bar.setValue(0)
        self.high_priority_bar.setStyleSheet("QProgressBar::chunk { background-color: #F44336; }")
        layout.addWidget(self.high_priority_bar, 0, 2, 1, 2)
        
        # 中优先级
        layout.addWidget(QLabel("🟡 中优先级:"), 1, 0)
        self.medium_priority_label = QLabel("0")
        self.medium_priority_label.setFont(QFont("", 14))
        layout.addWidget(self.medium_priority_label, 1, 1)
        
        self.medium_priority_bar = QProgressBar()
        self.medium_priority_bar.setMaximum(100)
        self.medium_priority_bar.setValue(0)
        self.medium_priority_bar.setStyleSheet("QProgressBar::chunk { background-color: #FF9800; }")
        layout.addWidget(self.medium_priority_bar, 1, 2, 1, 2)
        
        # 低优先级
        layout.addWidget(QLabel("🟢 低优先级:"), 2, 0)
        self.low_priority_label = QLabel("0")
        self.low_priority_label.setFont(QFont("", 14))
        layout.addWidget(self.low_priority_label, 2, 1)
        
        self.low_priority_bar = QProgressBar()
        self.low_priority_bar.setMaximum(100)
        self.low_priority_bar.setValue(0)
        self.low_priority_bar.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
        layout.addWidget(self.low_priority_bar, 2, 2, 1, 2)
        
        group.setLayout(layout)
        return group
    
    def create_category_section(self):
        """创建分类统计部分"""
        group = QGroupBox("📂 分类分布")
        layout = QVBoxLayout()
        
        self.category_info_label = QLabel("暂无分类数据")
        self.category_info_label.setWordWrap(True)
        layout.addWidget(self.category_info_label)
        
        group.setLayout(layout)
        return group
    
    def load_statistics(self):
        """加载统计数据"""
        if not self.database:
            print("[统计窗口] 数据库未连接")
            return
        
        try:
            # 获取所有任务
            all_tasks = self.database.get_all_tasks()
            
            if not all_tasks:
                print("[统计窗口] 暂无任务数据")
                return
            
            # 基础统计
            total = len(all_tasks)
            completed = sum(1 for t in all_tasks if t['status'] == '已完成')
            pending = sum(1 for t in all_tasks if t['status'] == '待完成')
            
            # 计算过期任务
            now = datetime.now()
            overdue = 0
            for task in all_tasks:
                if task['status'] == '待完成' and task['due_date']:
                    try:
                        due_date = datetime.strptime(task['due_date'], '%Y-%m-%d %H:%M:%S')
                        if due_date < now:
                            overdue += 1
                    except:
                        pass
            
            # 更新概览
            self.total_label.setText(str(total))
            self.completed_label.setText(str(completed))
            self.pending_label.setText(str(pending))
            self.overdue_label.setText(str(overdue))
            
            # 计算完成率
            complete_rate = int((completed / total * 100)) if total > 0 else 0
            self.complete_rate_bar.setValue(complete_rate)
            
            # 时间段统计
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            today_completed = 0
            week_completed = 0
            month_completed = 0
            
            for task in all_tasks:
                if task['status'] == '已完成' and task.get('completed_date'):
                    try:
                        completed_date = datetime.strptime(task['completed_date'], '%Y-%m-%d %H:%M:%S').date()
                        
                        if completed_date == today:
                            today_completed += 1
                        if completed_date >= week_ago:
                            week_completed += 1
                        if completed_date >= month_ago:
                            month_completed += 1
                    except:
                        pass
            
            self.today_completed_label.setText(str(today_completed))
            self.week_completed_label.setText(str(week_completed))
            self.month_completed_label.setText(str(month_completed))
            
            # 优先级统计
            high_count = sum(1 for t in all_tasks if t['priority'] == '高')
            medium_count = sum(1 for t in all_tasks if t['priority'] == '中')
            low_count = sum(1 for t in all_tasks if t['priority'] == '低')
            
            self.high_priority_label.setText(f"{high_count} 个")
            self.medium_priority_label.setText(f"{medium_count} 个")
            self.low_priority_label.setText(f"{low_count} 个")
            
            # 计算优先级百分比
            high_percent = int((high_count / total * 100)) if total > 0 else 0
            medium_percent = int((medium_count / total * 100)) if total > 0 else 0
            low_percent = int((low_count / total * 100)) if total > 0 else 0
            
            self.high_priority_bar.setValue(high_percent)
            self.medium_priority_bar.setValue(medium_percent)
            self.low_priority_bar.setValue(low_percent)
            
            # 分类统计（这里简化处理，因为数据库还没有分类字段）
            categories = {}
            for task in all_tasks:
                category = task.get('category', '未分类')
                categories[category] = categories.get(category, 0) + 1
            
            if categories:
                category_text = "\n".join([f"{cat}: {count} 个任务" for cat, count in categories.items()])
                self.category_info_label.setText(category_text)
            else:
                self.category_info_label.setText("暂无分类数据")
            
            print("[统计窗口] 统计数据已更新")
            
        except Exception as e:
            print(f"[统计窗口] 加载统计数据失败: {e}")
    
    def apply_theme(self, theme_name='light'):
        """
        应用主题 [v0.3.0]
        
        Args:
            theme_name: 主题名称（'light'/'dark'）
        """
        if apply_theme_to_widget:
            # 统计窗口使用设置窗口的样式
            apply_theme_to_widget(self, 'settings_window', theme_name)
            self.current_theme = theme_name
            print(f"[统计窗口] 已应用 {theme_name} 主题")
        else:
            print("[统计窗口] 主题模块不可用")
    
    def closeEvent(self, event):
        """关闭事件 - 隐藏窗口而不是退出"""
        event.ignore()
        self.hide()
        print("[统计窗口] 窗口已隐藏")


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = StatisticsWindow()
    window.show()
    
    sys.exit(app.exec_())

