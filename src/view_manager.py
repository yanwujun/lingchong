#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
视图管理器模块
View Manager Module - 管理多种视图模式
"""

import sys
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
from PyQt5.QtCore import Qt, pyqtSignal

try:
    from src.jingyeqian_ui import JYQButton, JYQ_COLORS
    from src.todo_window import TodoWindow
except ImportError:
    try:
        from jingyeqian_ui import JYQButton, JYQ_COLORS
        from todo_window import TodoWindow
    except ImportError:
        JYQButton = QPushButton
        JYQ_COLORS = {'primary': '#007AFF'}
        TodoWindow = QWidget


class ViewManager(QWidget):
    """视图管理器"""
    
    # 信号
    view_changed = pyqtSignal(str)
    
    def __init__(self, database=None, parent=None):
        super().__init__(parent)
        self.database = database
        self.current_view = 'list'
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 视图切换按钮
        toolbar = QHBoxLayout()
        
        self.list_btn = JYQButton("列表视图", style="primary")
        self.list_btn.clicked.connect(lambda: self.switch_view('list'))
        
        self.timeline_btn = JYQButton("时间轴", style="secondary")
        self.timeline_btn.clicked.connect(lambda: self.switch_view('timeline'))
        
        self.calendar_btn = JYQButton("日历", style="secondary")
        self.calendar_btn.clicked.connect(lambda: self.switch_view('calendar'))
        
        self.kanban_btn = JYQButton("看板", style="secondary")
        self.kanban_btn.clicked.connect(lambda: self.switch_view('kanban'))
        
        toolbar.addWidget(self.list_btn)
        toolbar.addWidget(self.timeline_btn)
        toolbar.addWidget(self.calendar_btn)
        toolbar.addWidget(self.kanban_btn)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # 视图堆叠
        self.view_stack = QStackedWidget()
        layout.addWidget(self.view_stack)
        
        # 创建默认列表视图
        self.list_view = TodoWindow(self.database) if TodoWindow != QWidget else QWidget()
        self.view_stack.addWidget(self.list_view)
        
        # 其他视图占位（未来实现）
        self.timeline_view = QWidget()
        self.calendar_view = QWidget()
        self.kanban_view = QWidget()
        
        self.view_stack.addWidget(self.timeline_view)
        self.view_stack.addWidget(self.calendar_view)
        self.view_stack.addWidget(self.kanban_view)
        
        self.setLayout(layout)
    
    def switch_view(self, view_type: str):
        """切换视图"""
        view_map = {
            'list': 0,
            'timeline': 1,
            'calendar': 2,
            'kanban': 3,
        }
        
        if view_type in view_map:
            self.current_view = view_type
            self.view_stack.setCurrentIndex(view_map[view_type])
            self.view_changed.emit(view_type)
            
            # 更新按钮样式
            self.update_button_styles(view_type)
    
    def update_button_styles(self, active_view: str):
        """更新按钮样式"""
        buttons = {
            'list': self.list_btn,
            'timeline': self.timeline_btn,
            'calendar': self.calendar_btn,
            'kanban': self.kanban_btn,
        }
        
        for view, btn in buttons.items():
            if view == active_view:
                btn.setStyle("primary")
            else:
                btn.setStyle("secondary")
    
    def save_view_settings(self):
        """保存视图设置"""
        if not self.database:
            return
        
        settings = {
            'current_view': self.current_view,
            'window_geometry': None,  # 可以保存窗口位置
        }
        
        self.database.save_view_settings(
            view_type=self.current_view,
            settings_data=json.dumps(settings)
        )
    
    def load_view_settings(self):
        """加载视图设置"""
        if not self.database:
            return
        
        settings = self.database.get_view_settings(view_type=self.current_view)
        if settings:
            try:
                data = json.loads(settings['settings_data'])
                if 'current_view' in data:
                    self.switch_view(data['current_view'])
            except:
                pass


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    manager = ViewManager()
    manager.show()
    
    sys.exit(app.exec_())

