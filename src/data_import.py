#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据导入模块
Data Import Module - 从JSON、CSV等格式导入数据
"""

import json
import csv
from datetime import datetime
from typing import Dict, List, Optional
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressDialog

try:
    from src.database import Database
except ImportError:
    from database import Database


class DataImporter:
    """数据导入器"""
    
    def __init__(self, database: Database):
        """
        初始化导入器
        
        Args:
            database: 数据库实例
        """
        self.database = database
    
    def import_from_json(self, file_path: str = None, parent_widget=None) -> bool:
        """
        从JSON格式导入
        
        Args:
            file_path: 文件路径，如果为None则弹出选择对话框
            parent_widget: 父窗口
        
        Returns:
            是否成功
        """
        try:
            if not file_path:
                file_path, _ = QFileDialog.getOpenFileName(
                    parent_widget,
                    "导入数据",
                    "",
                    "JSON文件 (*.json);;所有文件 (*.*)"
                )
                
                if not file_path:
                    return False
            
            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 验证数据格式
            if 'version' not in data:
                QMessageBox.warning(
                    parent_widget, "格式错误", 
                    "文件格式不正确，缺少版本信息"
                )
                return False
            
            # 确认导入
            reply = QMessageBox.question(
                parent_widget, "确认导入", 
                f"将导入以下数据：\n"
                f"- 任务: {len(data.get('tasks', []))} 条\n"
                f"- 便签: {len(data.get('notes', []))} 条\n"
                f"- 标签: {len(data.get('tags', []))} 条\n\n"
                f"是否继续？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return False
            
            # 创建进度对话框
            progress = QProgressDialog("正在导入数据...", "取消", 0, 100, parent_widget)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            imported_count = 0
            
            # 导入标签
            if 'tags' in data:
                for tag in data['tags']:
                    self.database.add_tag(tag.get('name', ''), tag.get('color', '#4CAF50'))
                    imported_count += 1
                    progress.setValue(int(imported_count / len(data.get('tags', [])) * 30))
            
            # 导入任务
            if 'tasks' in data:
                for task in data['tasks']:
                    task_id = self.database.add_task(
                        title=task.get('title', ''),
                        description=task.get('description', ''),
                        due_date=task.get('due_date'),
                        priority=task.get('priority', 1),
                        category=task.get('category', 'general'),
                        remind_time=task.get('remind_time')
                    )
                    imported_count += 1
                    progress.setValue(30 + int(imported_count / len(data.get('tasks', [])) * 50))
            
            # 导入便签
            if 'notes' in data:
                for note in data['notes']:
                    self.database.add_note(
                        title=note.get('title', ''),
                        content=note.get('content', ''),
                        color=note.get('color', '#FFFFFF'),
                        is_pinned=note.get('is_pinned', False),
                        is_locked=note.get('is_locked', False)
                    )
                    imported_count += 1
                    progress.setValue(80 + int(imported_count / len(data.get('notes', [])) * 20))
            
            progress.setValue(100)
            progress.close()
            
            QMessageBox.information(
                parent_widget, "导入成功", 
                f"成功导入 {imported_count} 条数据！"
            )
            
            print(f"[数据导入] JSON导入成功: {file_path}")
            return True
            
        except Exception as e:
            print(f"[数据导入] JSON导入失败: {e}")
            if parent_widget:
                QMessageBox.critical(
                    parent_widget, "导入失败", 
                    f"导入数据失败：\n{str(e)}"
                )
            return False
    
    def import_from_csv(self, file_path: str = None, parent_widget=None) -> bool:
        """
        从CSV格式导入任务
        
        Args:
            file_path: 文件路径
            parent_widget: 父窗口
        
        Returns:
            是否成功
        """
        try:
            if not file_path:
                file_path, _ = QFileDialog.getOpenFileName(
                    parent_widget,
                    "导入任务",
                    "",
                    "CSV文件 (*.csv);;所有文件 (*.*)"
                )
                
                if not file_path:
                    return False
            
            # 读取CSV文件
            tasks = []
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tasks.append(row)
            
            if not tasks:
                QMessageBox.warning(parent_widget, "警告", "CSV文件中没有数据")
                return False
            
            # 确认导入
            reply = QMessageBox.question(
                parent_widget, "确认导入", 
                f"将导入 {len(tasks)} 条任务，是否继续？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return False
            
            # 导入任务
            imported_count = 0
            for task in tasks:
                try:
                    priority = int(task.get('优先级', 1))
                    if priority < 1 or priority > 3:
                        priority = 1
                except:
                    priority = 1
                
                task_id = self.database.add_task(
                    title=task.get('标题', ''),
                    description=task.get('描述', ''),
                    due_date=task.get('截止日期'),
                    priority=priority,
                    category=task.get('分类', 'general')
                )
                
                if task_id > 0:
                    imported_count += 1
            else:
                pass
            
            QMessageBox.information(
                parent_widget, "导入成功", 
                f"成功导入 {imported_count} 条任务！"
            )
            
            print(f"[数据导入] CSV导入成功: {file_path}")
            return True
            
        except Exception as e:
            print(f"[数据导入] CSV导入失败: {e}")
            if parent_widget:
                QMessageBox.critical(
                    parent_widget, "导入失败", 
                    f"导入数据失败：\n{str(e)}"
                )
            return False


# 测试代码
if __name__ == "__main__":
    print("数据导入模块测试")

