#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具函数模块
Utils Module - 提供各种工具函数
"""

import sys
import os
import json
import configparser
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径（兼容开发环境和打包后环境）
    
    Args:
        relative_path: 相对路径
    
    Returns:
        资源文件的绝对路径
    """
    try:
        # PyInstaller 创建的临时文件夹
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        return os.path.join(base_path, relative_path)
    except Exception:
        # 如果出错，返回相对路径
        return relative_path


def load_config(config_path: str = "config.ini") -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        配置字典
    """
    config = configparser.ConfigParser()
    
    if os.path.exists(config_path):
        config.read(config_path, encoding='utf-8')
        print(f"[配置] 加载配置文件: {config_path}")
    else:
        print(f"[配置] 配置文件不存在，使用默认配置: {config_path}")
        return get_default_config()
    
    # 转换为字典
    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for key, value in config.items(section):
            # 尝试转换类型
            config_dict[section][key] = parse_value(value)
    
    return config_dict


def save_config(config_dict: Dict[str, Any], config_path: str = "config.ini") -> bool:
    """
    保存配置文件
    
    Args:
        config_dict: 配置字典
        config_path: 配置文件路径
    
    Returns:
        是否保存成功
    """
    config = configparser.ConfigParser()
    
    for section, options in config_dict.items():
        if not isinstance(options, dict):
            continue
            
        config[section] = {}
        for key, value in options.items():
            config[section][key] = str(value)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)
        print(f"[配置] 保存配置文件: {config_path}")
        return True
    except Exception as e:
        print(f"[配置] 保存配置失败: {e}")
        return False


def parse_value(value: str) -> Any:
    """
    解析配置值类型
    
    Args:
        value: 字符串值
    
    Returns:
        解析后的值
    """
    # 布尔值
    if value.lower() in ['true', 'yes', '1']:
        return True
    elif value.lower() in ['false', 'no', '0']:
        return False
    
    # 数字
    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        pass
    
    # 字符串
    return value


def get_default_config() -> Dict[str, Any]:
    """
    获取默认配置
    
    Returns:
        默认配置字典
    """
    return {
        'Pet': {
            'skin': 'default',
            'size': 128,
            'animation_speed': 1.0,
            'move_speed': 2,
            'move_frequency': 30,
        },
        'Window': {
            'always_on_top': True,
            'start_position_x': 100,
            'start_position_y': 100,
            'opacity': 1.0,
        },
        'Behavior': {
            'auto_move': True,
            'follow_mouse': False,
            'random_action': True,
            'action_interval': 10,
            'enable_gravity': True,
            'edge_bounce': True,
        },
        'Sound': {
            'enable_sound': True,
            'volume': 0.5,
            'click_sound': True,
            'reminder_sound': True,
        },
        'Reminder': {
            'enable_reminder': True,
            'reminder_method': 'both',
            'default_advance_time': 15,
            'snooze_time': 5,
            'show_notification': True,
        },
        'System': {
            'auto_start': False,
            'minimize_to_tray': True,
            'language': 'zh_CN',
            'theme': 'light',
        },
        'Database': {
            'db_path': 'data/tasks.db',
            'auto_backup': True,
            'backup_interval': 7,
        }
    }


def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: datetime对象
        format: 格式字符串
    
    Returns:
        格式化的日期字符串
    """
    return dt.strftime(format)


def parse_datetime(dt_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    解析日期时间字符串
    
    Args:
        dt_str: 日期字符串
        format: 格式字符串
    
    Returns:
        datetime对象或None
    """
    try:
        return datetime.strptime(dt_str, format)
    except ValueError:
        return None


def get_time_remaining(target_time: datetime) -> str:
    """
    获取剩余时间的人性化描述
    
    Args:
        target_time: 目标时间
    
    Returns:
        剩余时间描述
    """
    now = datetime.now()
    
    if target_time < now:
        return "已过期"
    
    delta = target_time - now
    
    if delta.days > 0:
        return f"{delta.days}天后"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"{hours}小时后"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"{minutes}分钟后"
    else:
        return "即将到期"


def calculate_remind_time(due_date: datetime, advance_minutes: int = 15) -> datetime:
    """
    计算提醒时间
    
    Args:
        due_date: 截止时间
        advance_minutes: 提前分钟数
    
    Returns:
        提醒时间
    """
    return due_date - timedelta(minutes=advance_minutes)


def export_tasks_to_json(tasks: list, file_path: str) -> bool:
    """
    导出任务到JSON文件
    
    Args:
        tasks: 任务列表
        file_path: 文件路径
    
    Returns:
        是否导出成功
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        print(f"[导出] 成功导出 {len(tasks)} 个任务到: {file_path}")
        return True
    except Exception as e:
        print(f"[导出] 导出失败: {e}")
        return False


def import_tasks_from_json(file_path: str) -> Optional[list]:
    """
    从JSON文件导入任务
    
    Args:
        file_path: 文件路径
    
    Returns:
        任务列表或None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        print(f"[导入] 成功导入 {len(tasks)} 个任务从: {file_path}")
        return tasks
    except Exception as e:
        print(f"[导入] 导入失败: {e}")
        return None


def ensure_directory(directory: str) -> bool:
    """
    确保目录存在
    
    Args:
        directory: 目录路径
    
    Returns:
        是否成功
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[工具] 创建目录: {directory}")
        return True
    except Exception as e:
        print(f"[工具] 创建目录失败: {e}")
        return False


def get_priority_text(priority: int) -> str:
    """
    获取优先级文本
    
    Args:
        priority: 优先级数值 (1-3)
    
    Returns:
        优先级文本
    """
    priority_map = {
        1: "低",
        2: "中",
        3: "高"
    }
    return priority_map.get(priority, "未知")


def get_status_text(status: str) -> str:
    """
    获取状态文本
    
    Args:
        status: 状态代码
    
    Returns:
        状态文本
    """
    status_map = {
        'pending': '待完成',
        'in_progress': '进行中',
        'completed': '已完成',
        'expired': '已过期'
    }
    return status_map.get(status, '未知')


def validate_task_data(task_data: Dict) -> tuple:
    """
    验证任务数据
    
    Args:
        task_data: 任务数据字典
    
    Returns:
        (是否有效, 错误信息)
    """
    # 检查必填字段
    if not task_data.get('title'):
        return False, "任务标题不能为空"
    
    # 检查标题长度
    if len(task_data['title']) > 200:
        return False, "任务标题不能超过200个字符"
    
    # 检查优先级
    priority = task_data.get('priority', 1)
    if priority not in [1, 2, 3]:
        return False, "优先级必须是1、2或3"
    
    # 检查截止时间格式
    if task_data.get('due_date'):
        due_date = parse_datetime(task_data['due_date'])
        if not due_date:
            return False, "截止时间格式不正确"
    
    return True, ""


def get_app_version() -> str:
    """获取应用版本号"""
    return "0.1.0"


def get_system_info() -> Dict[str, str]:
    """
    获取系统信息
    
    Returns:
        系统信息字典
    """
    import platform
    
    return {
        'system': platform.system(),
        'version': platform.version(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
    }


def log_message(message: str, level: str = "INFO"):
    """
    记录日志消息
    
    Args:
        message: 消息内容
        level: 日志级别
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("工具函数模块测试")
    print("=" * 60)
    
    # 测试配置加载
    print("\n1. 测试配置加载:")
    config = load_config()
    print(f"  宠物大小: {config.get('Pet', {}).get('size')}")
    print(f"  自动移动: {config.get('Behavior', {}).get('auto_move')}")
    
    # 测试时间格式化
    print("\n2. 测试时间处理:")
    now = datetime.now()
    print(f"  当前时间: {format_datetime(now)}")
    
    future_time = now + timedelta(hours=2, minutes=30)
    print(f"  剩余时间: {get_time_remaining(future_time)}")
    
    # 测试优先级和状态
    print("\n3. 测试文本映射:")
    print(f"  优先级1: {get_priority_text(1)}")
    print(f"  优先级3: {get_priority_text(3)}")
    print(f"  状态pending: {get_status_text('pending')}")
    print(f"  状态completed: {get_status_text('completed')}")
    
    # 测试数据验证
    print("\n4. 测试数据验证:")
    test_task = {
        'title': '测试任务',
        'priority': 2,
        'due_date': '2025-10-15 18:00:00'
    }
    valid, error = validate_task_data(test_task)
    print(f"  验证结果: {valid}, 错误: {error}")
    
    # 测试系统信息
    print("\n5. 系统信息:")
    sys_info = get_system_info()
    for key, value in sys_info.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

