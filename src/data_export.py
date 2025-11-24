#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据导出模块
Data Export Module - 导出数据为JSON、CSV等格式
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional
from PyQt5.QtWidgets import QFileDialog, QMessageBox

try:
    from src.database import Database
except ImportError:
    from database import Database


class DataExporter:
    """数据导出器"""
    
    def __init__(self, database: Database):
        """
        初始化导出器
        
        Args:
            database: 数据库实例
        """
        self.database = database
    
    def export_to_json(self, file_path: str = None, parent_widget=None) -> bool:
        """
        导出为JSON格式
        
        Args:
            file_path: 文件路径，如果为None则弹出保存对话框
            parent_widget: 父窗口
        
        Returns:
            是否成功
        """
        try:
            if not file_path:
                file_path, _ = QFileDialog.getSaveFileName(
                    parent_widget,
                    "导出数据",
                    f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "JSON文件 (*.json);;所有文件 (*.*)"
                )
                
                if not file_path:
                    return False
            
            # 收集所有数据
            data = {
                'version': '0.5.0',
                'export_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'tasks': self.database.get_all_tasks(),
                'notes': self.database.get_all_notes(),
                'tags': self.database.get_all_tags(),
                'note_categories': self.database.get_all_note_categories(),
                'task_templates': self.database.get_all_task_templates(),
                'reminder_templates': self.database.get_all_reminder_templates(),
            }
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 记录备份
            file_size = os.path.getsize(file_path)
            self.database.add_backup_record(
                backup_file_path=file_path,
                backup_type='manual',
                file_size=file_size,
                record_count=len(data['tasks']) + len(data['notes']),
                description="JSON导出"
            )
            
            if parent_widget:
                QMessageBox.information(
                    parent_widget, "导出成功", 
                    f"数据已导出到：\n{file_path}"
                )
            
            print(f"[数据导出] JSON导出成功: {file_path}")
            return True
            
        except Exception as e:
            print(f"[数据导出] JSON导出失败: {e}")
            if parent_widget:
                QMessageBox.critical(
                    parent_widget, "导出失败", 
                    f"导出数据失败：\n{str(e)}"
                )
            return False
    
    def export_to_csv(self, file_path: str = None, parent_widget=None) -> bool:
        """
        导出任务为CSV格式
        
        Args:
            file_path: 文件路径
            parent_widget: 父窗口
        
        Returns:
            是否成功
        """
        try:
            if not file_path:
                file_path, _ = QFileDialog.getSaveFileName(
                    parent_widget,
                    "导出任务",
                    f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "CSV文件 (*.csv);;所有文件 (*.*)"
                )
                
                if not file_path:
                    return False
            
            # 获取所有任务
            tasks = self.database.get_all_tasks()
            
            # 写入CSV
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 表头
                writer.writerow([
                    'ID', '标题', '描述', '截止日期', '优先级', 
                    '状态', '分类', '创建时间', '更新时间'
                ])
                
                # 数据行
                for task in tasks:
                    writer.writerow([
                        task.get('id', ''),
                        task.get('title', ''),
                        task.get('description', ''),
                        task.get('due_date', ''),
                        task.get('priority', ''),
                        task.get('status', ''),
                        task.get('category', ''),
                        task.get('created_at', ''),
                        task.get('updated_at', ''),
                    ])
            
            if parent_widget:
                QMessageBox.information(
                    parent_widget, "导出成功", 
                    f"任务已导出到：\n{file_path}"
                )
            
            print(f"[数据导出] CSV导出成功: {file_path}")
            return True
            
        except Exception as e:
            print(f"[数据导出] CSV导出失败: {e}")
            if parent_widget:
                QMessageBox.critical(
                    parent_widget, "导出失败", 
                    f"导出数据失败：\n{str(e)}"
                )
            return False
    
    def export_notes_to_txt(self, file_path: str = None, parent_widget=None) -> bool:
        """
        导出便签为TXT格式
        
        Args:
            file_path: 文件路径
            parent_widget: 父窗口
        
        Returns:
            是否成功
        """
        try:
            if not file_path:
                file_path, _ = QFileDialog.getSaveFileName(
                    parent_widget,
                    "导出便签",
                    f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    "文本文件 (*.txt);;所有文件 (*.*)"
                )
                
                if not file_path:
                    return False
            
            # 获取所有便签
            notes = self.database.get_all_notes()
            
            # 写入TXT
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"便签导出 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                for note in notes:
                    f.write(f"标题: {note.get('title', '无标题')}\n")
                    f.write(f"创建时间: {note.get('created_at', '')}\n")
                    f.write(f"更新时间: {note.get('updated_at', '')}\n")
                    f.write("-" * 60 + "\n")
                    
                    # 去除HTML标签
                    import re
                    content = note.get('content', '')
                    plain_text = re.sub(r'<[^>]+>', '', content)
                    f.write(plain_text)
                    f.write("\n\n" + "=" * 60 + "\n\n")
            
            if parent_widget:
                QMessageBox.information(
                    parent_widget, "导出成功", 
                    f"便签已导出到：\n{file_path}"
                )
            
            print(f"[数据导出] TXT导出成功: {file_path}")
            return True
            
        except Exception as e:
            print(f"[数据导出] TXT导出失败: {e}")
            if parent_widget:
                QMessageBox.critical(
                    parent_widget, "导出失败", 
                    f"导出数据失败：\n{str(e)}"
                )
            return False


# 测试代码
if __name__ == "__main__":
    print("数据导出模块测试")

