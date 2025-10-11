#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志系统模块
Logger Module - 统一的日志管理
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


class Logger:
    """日志管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化日志系统"""
        if self._initialized:
            return
        
        self._initialized = True
        
        # 确保日志目录存在
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志文件名
        log_file = os.path.join(log_dir, f"desktop_pet_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 配置根日志器
        self.logger = logging.getLogger("DesktopPet")
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if self.logger.handlers:
            return
        
        # 文件处理器（带轮转）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 日志格式
        detailed_formatter = logging.Formatter(
            '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '[%(name)s] [%(levelname)s] %(message)s'
        )
        
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("=" * 60)
        self.logger.info("日志系统初始化成功")
        self.logger.info(f"日志文件: {log_file}")
        self.logger.info("=" * 60)
    
    def get_logger(self, name=None):
        """
        获取日志器
        
        Args:
            name: 日志器名称
        
        Returns:
            Logger对象
        """
        if name:
            return logging.getLogger(f"DesktopPet.{name}")
        return self.logger
    
    def debug(self, message):
        """调试级别日志"""
        self.logger.debug(message)
    
    def info(self, message):
        """信息级别日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """警告级别日志"""
        self.logger.warning(message)
    
    def error(self, message):
        """错误级别日志"""
        self.logger.error(message)
    
    def critical(self, message):
        """严重错误级别日志"""
        self.logger.critical(message)
    
    def exception(self, message):
        """异常日志（包含堆栈信息）"""
        self.logger.exception(message)


# 全局日志器实例
_logger_instance = None

def get_logger(name=None):
    """
    获取全局日志器
    
    Args:
        name: 模块名称
    
    Returns:
        Logger对象
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger()
    
    if name:
        return _logger_instance.get_logger(name)
    return _logger_instance.logger


# 便捷函数
def debug(message):
    """调试日志"""
    get_logger().debug(message)

def info(message):
    """信息日志"""
    get_logger().info(message)

def warning(message):
    """警告日志"""
    get_logger().warning(message)

def error(message):
    """错误日志"""
    get_logger().error(message)

def critical(message):
    """严重错误日志"""
    get_logger().critical(message)

def exception(message):
    """异常日志"""
    get_logger().exception(message)


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("日志系统测试")
    print("=" * 60)
    
    # 获取日志器
    logger = get_logger("Test")
    
    # 测试不同级别的日志
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    
    # 测试异常日志
    try:
        1 / 0
    except Exception:
        logger.exception("发生异常")
    
    print("\n" + "=" * 60)
    print("日志已写入 logs 目录")
    print("=" * 60)

