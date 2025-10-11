#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库模块
Database Module - 负责待办事项的数据存储和管理
"""

import sqlite3
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class Database:
    """数据库管理类"""
    
    def __init__(self, db_path="data/tasks.db"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        
        # 确保数据目录存在
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # 创建数据库连接
        self.conn = None
        self.cursor = None
        
        # 初始化数据库
        self.init_database()
    
    def connect(self):
        """连接数据库"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
            self.cursor = self.conn.cursor()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def init_database(self):
        """初始化数据库表结构"""
        self.connect()
        
        # 创建任务表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                priority INTEGER DEFAULT 1,
                status TEXT DEFAULT 'pending',
                category TEXT DEFAULT 'general',
                remind_time TEXT,
                repeat_type TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # 创建配置表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # 创建标签表 [v0.3.0]
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT DEFAULT '#4CAF50',
                created_at TEXT NOT NULL
            )
        """)
        
        # 创建任务标签关联表 [v0.3.0]
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_tags (
                task_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (task_id, tag_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)
        
        # ========== v0.4.0 新增表 ==========
        
        # 创建番茄钟会话表 [v0.4.0]
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration INTEGER NOT NULL,
                completed BOOLEAN DEFAULT 0,
                session_type TEXT DEFAULT 'work',
                created_at TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
            )
        """)
        
        # 创建宠物数据表 [v0.4.0]
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                pet_type TEXT DEFAULT 'cat',
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                hunger INTEGER DEFAULT 100,
                happiness INTEGER DEFAULT 100,
                health INTEGER DEFAULT 100,
                energy INTEGER DEFAULT 100,
                is_active BOOLEAN DEFAULT 1,
                position_x INTEGER DEFAULT 100,
                position_y INTEGER DEFAULT 100,
                skin TEXT DEFAULT 'default',
                evolution_stage INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                last_fed_at TEXT,
                last_played_at TEXT
            )
        """)
        
        # 创建成就表 [v0.4.0]
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                achievement_type TEXT NOT NULL,
                achievement_name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                unlocked_at TEXT NOT NULL,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
            )
        """)
        
        # 创建道具背包表 [v0.4.0]
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                item_type TEXT NOT NULL,
                item_effect TEXT,
                quantity INTEGER DEFAULT 1,
                acquired_at TEXT NOT NULL,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
            )
        """)
        
        # 创建AI对话历史表 [v0.4.0]
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                tokens_used INTEGER DEFAULT 0,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE SET NULL
            )
        """)
        
        # 创建图片识别任务表 [v0.4.0]
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                image_hash TEXT,
                recognition_result TEXT,
                task_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
            )
        """)
        
        # 添加任务表新字段（如果不存在）[v0.4.0]
        try:
            self.cursor.execute("ALTER TABLE tasks ADD COLUMN completed_date TEXT")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        try:
            self.cursor.execute("ALTER TABLE tasks ADD COLUMN pomodoro_count INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # 字段已存在
        
        self.conn.commit()
        print(f"[数据库] 初始化成功: {self.db_path}")
    
    def add_task(self, title: str, description: str = "", due_date: str = None,
                 priority: int = 1, category: str = "general", 
                 remind_time: str = None, repeat_type: str = None) -> int:
        """
        添加新任务
        
        Args:
            title: 任务标题
            description: 任务描述
            due_date: 截止日期 (格式: YYYY-MM-DD HH:MM:SS)
            priority: 优先级 (1=低, 2=中, 3=高)
            category: 分类
            remind_time: 提醒时间
            repeat_type: 重复类型 (daily, weekly, monthly)
        
        Returns:
            新任务的ID，失败返回-1
        """
        try:
            self.connect()
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute("""
                INSERT INTO tasks (title, description, due_date, priority, 
                                 category, remind_time, repeat_type, 
                                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, description, due_date, priority, category, 
                  remind_time, repeat_type, now, now))
            
            self.conn.commit()
            task_id = self.cursor.lastrowid
            
            print(f"[数据库] 添加任务成功: ID={task_id}, 标题={title}")
            return task_id
        except Exception as e:
            print(f"[数据库] 添加任务失败: {e}")
            if self.conn:
                self.conn.rollback()
            return -1
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """
        获取指定任务
        
        Args:
            task_id: 任务ID
        
        Returns:
            任务字典或None
        """
        self.connect()
        
        self.cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = self.cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_all_tasks(self, status: str = None) -> List[Dict]:
        """
        获取所有任务
        
        Args:
            status: 状态筛选 (pending, completed, expired)
        
        Returns:
            任务列表
        """
        self.connect()
        
        if status:
            self.cursor.execute(
                "SELECT * FROM tasks WHERE status = ? ORDER BY due_date",
                (status,)
            )
        else:
            self.cursor.execute("SELECT * FROM tasks ORDER BY due_date")
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_today_tasks(self) -> List[Dict]:
        """获取今日任务"""
        self.connect()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        self.cursor.execute("""
            SELECT * FROM tasks 
            WHERE date(due_date) = ? AND status = 'pending'
            ORDER BY due_date
        """, (today,))
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_pending_reminders(self) -> List[Dict]:
        """获取待提醒的任务"""
        self.connect()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.cursor.execute("""
            SELECT * FROM tasks 
            WHERE status = 'pending' 
            AND remind_time IS NOT NULL 
            AND remind_time <= ?
            ORDER BY remind_time
        """, (now,))
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            **kwargs: 要更新的字段
        
        Returns:
            是否更新成功
        """
        self.connect()
        
        # 添加更新时间
        kwargs['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 构建SQL语句
        fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [task_id]
        
        self.cursor.execute(
            f"UPDATE tasks SET {fields} WHERE id = ?",
            values
        )
        
        self.conn.commit()
        success = self.cursor.rowcount > 0
        
        if success:
            print(f"[数据库] 更新任务成功: ID={task_id}")
        
        return success
    
    def delete_task(self, task_id: int) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
        
        Returns:
            是否删除成功
        """
        self.connect()
        
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
        
        success = self.cursor.rowcount > 0
        
        if success:
            print(f"[数据库] 删除任务成功: ID={task_id}")
        
        return success
    
    def mark_completed(self, task_id: int) -> bool:
        """标记任务为已完成"""
        return self.update_task(task_id, status='completed')
    
    def mark_expired(self, task_id: int) -> bool:
        """标记任务为已过期"""
        return self.update_task(task_id, status='expired')
    
    def search_tasks(self, keyword: str) -> List[Dict]:
        """
        搜索任务
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            匹配的任务列表
        """
        self.connect()
        
        pattern = f"%{keyword}%"
        
        self.cursor.execute("""
            SELECT * FROM tasks 
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY due_date
        """, (pattern, pattern))
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict:
        """获取任务统计信息"""
        self.connect()
        
        stats = {}
        
        # 总任务数
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        stats['total'] = self.cursor.fetchone()[0]
        
        # 待完成
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
        stats['pending'] = self.cursor.fetchone()[0]
        
        # 已完成
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
        stats['completed'] = self.cursor.fetchone()[0]
        
        # 已过期
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'expired'")
        stats['expired'] = self.cursor.fetchone()[0]
        
        return stats
    
    def auto_backup(self, backup_dir="backups", keep_days=7) -> bool:
        """
        自动备份数据库
        
        Args:
            backup_dir: 备份目录
            keep_days: 保留天数
        
        Returns:
            是否备份成功
        """
        try:
            # 确保备份目录存在
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"tasks_backup_{timestamp}.db")
            
            # 关闭当前连接
            if self.conn:
                self.conn.close()
                self.conn = None
            
            # 复制数据库文件
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_file)
                print(f"[数据库] 备份成功: {backup_file}")
                
                # 清理旧备份
                self.clean_old_backups(backup_dir, keep_days)
                
                return True
            else:
                print(f"[数据库] 数据库文件不存在: {self.db_path}")
                return False
                
        except Exception as e:
            print(f"[数据库] 备份失败: {e}")
            return False
    
    def clean_old_backups(self, backup_dir, keep_days=7):
        """
        清理旧的备份文件
        
        Args:
            backup_dir: 备份目录
            keep_days: 保留天数
        """
        try:
            if not os.path.exists(backup_dir):
                return
            
            # 计算过期时间
            cutoff_time = datetime.now() - timedelta(days=keep_days)
            
            # 遍历备份文件
            for filename in os.listdir(backup_dir):
                if filename.startswith("tasks_backup_") and filename.endswith(".db"):
                    filepath = os.path.join(backup_dir, filename)
                    
                    # 获取文件修改时间
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    # 删除过期备份
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        print(f"[数据库] 删除旧备份: {filename}")
                        
        except Exception as e:
            print(f"[数据库] 清理备份失败: {e}")
    
    # ========== 标签管理方法 [v0.3.0] ==========
    
    def add_tag(self, name: str, color: str = '#4CAF50') -> Optional[int]:
        """
        添加新标签
        
        Args:
            name: 标签名称
            color: 标签颜色（十六进制）
        
        Returns:
            标签ID，失败返回None
        """
        try:
            self.connect()
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute("""
                INSERT INTO tags (name, color, created_at)
                VALUES (?, ?, ?)
            """, (name, color, created_at))
            
            self.conn.commit()
            tag_id = self.cursor.lastrowid
            print(f"[数据库] 添加标签成功: ID={tag_id}, 名称={name}")
            return tag_id
            
        except sqlite3.IntegrityError:
            print(f"[数据库] 标签已存在: {name}")
            # 返回现有标签的ID
            self.cursor.execute("SELECT id FROM tags WHERE name = ?", (name,))
            row = self.cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(f"[数据库] 添加标签失败: {e}")
            self.conn.rollback()
            return None
    
    def get_all_tags(self) -> List[Dict]:
        """获取所有标签"""
        self.connect()
        
        self.cursor.execute("SELECT * FROM tags ORDER BY name")
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_tag_by_name(self, name: str) -> Optional[Dict]:
        """根据名称获取标签"""
        self.connect()
        
        self.cursor.execute("SELECT * FROM tags WHERE name = ?", (name,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def delete_tag(self, tag_id: int) -> bool:
        """
        删除标签
        
        Args:
            tag_id: 标签ID
        
        Returns:
            是否成功
        """
        try:
            self.connect()
            
            # 删除标签（关联关系会自动删除）
            self.cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
            self.conn.commit()
            
            print(f"[数据库] 删除标签成功: ID={tag_id}")
            return True
            
        except Exception as e:
            print(f"[数据库] 删除标签失败: {e}")
            self.conn.rollback()
            return False
    
    def add_task_tag(self, task_id: int, tag_id: int) -> bool:
        """
        为任务添加标签
        
        Args:
            task_id: 任务ID
            tag_id: 标签ID
        
        Returns:
            是否成功
        """
        try:
            self.connect()
            
            self.cursor.execute("""
                INSERT OR IGNORE INTO task_tags (task_id, tag_id)
                VALUES (?, ?)
            """, (task_id, tag_id))
            
            self.conn.commit()
            print(f"[数据库] 添加任务标签成功: task_id={task_id}, tag_id={tag_id}")
            return True
            
        except Exception as e:
            print(f"[数据库] 添加任务标签失败: {e}")
            self.conn.rollback()
            return False
    
    def remove_task_tag(self, task_id: int, tag_id: int) -> bool:
        """
        移除任务标签
        
        Args:
            task_id: 任务ID
            tag_id: 标签ID
        
        Returns:
            是否成功
        """
        try:
            self.connect()
            
            self.cursor.execute("""
                DELETE FROM task_tags 
                WHERE task_id = ? AND tag_id = ?
            """, (task_id, tag_id))
            
            self.conn.commit()
            print(f"[数据库] 移除任务标签成功: task_id={task_id}, tag_id={tag_id}")
            return True
            
        except Exception as e:
            print(f"[数据库] 移除任务标签失败: {e}")
            self.conn.rollback()
            return False
    
    def get_task_tags(self, task_id: int) -> List[Dict]:
        """
        获取任务的所有标签
        
        Args:
            task_id: 任务ID
        
        Returns:
            标签列表
        """
        self.connect()
        
        self.cursor.execute("""
            SELECT t.* FROM tags t
            INNER JOIN task_tags tt ON t.id = tt.tag_id
            WHERE tt.task_id = ?
            ORDER BY t.name
        """, (task_id,))
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_tasks_by_tag(self, tag_id: int) -> List[Dict]:
        """
        获取具有指定标签的所有任务
        
        Args:
            tag_id: 标签ID
        
        Returns:
            任务列表
        """
        self.connect()
        
        self.cursor.execute("""
            SELECT t.* FROM tasks t
            INNER JOIN task_tags tt ON t.id = tt.task_id
            WHERE tt.tag_id = ?
            ORDER BY t.due_date
        """, (tag_id,))
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    # ========== v0.4.0 新增方法 ==========
    
    # --- 番茄钟相关 ---
    
    def add_pomodoro_session(self, task_id: Optional[int], duration: int, 
                            session_type: str = 'work') -> int:
        """
        添加番茄钟会话记录
        
        Args:
            task_id: 关联的任务ID
            duration: 持续时间（秒）
            session_type: 会话类型 ('work' 或 'break')
        
        Returns:
            会话ID
        """
        try:
            self.connect()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute("""
                INSERT INTO pomodoro_sessions 
                (task_id, start_time, duration, session_type, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (task_id, now, duration, session_type, now))
            
            self.conn.commit()
            session_id = self.cursor.lastrowid
            print(f"[数据库] 添加番茄钟会话: ID={session_id}")
            return session_id
        except Exception as e:
            print(f"[数据库] 添加番茄钟会话失败: {e}")
            self.conn.rollback()
            return 0
    
    def complete_pomodoro_session(self, session_id: int) -> bool:
        """完成番茄钟会话"""
        try:
            self.connect()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute("""
                UPDATE pomodoro_sessions 
                SET completed = 1, end_time = ?
                WHERE id = ?
            """, (now, session_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[数据库] 完成番茄钟会话失败: {e}")
            self.conn.rollback()
            return False
    
    def get_pomodoro_stats(self, days: int = 7) -> Dict:
        """获取番茄钟统计数据"""
        self.connect()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_sessions,
                SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_sessions,
                SUM(CASE WHEN session_type = 'work' THEN duration ELSE 0 END) as work_time,
                SUM(CASE WHEN session_type = 'break' THEN duration ELSE 0 END) as break_time
            FROM pomodoro_sessions
            WHERE DATE(created_at) >= ?
        """, (cutoff_date,))
        
        row = self.cursor.fetchone()
        return dict(row) if row else {}
    
    # --- 宠物相关 ---
    
    def create_pet(self, name: str, pet_type: str = 'cat') -> int:
        """
        创建新宠物
        
        Args:
            name: 宠物名称
            pet_type: 宠物类型
        
        Returns:
            宠物ID
        """
        try:
            self.connect()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute("""
                INSERT INTO pets 
                (name, pet_type, created_at)
                VALUES (?, ?, ?)
            """, (name, pet_type, now))
            
            self.conn.commit()
            pet_id = self.cursor.lastrowid
            print(f"[数据库] 创建宠物: ID={pet_id}, 名称={name}")
            return pet_id
        except Exception as e:
            print(f"[数据库] 创建宠物失败: {e}")
            self.conn.rollback()
            return 0
    
    def get_pet(self, pet_id: int) -> Optional[Dict]:
        """获取宠物信息"""
        self.connect()
        
        self.cursor.execute("SELECT * FROM pets WHERE id = ?", (pet_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_active_pet(self) -> Optional[Dict]:
        """获取当前激活的宠物"""
        self.connect()
        
        self.cursor.execute("SELECT * FROM pets WHERE is_active = 1 LIMIT 1")
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_pets(self) -> List[Dict]:
        """获取所有宠物"""
        self.connect()
        
        self.cursor.execute("SELECT * FROM pets ORDER BY created_at")
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_pet(self, pet_id: int, **kwargs) -> bool:
        """更新宠物信息"""
        try:
            self.connect()
            
            # 构建更新语句
            fields = []
            values = []
            for key, value in kwargs.items():
                fields.append(f"{key} = ?")
                values.append(value)
            
            if not fields:
                return False
            
            values.append(pet_id)
            query = f"UPDATE pets SET {', '.join(fields)} WHERE id = ?"
            
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[数据库] 更新宠物失败: {e}")
            self.conn.rollback()
            return False
    
    def add_experience(self, pet_id: int, exp: int) -> bool:
        """增加宠物经验值"""
        try:
            self.connect()
            
            self.cursor.execute("""
                UPDATE pets 
                SET experience = experience + ?
                WHERE id = ?
            """, (exp, pet_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[数据库] 增加经验失败: {e}")
            self.conn.rollback()
            return False
    
    # --- 成就相关 ---
    
    def unlock_achievement(self, pet_id: int, achievement_type: str, 
                          achievement_name: str, description: str = "") -> int:
        """解锁成就"""
        try:
            self.connect()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 检查是否已解锁
            self.cursor.execute("""
                SELECT id FROM achievements 
                WHERE pet_id = ? AND achievement_name = ?
            """, (pet_id, achievement_name))
            
            if self.cursor.fetchone():
                return 0  # 已解锁
            
            self.cursor.execute("""
                INSERT INTO achievements 
                (pet_id, achievement_type, achievement_name, description, unlocked_at)
                VALUES (?, ?, ?, ?, ?)
            """, (pet_id, achievement_type, achievement_name, description, now))
            
            self.conn.commit()
            achievement_id = self.cursor.lastrowid
            print(f"[数据库] 解锁成就: {achievement_name}")
            return achievement_id
        except Exception as e:
            print(f"[数据库] 解锁成就失败: {e}")
            self.conn.rollback()
            return 0
    
    def get_pet_achievements(self, pet_id: int) -> List[Dict]:
        """获取宠物的所有成就"""
        self.connect()
        
        self.cursor.execute("""
            SELECT * FROM achievements 
            WHERE pet_id = ?
            ORDER BY unlocked_at DESC
        """, (pet_id,))
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    # --- 道具相关 ---
    
    def add_item(self, pet_id: int, item_name: str, item_type: str, 
                item_effect: str = "", quantity: int = 1) -> int:
        """添加道具到背包"""
        try:
            self.connect()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 检查是否已有该道具
            self.cursor.execute("""
                SELECT id, quantity FROM inventory 
                WHERE pet_id = ? AND item_name = ?
            """, (pet_id, item_name))
            
            row = self.cursor.fetchone()
            if row:
                # 增加数量
                new_quantity = row['quantity'] + quantity
                self.cursor.execute("""
                    UPDATE inventory 
                    SET quantity = ?
                    WHERE id = ?
                """, (new_quantity, row['id']))
                item_id = row['id']
            else:
                # 新增道具
                self.cursor.execute("""
                    INSERT INTO inventory 
                    (pet_id, item_name, item_type, item_effect, quantity, acquired_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (pet_id, item_name, item_type, item_effect, quantity, now))
                item_id = self.cursor.lastrowid
            
            self.conn.commit()
            print(f"[数据库] 添加道具: {item_name} x{quantity}")
            return item_id
        except Exception as e:
            print(f"[数据库] 添加道具失败: {e}")
            self.conn.rollback()
            return 0
    
    def use_item(self, pet_id: int, item_name: str, quantity: int = 1) -> bool:
        """使用道具"""
        try:
            self.connect()
            
            self.cursor.execute("""
                SELECT id, quantity FROM inventory 
                WHERE pet_id = ? AND item_name = ?
            """, (pet_id, item_name))
            
            row = self.cursor.fetchone()
            if not row or row['quantity'] < quantity:
                return False
            
            new_quantity = row['quantity'] - quantity
            if new_quantity > 0:
                self.cursor.execute("""
                    UPDATE inventory 
                    SET quantity = ?
                    WHERE id = ?
                """, (new_quantity, row['id']))
            else:
                self.cursor.execute("DELETE FROM inventory WHERE id = ?", (row['id'],))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[数据库] 使用道具失败: {e}")
            self.conn.rollback()
            return False
    
    def get_inventory(self, pet_id: int) -> List[Dict]:
        """获取宠物背包"""
        self.connect()
        
        self.cursor.execute("""
            SELECT * FROM inventory 
            WHERE pet_id = ?
            ORDER BY acquired_at DESC
        """, (pet_id,))
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    # --- 对话相关 ---
    
    def add_chat_message(self, pet_id: Optional[int], role: str, message: str, 
                        tokens_used: int = 0) -> int:
        """添加对话消息"""
        try:
            self.connect()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute("""
                INSERT INTO chat_history 
                (pet_id, role, message, timestamp, tokens_used)
                VALUES (?, ?, ?, ?, ?)
            """, (pet_id, role, message, now, tokens_used))
            
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"[数据库] 添加对话消息失败: {e}")
            self.conn.rollback()
            return 0
    
    def get_chat_history(self, pet_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
        """获取对话历史"""
        self.connect()
        
        if pet_id is not None:
            self.cursor.execute("""
                SELECT * FROM chat_history 
                WHERE pet_id = ? OR pet_id IS NULL
                ORDER BY timestamp DESC
                LIMIT ?
            """, (pet_id, limit))
        else:
            self.cursor.execute("""
                SELECT * FROM chat_history 
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in reversed(rows)]  # 返回正序
    
    def clear_chat_history(self, pet_id: Optional[int] = None) -> bool:
        """清除对话历史"""
        try:
            self.connect()
            
            if pet_id is not None:
                self.cursor.execute("DELETE FROM chat_history WHERE pet_id = ?", (pet_id,))
            else:
                self.cursor.execute("DELETE FROM chat_history")
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[数据库] 清除对话历史失败: {e}")
            self.conn.rollback()
            return False
    
    # --- 图片识别相关 ---
    
    def add_image_task(self, image_path: str, recognition_result: str, 
                      task_id: Optional[int] = None, image_hash: str = "") -> int:
        """添加图片识别记录"""
        try:
            self.connect()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute("""
                INSERT INTO image_tasks 
                (image_path, image_hash, recognition_result, task_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (image_path, image_hash, recognition_result, task_id, now))
            
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"[数据库] 添加图片识别记录失败: {e}")
            self.conn.rollback()
            return 0
    
    def get_image_tasks(self, limit: int = 20) -> List[Dict]:
        """获取图片识别记录"""
        self.connect()
        
        self.cursor.execute("""
            SELECT * FROM image_tasks 
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("数据库模块测试")
    print("=" * 60)
    
    # 创建数据库实例
    db = Database("data/test_tasks.db")
    
    # 测试添加任务
    task_id1 = db.add_task(
        title="完成项目文档",
        description="编写桌面灵宠的开发文档",
        due_date="2025-10-15 18:00:00",
        priority=3,
        category="work"
    )
    
    task_id2 = db.add_task(
        title="学习PyQt5",
        description="学习PyQt5的窗口和动画功能",
        due_date="2025-10-20 12:00:00",
        priority=2,
        category="study"
    )
    
    # 测试获取所有任务
    print("\n所有任务：")
    tasks = db.get_all_tasks()
    for task in tasks:
        print(f"  [{task['id']}] {task['title']} - 优先级:{task['priority']}")
    
    # 测试更新任务
    print("\n更新任务...")
    db.update_task(task_id1, status="completed")
    
    # 测试统计
    print("\n任务统计：")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 测试搜索
    print("\n搜索'PyQt'：")
    results = db.search_tasks("PyQt")
    for task in results:
        print(f"  [{task['id']}] {task['title']}")
    
    # 关闭数据库
    db.close()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

