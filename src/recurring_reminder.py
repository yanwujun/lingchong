#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重复提醒模块
Recurring Reminder Module - 处理重复提醒
"""

import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

try:
    from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
    from dateutil.parser import parse
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False
    print("[重复提醒] dateutil库未安装，重复提醒功能将受限")

try:
    from src.database import Database
except ImportError:
    from database import Database


class RecurringReminder:
    """重复提醒处理器"""
    
    def __init__(self, database: Database):
        """
        初始化重复提醒
        
        Args:
            database: 数据库实例
        """
        self.database = database
    
    def parse_repeat_rule(self, repeat_rule_str: str) -> Optional[Dict]:
        """
        解析重复规则字符串（JSON格式）
        
        Args:
            repeat_rule_str: JSON格式的重复规则
        
        Returns:
            解析后的规则字典
        """
        try:
            return json.loads(repeat_rule_str)
        except:
            return None
    
    def calculate_next_reminder(self, start_date: str, repeat_type: str, 
                                repeat_rule: str = None) -> Optional[str]:
        """
        计算下次提醒时间
        
        Args:
            start_date: 开始日期
            repeat_type: 重复类型（daily, weekly, monthly, yearly）
            repeat_rule: 重复规则（JSON字符串）
        
        Returns:
            下次提醒时间字符串，失败返回None
        """
        if not DATEUTIL_AVAILABLE:
            # 简单实现
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            except:
                try:
                    start = datetime.strptime(start_date, "%Y-%m-%d")
                except:
                    return None
            
            if repeat_type == 'daily':
                next_date = start + timedelta(days=1)
            elif repeat_type == 'weekly':
                next_date = start + timedelta(weeks=1)
            elif repeat_type == 'monthly':
                next_date = start + timedelta(days=30)  # 简化
            elif repeat_type == 'yearly':
                next_date = start + timedelta(days=365)  # 简化
            else:
                return None
            
            return next_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # 使用dateutil实现
        try:
            start = parse(start_date)
        except:
            return None
        
        rule_dict = self.parse_repeat_rule(repeat_rule) if repeat_rule else {}
        
        if repeat_type == 'daily':
            freq = DAILY
        elif repeat_type == 'weekly':
            freq = WEEKLY
        elif repeat_type == 'monthly':
            freq = MONTHLY
        elif repeat_type == 'yearly':
            freq = YEARLY
        else:
            return None
        
        # 生成下次提醒时间
        rule = rrule(freq, dtstart=start, count=2)
        dates = list(rule)
        
        if len(dates) > 1:
            return dates[1].strftime("%Y-%m-%d %H:%M:%S")
        
        return None
    
    def update_task_reminder(self, task_id: int):
        """
        更新任务的提醒时间（用于重复提醒）
        
        Args:
            task_id: 任务ID
        """
        if not self.database:
            return
        
        task = self.database.get_task(task_id)
        if not task:
            return
        
        repeat_type = task.get('repeat_type')
        repeat_rule = task.get('repeat_rule')
        current_remind = task.get('remind_time')
        
        if not repeat_type or not current_remind:
            return
        
        # 计算下次提醒时间
        next_remind = self.calculate_next_reminder(
            current_remind, repeat_type, repeat_rule
        )
        
        if next_remind:
            # 更新提醒时间
            self.database.update_task(task_id, remind_time=next_remind)
            print(f"[重复提醒] 任务 {task_id} 下次提醒时间: {next_remind}")
    
    def get_recurring_tasks(self) -> List[Dict]:
        """
        获取所有需要重复提醒的任务
        
        Returns:
            任务列表
        """
        if not self.database:
            return []
        
        all_tasks = self.database.get_all_tasks()
        recurring_tasks = [
            task for task in all_tasks
            if task.get('repeat_type') and task.get('remind_time')
        ]
        
        return recurring_tasks


# 测试代码
if __name__ == "__main__":
    print("重复提醒模块测试")
    
    if DATEUTIL_AVAILABLE:
        print("dateutil库可用")
    else:
        print("dateutil库不可用，使用简化实现")

