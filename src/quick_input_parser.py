#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速输入解析模块
Quick Input Parser Module - 解析快速输入语法
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple


class QuickInputParser:
    """快速输入解析器"""
    
    def __init__(self):
        """初始化解析器"""
        pass
    
    def parse(self, text: str) -> Dict:
        """
        解析快速输入文本
        
        语法示例：
        - @分类 - 设置分类
        - #标签 - 添加标签
        - 时间 - 设置时间（今天、明天、1小时后等）
        - !优先级 - 设置优先级（!低、!!中、!!!高）
        
        Args:
            text: 输入文本
        
        Returns:
            解析结果字典
        """
        result = {
            'title': '',
            'category': None,
            'tags': [],
            'due_date': None,
            'priority': 1,
            'remind_time': None,
        }
        
        # 提取分类 @分类
        category_match = re.search(r'@(\S+)', text)
        if category_match:
            result['category'] = category_match.group(1)
            text = text.replace(category_match.group(0), '').strip()
        
        # 提取标签 #标签
        tag_matches = re.findall(r'#(\S+)', text)
        if tag_matches:
            result['tags'] = tag_matches
            for tag in tag_matches:
                text = text.replace(f'#{tag}', '').strip()
        
        # 提取优先级 !低、!!中、!!!高
        priority_match = re.search(r'(!+)', text)
        if priority_match:
            priority_level = len(priority_match.group(1))
            if priority_level == 1:
                result['priority'] = 1  # 低
            elif priority_level == 2:
                result['priority'] = 2  # 中
            elif priority_level >= 3:
                result['priority'] = 3  # 高
            text = text.replace(priority_match.group(0), '').strip()
        
        # 提取时间
        time_result = self._parse_time(text)
        if time_result:
            result['due_date'] = time_result
            # 从文本中移除时间部分
            time_patterns = [
                r'今天',
                r'明天',
                r'后天',
                r'\d+小时后',
                r'\d+分钟后',
                r'\d+天后',
            ]
            for pattern in time_patterns:
                text = re.sub(pattern, '', text).strip()
        
        # 剩余文本作为标题
        result['title'] = text.strip()
        
        return result
    
    def _parse_time(self, text: str) -> Optional[str]:
        """
        解析时间表达式
        
        Args:
            text: 文本
        
        Returns:
            时间字符串（YYYY-MM-DD HH:MM:SS），失败返回None
        """
        now = datetime.now()
        
        # 今天
        if '今天' in text:
            return now.strftime("%Y-%m-%d %H:%M:%S")
        
        # 明天
        if '明天' in text:
            tomorrow = now + timedelta(days=1)
            return tomorrow.strftime("%Y-%m-%d %H:%M:%S")
        
        # 后天
        if '后天' in text:
            day_after = now + timedelta(days=2)
            return day_after.strftime("%Y-%m-%d %H:%M:%S")
        
        # X小时后
        hour_match = re.search(r'(\d+)小时后', text)
        if hour_match:
            hours = int(hour_match.group(1))
            future = now + timedelta(hours=hours)
            return future.strftime("%Y-%m-%d %H:%M:%S")
        
        # X分钟后
        minute_match = re.search(r'(\d+)分钟后', text)
        if minute_match:
            minutes = int(minute_match.group(1))
            future = now + timedelta(minutes=minutes)
            return future.strftime("%Y-%m-%d %H:%M:%S")
        
        # X天后
        day_match = re.search(r'(\d+)天后', text)
        if day_match:
            days = int(day_match.group(1))
            future = now + timedelta(days=days)
            return future.strftime("%Y-%m-%d %H:%M:%S")
        
        return None


# 测试代码
if __name__ == "__main__":
    parser = QuickInputParser()
    
    test_cases = [
        "完成项目报告 @工作 #重要 !! 明天",
        "学习Python #学习 !!! 2小时后",
        "购物 @生活 今天",
    ]
    
    for test in test_cases:
        result = parser.parse(test)
        print(f"输入: {test}")
        print(f"解析结果: {result}")
        print()

