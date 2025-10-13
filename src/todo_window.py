#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
待办事项窗口模块
Todo Window Module - 负责任务的显示和管理界面
"""

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QTableWidget, QTableWidgetItem, QLabel,
                             QDialog, QFormLayout, QTextEdit, QDateTimeEdit,
                             QComboBox, QHeaderView, QMessageBox, QApplication, QShortcut)
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal
from PyQt5.QtGui import QColor, QKeySequence

# 导入音效管理器和主题
try:
    from src.sound_manager import get_sound_manager
    from src.themes import apply_theme_to_widget
    from src.modern_ui import (ModernButton, ModernInput, ModernComboBox, 
                              ModernTableWidget, ModernTextEdit, ModernCard, COLORS)
except ImportError:
    try:
        from sound_manager import get_sound_manager
        from themes import apply_theme_to_widget
        from modern_ui import (ModernButton, ModernInput, ModernComboBox, 
                              ModernTableWidget, ModernTextEdit, ModernCard, COLORS)
    except ImportError:
        get_sound_manager = None
        apply_theme_to_widget = None
        # 回退到原始组件
        ModernButton = QPushButton
        ModernInput = QLineEdit
        ModernComboBox = QComboBox
        ModernTableWidget = QTableWidget
        ModernTextEdit = QTextEdit
        ModernCard = QWidget
        COLORS = {'background': '#e0e5ec', 'surface': '#e0e5ec', 'primary': '#6366f1', 'primary_dark': '#4f46e5', 
                  'primary_light': '#a5b4fc', 'text_primary': '#4a5568', 'shadow_dark': '#a3b1c6', 'shadow_light': '#ffffff'}


class TaskDialog(QDialog):
    """任务编辑对话框"""
    
    def __init__(self, parent=None, task_data=None, database=None):
        super().__init__(parent)
        self.task_data = task_data or {}
        self.database = database  # [v0.3.0] 数据库引用用于标签操作
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("编辑任务" if self.task_data else "添加任务")
        self.setFixedSize(500, 500)  # [v0.3.0] 增加高度以容纳标签组件
        
        layout = QFormLayout()
        
        # 任务标题
        self.title_edit = ModernInput("输入任务标题...")
        if 'title' in self.task_data:
            self.title_edit.setText(self.task_data['title'])
        layout.addRow("标题*:", self.title_edit)
        
        # 任务描述
        self.desc_edit = ModernTextEdit()
        self.desc_edit.setPlaceholderText("输入任务描述（可选）...")
        self.desc_edit.setMaximumHeight(100)
        if 'description' in self.task_data:
            self.desc_edit.setPlainText(self.task_data['description'])
        layout.addRow("描述:", self.desc_edit)
        
        # 截止日期
        self.due_date_edit = QDateTimeEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDateTime(QDateTime.currentDateTime())
        if 'due_date' in self.task_data and self.task_data['due_date']:
            # 解析日期字符串
            try:
                dt = QDateTime.fromString(self.task_data['due_date'], "yyyy-MM-dd HH:mm:ss")
                if dt.isValid():
                    self.due_date_edit.setDateTime(dt)
            except:
                pass
        layout.addRow("截止日期:", self.due_date_edit)
        
        # 优先级
        self.priority_combo = ModernComboBox()
        self.priority_combo.addItems(["低", "中", "高"])
        if 'priority' in self.task_data:
            self.priority_combo.setCurrentIndex(self.task_data['priority'] - 1)
        layout.addRow("优先级:", self.priority_combo)
        
        # 分类
        self.category_combo = ModernComboBox()
        self.category_combo.addItems(["一般", "工作", "学习", "生活", "其他"])
        self.category_combo.setEditable(True)
        if 'category' in self.task_data and self.task_data['category']:
            # 设置分类
            index = self.category_combo.findText(self.task_data['category'])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                # 如果不在列表中，添加并选中
                self.category_combo.addItem(self.task_data['category'])
                self.category_combo.setCurrentText(self.task_data['category'])
        layout.addRow("分类:", self.category_combo)
        
        # 标签选择 [v0.3.0]
        tags_layout = QVBoxLayout()
        
        # 标签输入和添加
        tag_input_layout = QHBoxLayout()
        self.tag_input = ModernInput("输入新标签...")
        add_tag_btn = ModernButton("+ 添加", style="secondary")
        add_tag_btn.clicked.connect(self.add_new_tag)
        tag_input_layout.addWidget(self.tag_input)
        tag_input_layout.addWidget(add_tag_btn)
        tags_layout.addLayout(tag_input_layout)
        
        # 标签列表（使用简单的文本显示，暂不使用复杂组件）
        self.tags_label = QLabel("标签: 无")
        self.tags_label.setWordWrap(True)
        tags_layout.addWidget(self.tags_label)
        
        # 可用标签按钮
        self.tags_buttons_layout = QHBoxLayout()
        self.tags_buttons_layout.addStretch()
        tags_layout.addLayout(self.tags_buttons_layout)
        
        # 存储选中的标签ID
        self.selected_tag_ids = set()
        
        # 加载标签
        self.load_tags()
        
        layout.addRow("标签:", tags_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_btn = ModernButton("保存", style="primary")
        save_btn.clicked.connect(self.accept)
        cancel_btn = ModernButton("取消", style="secondary")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow("", button_layout)
        
        self.setLayout(layout)
    
    def load_tags(self):
        """加载标签 [v0.3.0]"""
        if not self.database:
            return
        
        # 获取所有标签
        all_tags = self.database.get_all_tags()
        
        # 如果正在编辑任务，加载任务的标签
        if 'id' in self.task_data:
            task_tags = self.database.get_task_tags(self.task_data['id'])
            self.selected_tag_ids = {tag['id'] for tag in task_tags}
        
        # 清空现有按钮
        while self.tags_buttons_layout.count() > 1:  # 保留stretch
            item = self.tags_buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 创建标签按钮
        for tag in all_tags:
            btn = QPushButton(f"🏷️ {tag['name']}")
            btn.setCheckable(True)
            btn.setChecked(tag['id'] in self.selected_tag_ids)
            btn.clicked.connect(lambda checked, tag_id=tag['id']: self.toggle_tag(tag_id, checked))
            self.tags_buttons_layout.insertWidget(self.tags_buttons_layout.count() - 1, btn)
        
        self.update_tags_label()
    
    def add_new_tag(self):
        """添加新标签 [v0.3.0]"""
        if not self.database:
            return
        
        tag_name = self.tag_input.text().strip()
        if not tag_name:
            return
        
        # 添加到数据库
        tag_id = self.database.add_tag(tag_name)
        if tag_id:
            self.tag_input.clear()
            self.load_tags()
            # 自动选中新标签
            self.selected_tag_ids.add(tag_id)
            self.load_tags()
    
    def toggle_tag(self, tag_id, checked):
        """切换标签选择 [v0.3.0]"""
        if checked:
            self.selected_tag_ids.add(tag_id)
        else:
            self.selected_tag_ids.discard(tag_id)
        self.update_tags_label()
    
    def update_tags_label(self):
        """更新标签显示 [v0.3.0]"""
        if not self.database or not self.selected_tag_ids:
            self.tags_label.setText("标签: 无")
            return
        
        # 获取选中标签的名称
        all_tags = self.database.get_all_tags()
        selected_names = [tag['name'] for tag in all_tags if tag['id'] in self.selected_tag_ids]
        
        if selected_names:
            self.tags_label.setText(f"标签: {', '.join(selected_names)}")
        else:
            self.tags_label.setText("标签: 无")
    
    def get_selected_tag_ids(self):
        """获取选中的标签ID列表 [v0.3.0]"""
        return list(self.selected_tag_ids)
    
    def get_task_data(self):
        """获取任务数据"""
        return {
            'title': self.title_edit.text(),
            'description': self.desc_edit.toPlainText(),
            'due_date': self.due_date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            'priority': self.priority_combo.currentIndex() + 1,
            'category': self.category_combo.currentText(),
        }


class TodoWindow(QWidget):
    """待办事项窗口"""
    
    # 信号
    task_added = pyqtSignal(dict)
    task_updated = pyqtSignal(int, dict)
    task_deleted = pyqtSignal(int)
    
    def __init__(self, database=None):
        super().__init__()
        self.database = database
        self.current_theme = 'light'  # 默认主题 [v0.3.0]
        self.statistics_window = None  # 统计窗口引用 [v0.3.0]
        self.init_ui()
        
        # 加载任务
        if self.database:
            self.load_tasks()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("📝 待办事项")
        self.setGeometry(100, 100, 800, 600)
        # 应用Neumorphism背景色
        self.setStyleSheet(f"QWidget {{ background-color: {COLORS['background']}; }}")
        
        # 主布局
        layout = QVBoxLayout()
        
        # 顶部工具栏
        toolbar = self.create_toolbar()
        layout.addLayout(toolbar)
        
        # 任务列表表格
        self.task_table = ModernTableWidget()
        self.task_table.setColumnCount(6)
        self.task_table.setHorizontalHeaderLabels([
            "ID", "标题", "截止时间", "优先级", "状态", "分类"
        ])
        
        # 设置表格属性
        self.task_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.task_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.task_table.horizontalHeader().setStretchLastSection(True)
        self.task_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )
        
        # 隐藏ID列
        self.task_table.setColumnHidden(0, True)
        
        # 双击编辑
        self.task_table.doubleClicked.connect(self.edit_task)
        
        layout.addWidget(self.task_table)
        
        # 底部状态栏
        status_bar = self.create_status_bar()
        layout.addLayout(status_bar)
        
        self.setLayout(layout)
        
        # 添加快捷键
        self.setup_shortcuts()
        
        # 应用主题 [v0.3.0]
        self.apply_theme(self.current_theme)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QHBoxLayout()
        
        # 添加按钮
        self.add_btn = ModernButton("➕ 添加任务", style="primary")
        self.add_btn.clicked.connect(self.add_task)
        
        # 编辑按钮
        self.edit_btn = ModernButton("✏️ 编辑", style="secondary")
        self.edit_btn.clicked.connect(self.edit_task)
        
        # 删除按钮
        self.delete_btn = ModernButton("🗑️ 删除", style="secondary")
        self.delete_btn.clicked.connect(self.delete_task)
        
        # 完成按钮
        self.complete_btn = ModernButton("✅ 完成", style="secondary")
        self.complete_btn.clicked.connect(self.complete_task)
        
        # 统计按钮 [v0.3.0]
        self.stats_btn = ModernButton("📊 统计", style="secondary")
        self.stats_btn.clicked.connect(self.show_statistics)
        
        # 搜索框
        self.search_edit = ModernInput("🔍 搜索任务...")
        self.search_edit.textChanged.connect(self.search_tasks)
        
        # 筛选下拉框
        self.filter_combo = ModernComboBox()
        self.filter_combo.addItems(["全部", "待完成", "已完成", "已过期"])
        self.filter_combo.currentTextChanged.connect(self.filter_tasks)
        
        # 添加到布局
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.edit_btn)
        toolbar.addWidget(self.delete_btn)
        toolbar.addWidget(self.complete_btn)
        toolbar.addWidget(self.stats_btn)  # [v0.3.0]
        toolbar.addStretch()
        toolbar.addWidget(QLabel("筛选:"))
        toolbar.addWidget(self.filter_combo)
        toolbar.addWidget(self.search_edit)
        
        return toolbar
    
    def create_status_bar(self):
        """创建状态栏"""
        status_bar = QHBoxLayout()
        
        self.status_label = QLabel("就绪")
        self.task_count_label = QLabel("总任务: 0")
        
        status_bar.addWidget(self.status_label)
        status_bar.addStretch()
        status_bar.addWidget(self.task_count_label)
        
        return status_bar
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+N: 新建任务
        new_task_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_task_shortcut.activated.connect(self.add_task)
        
        # Ctrl+F: 聚焦搜索框
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(lambda: self.search_edit.setFocus())
        
        # Ctrl+W: 关闭窗口
        close_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_shortcut.activated.connect(self.hide)
        
        # Delete: 删除选中任务
        delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_shortcut.activated.connect(self.delete_task)
        
        # Enter: 编辑选中任务
        edit_shortcut = QShortcut(QKeySequence("Return"), self)
        edit_shortcut.activated.connect(self.edit_task)
        
        print("[待办窗口] 快捷键已设置: Ctrl+N(新建) Ctrl+F(搜索) Ctrl+W(关闭) Delete(删除)")
    
    def load_tasks(self, status=None):
        """加载任务列表"""
        if not self.database:
            return
        
        # 获取任务
        tasks = self.database.get_all_tasks(status)
        
        # 清空表格
        self.task_table.setRowCount(0)
        
        # 填充数据
        for task in tasks:
            self.add_task_to_table(task)
        
        # 更新状态
        self.update_status()
    
    def add_task_to_table(self, task):
        """添加任务到表格"""
        row = self.task_table.rowCount()
        self.task_table.insertRow(row)
        
        # ID (隐藏列)
        self.task_table.setItem(row, 0, QTableWidgetItem(str(task['id'])))
        
        # 标题
        self.task_table.setItem(row, 1, QTableWidgetItem(task['title']))
        
        # 截止时间
        due_date = task['due_date'] if task['due_date'] else "未设置"
        self.task_table.setItem(row, 2, QTableWidgetItem(due_date))
        
        # 优先级
        priority_map = {1: "低", 2: "中", 3: "高"}
        priority_text = priority_map.get(task['priority'], "中")
        priority_item = QTableWidgetItem(priority_text)
        
        # 根据优先级设置颜色
        if task['priority'] == 3:
            priority_item.setForeground(QColor(255, 0, 0))  # 红色
        elif task['priority'] == 2:
            priority_item.setForeground(QColor(255, 165, 0))  # 橙色
        
        self.task_table.setItem(row, 3, priority_item)
        
        # 状态
        status_map = {
            'pending': '待完成',
            'completed': '已完成',
            'expired': '已过期'
        }
        status_text = status_map.get(task['status'], '未知')
        self.task_table.setItem(row, 4, QTableWidgetItem(status_text))
        
        # 分类
        self.task_table.setItem(row, 5, QTableWidgetItem(task['category']))
    
    def add_task(self):
        """添加新任务"""
        try:
            dialog = TaskDialog(self, database=self.database)  # [v0.3.0] 传递database
            if dialog.exec_() == QDialog.Accepted:
                task_data = dialog.get_task_data()
                
                # 验证标题
                if not task_data['title'].strip():
                    QMessageBox.warning(self, "警告", "任务标题不能为空！")
                    return
                
                # 获取选中的标签 [v0.3.0]
                tag_ids = dialog.get_selected_tag_ids()
                
                # 保存到数据库
                if self.database:
                    task_id = self.database.add_task(**task_data)
                    
                    if task_id > 0:
                        # 保存标签关联 [v0.3.0]
                        for tag_id in tag_ids:
                            self.database.add_task_tag(task_id, tag_id)
                        
                        task_data['id'] = task_id
                        task_data['status'] = 'pending'
                        
                        # 添加到表格
                        self.add_task_to_table(task_data)
                        self.update_status()
                        
                        # 发送信号
                        self.task_added.emit(task_data)
                        
                        self.status_label.setText(f"✅ 添加任务成功: {task_data['title']}")
                    else:
                        QMessageBox.warning(self, "错误", "添加任务失败，请查看日志")
                        self.status_label.setText("❌ 添加任务失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加任务时发生错误：\n{str(e)}")
            self.status_label.setText("❌ 添加任务失败")
            print(f"[待办窗口] 添加任务异常: {e}")
    
    def edit_task(self):
        """编辑选中的任务"""
        current_row = self.task_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要编辑的任务！")
            return
        
        # 获取任务ID
        task_id = int(self.task_table.item(current_row, 0).text())
        
        # 从数据库获取完整任务数据
        if not self.database:
            QMessageBox.warning(self, "错误", "数据库未初始化！")
            return
        
        task_data = self.database.get_task(task_id)
        if not task_data:
            QMessageBox.warning(self, "错误", f"找不到任务 ID: {task_id}")
            return
        
        # 显示编辑对话框
        dialog = TaskDialog(self, task_data, database=self.database)  # [v0.3.0] 传递database
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_task_data()
            
            # 获取新的标签 [v0.3.0]
            new_tag_ids = set(dialog.get_selected_tag_ids())
            old_tag_ids = {tag['id'] for tag in self.database.get_task_tags(task_id)}
            
            # 更新数据库
            self.database.update_task(task_id, **new_data)
            
            # 更新标签关联 [v0.3.0]
            # 删除不再需要的标签
            for tag_id in old_tag_ids - new_tag_ids:
                self.database.remove_task_tag(task_id, tag_id)
            # 添加新标签
            for tag_id in new_tag_ids - old_tag_ids:
                self.database.add_task_tag(task_id, tag_id)
            
            # 刷新列表
            self.load_tasks()
            
            # 更新状态
            self.status_label.setText(f"✅ 任务已更新: {new_data['title']}")
            
            # 发送信号
            self.task_updated.emit(task_id, new_data)
    
    def delete_task(self):
        """删除选中的任务"""
        try:
            current_row = self.task_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "警告", "请先选择要删除的任务！")
                return
            
            # 确认删除
            reply = QMessageBox.question(
                self, "确认", "确定要删除选中的任务吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 获取任务ID
                task_id = int(self.task_table.item(current_row, 0).text())
                
                # 从数据库删除
                if self.database:
                    if self.database.delete_task(task_id):
                        self.task_deleted.emit(task_id)
                        
                        # 从表格删除
                        self.task_table.removeRow(current_row)
                        self.update_status()
                        
                        self.status_label.setText("✅ 删除任务成功")
                    else:
                        QMessageBox.warning(self, "错误", "删除任务失败")
                        self.status_label.setText("❌ 删除任务失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除任务时发生错误：\n{str(e)}")
            self.status_label.setText("❌ 删除任务失败")
            print(f"[待办窗口] 删除任务异常: {e}")
    
    def complete_task(self):
        """标记任务为已完成"""
        try:
            current_row = self.task_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "警告", "请先选择要完成的任务！")
                return
            
            # 获取任务ID
            task_id = int(self.task_table.item(current_row, 0).text())
            
            # 更新数据库
            if self.database:
                if self.database.mark_completed(task_id):
                    # 更新表格
                    self.task_table.item(current_row, 4).setText("已完成")
                    self.update_status()
                    
                    self.status_label.setText("✅ 任务已完成！")
                    
                    # 播放完成音效 [v0.3.0]
                    if get_sound_manager:
                        sound_mgr = get_sound_manager()
                        sound_mgr.play_complete()
                else:
                    QMessageBox.warning(self, "错误", "标记完成失败")
                    self.status_label.setText("❌ 操作失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"标记完成时发生错误：\n{str(e)}")
            self.status_label.setText("❌ 操作失败")
            print(f"[待办窗口] 标记完成异常: {e}")
    
    def search_tasks(self, keyword):
        """搜索任务"""
        if not keyword.strip():
            # 如果搜索框为空，显示所有任务
            self.load_tasks()
            return
        
        if not self.database:
            return
        
        # 使用数据库搜索
        tasks = self.database.search_tasks(keyword)
        
        # 清空表格
        self.task_table.setRowCount(0)
        
        # 显示搜索结果
        for task in tasks:
            self.add_task_to_table(task)
        
        # 更新状态
        self.update_status()
        self.status_label.setText(f"🔍 找到 {len(tasks)} 个匹配任务")
    
    def filter_tasks(self, filter_text):
        """筛选任务"""
        status_map = {
            "全部": None,
            "待完成": "pending",
            "已完成": "completed",
            "已过期": "expired"
        }
        
        status = status_map.get(filter_text)
        self.load_tasks(status)
    
    def update_status(self):
        """更新状态栏"""
        count = self.task_table.rowCount()
        self.task_count_label.setText(f"总任务: {count}")
    
    def show_statistics(self):
        """
        显示统计窗口 [v0.3.0]
        """
        try:
            if self.statistics_window is None:
                # 延迟导入
                try:
                    from src.statistics_window import StatisticsWindow
                except ImportError:
                    from statistics_window import StatisticsWindow
                
                self.statistics_window = StatisticsWindow(self.database)
                self.statistics_window.apply_theme(self.current_theme)
            
            self.statistics_window.load_statistics()  # 刷新数据
            self.statistics_window.show()
            self.statistics_window.raise_()
            self.statistics_window.activateWindow()
            
            print("[待办窗口] 打开统计窗口")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开统计窗口失败：\n{str(e)}")
            print(f"[待办窗口] 打开统计窗口异常: {e}")
    
    def apply_theme(self, theme_name='light'):
        """
        应用主题 [v0.3.0]
        
        Args:
            theme_name: 主题名称（'light'/'dark'）
        """
        if apply_theme_to_widget:
            apply_theme_to_widget(self, 'todo_window', theme_name)
            self.current_theme = theme_name
            print(f"[待办窗口] 已应用 {theme_name} 主题")
            
            # 同步主题到统计窗口
            if self.statistics_window:
                self.statistics_window.apply_theme(theme_name)
        else:
            print("[待办窗口] 主题模块不可用")
    
    def closeEvent(self, event):
        """关闭事件 - 隐藏窗口而不是退出"""
        event.ignore()  # 忽略关闭事件
        self.hide()     # 隐藏窗口
        print("[待办窗口] 窗口已隐藏")


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = TodoWindow()
    window.show()
    
    sys.exit(app.exec_())

