#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
番茄钟核心模块
Pomodoro Core Module - 番茄钟计时器和会话管理
"""

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from datetime import datetime
from typing import Optional

class PomodoroTimer(QObject):
    """番茄钟计时器"""
    
    # 信号
    tick = pyqtSignal(int)  # 每秒触发，参数为剩余秒数
    session_started = pyqtSignal(str)  # 会话开始，参数为类型
    session_completed = pyqtSignal(str, int)  # 会话完成，参数为类型和持续时间
    session_cancelled = pyqtSignal()  # 会话取消
    
    def __init__(self, database=None):
        super().__init__()
        
        self.database = database
        
        # 计时器设置
        self.work_duration = 25 * 60  # 25分钟工作时间
        self.short_break_duration = 5 * 60  # 5分钟短休息
        self.long_break_duration = 15 * 60  # 15分钟长休息
        self.sessions_until_long_break = 4  # 4个工作会话后长休息
        
        # 当前状态
        self.is_running = False
        self.is_paused = False
        self.current_session_type = 'work'  # 'work', 'short_break', 'long_break'
        self.remaining_seconds = self.work_duration
        self.session_count = 0  # 完成的工作会话数
        self.current_task_id = None
        self.session_start_time = None
        self.current_session_id = None
        
        # 定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_tick)
        
        print("[番茄钟] 计时器初始化完成")
    
    def set_durations(self, work: int = None, short_break: int = None, long_break: int = None):
        """
        设置时长
        
        Args:
            work: 工作时长（分钟）
            short_break: 短休息时长（分钟）
            long_break: 长休息时长（分钟）
        """
        if work is not None:
            self.work_duration = work * 60
        if short_break is not None:
            self.short_break_duration = short_break * 60
        if long_break is not None:
            self.long_break_duration = long_break * 60
        
        print(f"[番茄钟] 时长设置: 工作{work}分钟, 短休息{short_break}分钟, 长休息{long_break}分钟")
    
    def start_session(self, session_type: str = 'work', task_id: Optional[int] = None):
        """
        开始番茄钟会话
        
        Args:
            session_type: 会话类型 ('work', 'short_break', 'long_break')
            task_id: 关联的任务ID
        """
        if self.is_running and not self.is_paused:
            print("[番茄钟] 已有会话正在进行")
            return False
        
        self.current_session_type = session_type
        self.current_task_id = task_id
        self.is_running = True
        self.is_paused = False
        self.session_start_time = datetime.now()
        
        # 设置剩余时间
        if session_type == 'work':
            self.remaining_seconds = self.work_duration
        elif session_type == 'short_break':
            self.remaining_seconds = self.short_break_duration
        elif session_type == 'long_break':
            self.remaining_seconds = self.long_break_duration
        else:
            self.remaining_seconds = self.work_duration
        
        # 在数据库中创建会话记录
        if self.database and session_type == 'work':
            duration = self.work_duration if session_type == 'work' else \
                      (self.short_break_duration if session_type == 'short_break' else self.long_break_duration)
            self.current_session_id = self.database.add_pomodoro_session(
                task_id=task_id,
                duration=duration,
                session_type=session_type
            )
        
        # 启动定时器（每秒触发一次）
        self.timer.start(1000)
        
        self.session_started.emit(session_type)
        print(f"[番茄钟] 开始{self.get_session_name()}会话: {self.remaining_seconds}秒")
        
        return True
    
    def pause(self):
        """暂停"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.timer.stop()
            print("[番茄钟] 暂停")
            return True
        return False
    
    def resume(self):
        """继续"""
        if self.is_running and self.is_paused:
            self.is_paused = False
            self.timer.start(1000)
            print("[番茄钟] 继续")
            return True
        return False
    
    def stop(self):
        """停止并取消当前会话"""
        if self.is_running:
            self.is_running = False
            self.is_paused = False
            self.timer.stop()
            self.session_cancelled.emit()
            print("[番茄钟] 停止")
            return True
        return False
    
    def skip(self):
        """跳过当前会话"""
        if self.is_running:
            self.complete_session()
            print("[番茄钟] 跳过当前会话")
            return True
        return False
    
    def on_timer_tick(self):
        """定时器每秒触发"""
        if not self.is_running or self.is_paused:
            return
        
        self.remaining_seconds -= 1
        self.tick.emit(self.remaining_seconds)
        
        # 检查是否完成
        if self.remaining_seconds <= 0:
            self.complete_session()
    
    def complete_session(self):
        """完成当前会话"""
        self.timer.stop()
        self.is_running = False
        self.is_paused = False
        
        # 计算实际持续时间
        if self.session_start_time:
            elapsed_time = (datetime.now() - self.session_start_time).total_seconds()
        else:
            elapsed_time = 0
        
        # 更新数据库
        if self.database and self.current_session_id:
            self.database.complete_pomodoro_session(self.current_session_id)
        
        # 如果是工作会话，增加计数
        if self.current_session_type == 'work':
            self.session_count += 1
            print(f"[番茄钟] 完成工作会话 #{self.session_count}")
        
        # 发送完成信号
        self.session_completed.emit(self.current_session_type, int(elapsed_time))
        
        # 自动开始下一个会话（可选）
        # self.start_next_session()
    
    def start_next_session(self):
        """自动开始下一个会话"""
        if self.current_session_type == 'work':
            # 工作完成后，判断是短休息还是长休息
            if self.session_count % self.sessions_until_long_break == 0:
                self.start_session('long_break')
            else:
                self.start_session('short_break')
        else:
            # 休息完成后，开始工作
            self.start_session('work', self.current_task_id)
    
    def get_session_name(self) -> str:
        """获取会话类型名称"""
        names = {
            'work': '工作',
            'short_break': '短休息',
            'long_break': '长休息'
        }
        return names.get(self.current_session_type, '未知')
    
    def get_remaining_time(self) -> tuple:
        """
        获取剩余时间
        
        Returns:
            (分钟, 秒)
        """
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return (minutes, seconds)
    
    def get_progress(self) -> float:
        """
        获取进度百分比
        
        Returns:
            0.0 到 1.0
        """
        total_duration = self.work_duration if self.current_session_type == 'work' else \
                        (self.short_break_duration if self.current_session_type == 'short_break' else self.long_break_duration)
        
        if total_duration == 0:
            return 1.0
        
        return 1.0 - (self.remaining_seconds / total_duration)
    
    def get_session_count(self) -> int:
        """获取完成的工作会话数"""
        return self.session_count
    
    def reset_session_count(self):
        """重置会话计数"""
        self.session_count = 0
        print("[番茄钟] 重置会话计数")


class PomodoroManager(QObject):
    """番茄钟管理器"""
    
    def __init__(self, database=None):
        super().__init__()
        
        self.database = database
        self.timer = PomodoroTimer(database)
        
        # 专注模式设置
        self.focus_mode_enabled = False
        self.auto_start_breaks = True
        self.auto_start_work = False
        
        print("[番茄钟] 管理器初始化完成")
    
    def start_work_session(self, task_id: Optional[int] = None):
        """开始工作会话"""
        return self.timer.start_session('work', task_id)
    
    def start_break_session(self, long_break: bool = False):
        """开始休息会话"""
        session_type = 'long_break' if long_break else 'short_break'
        return self.timer.start_session(session_type)
    
    def toggle_pause(self):
        """切换暂停/继续"""
        if self.timer.is_paused:
            return self.timer.resume()
        else:
            return self.timer.pause()
    
    def stop_session(self):
        """停止当前会话"""
        return self.timer.stop()
    
    def skip_session(self):
        """跳过当前会话"""
        return self.timer.skip()
    
    def get_statistics(self, days: int = 7) -> dict:
        """
        获取统计数据
        
        Args:
            days: 统计天数
        
        Returns:
            统计数据字典
        """
        if not self.database:
            return {}
        
        return self.database.get_pomodoro_stats(days)
    
    def enable_focus_mode(self):
        """启用专注模式"""
        self.focus_mode_enabled = True
        print("[番茄钟] 专注模式已启用")
    
    def disable_focus_mode(self):
        """禁用专注模式"""
        self.focus_mode_enabled = False
        print("[番茄钟] 专注模式已禁用")


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    print("=" * 60)
    print("番茄钟核心模块测试")
    print("=" * 60)
    
    # 创建管理器
    manager = PomodoroManager()
    
    # 连接信号
    def on_tick(remaining):
        mins, secs = manager.timer.get_remaining_time()
        print(f"  ⏱️  {mins:02d}:{secs:02d} 剩余")
    
    def on_started(session_type):
        print(f"\n✅ {manager.timer.get_session_name()}会话开始！")
    
    def on_completed(session_type, duration):
        print(f"\n🎉 {manager.timer.get_session_name()}会话完成！持续{duration}秒")
    
    manager.timer.tick.connect(on_tick)
    manager.timer.session_started.connect(on_started)
    manager.timer.session_completed.connect(on_completed)
    
    # 测试：设置为短时间（测试用）
    manager.timer.set_durations(work=0.1, short_break=0.05, long_break=0.1)  # 6秒工作，3秒休息
    
    # 开始工作会话
    print("\n开始工作会话...")
    manager.start_work_session()
    
    sys.exit(app.exec_())

