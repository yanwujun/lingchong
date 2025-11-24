#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
附件管理模块
Attachment Manager Module - 处理文件上传、缩略图生成、预览等功能
"""

import os
import shutil
import mimetypes
from datetime import datetime
from typing import Optional, List, Dict
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap, QImage

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[附件管理] PIL未安装，缩略图功能将不可用")

# 文件类型白名单
ALLOWED_IMAGE_TYPES = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
ALLOWED_DOCUMENT_TYPES = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md'}
ALLOWED_FILE_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES

# 文件大小限制（10MB）
MAX_FILE_SIZE = 10 * 1024 * 1024


class AttachmentManager:
    """附件管理器"""
    
    def __init__(self, database=None, base_path="data/attachments"):
        """
        初始化附件管理器
        
        Args:
            database: 数据库实例
            base_path: 附件存储基础路径
        """
        self.database = database
        self.base_path = base_path
        self.ensure_directories()
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        os.makedirs(self.base_path, exist_ok=True)
        os.makedirs(os.path.join(self.base_path, "tasks"), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, "notes"), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, "thumbnails"), exist_ok=True)
    
    def validate_file(self, file_path: str) -> tuple[bool, str]:
        """
        验证文件
        
        Returns:
            (是否有效, 错误信息)
        """
        if not os.path.exists(file_path):
            return False, "文件不存在"
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            return False, f"文件大小超过限制（最大{MAX_FILE_SIZE // 1024 // 1024}MB）"
        
        # 检查文件类型
        _, ext = os.path.splitext(file_path.lower())
        if ext not in ALLOWED_FILE_TYPES:
            return False, f"不支持的文件类型: {ext}"
        
        return True, ""
    
    def get_file_type(self, file_path: str) -> str:
        """获取文件MIME类型"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"
    
    def is_image(self, file_path: str) -> bool:
        """判断是否为图片文件"""
        _, ext = os.path.splitext(file_path.lower())
        return ext in ALLOWED_IMAGE_TYPES
    
    def upload_file(self, entity_type: str, entity_id: int, 
                   source_path: str, parent_widget=None) -> Optional[int]:
        """
        上传文件
        
        Args:
            entity_type: 实体类型（'task' 或 'note'）
            entity_id: 实体ID
            source_path: 源文件路径
            parent_widget: 父窗口（用于显示对话框）
        
        Returns:
            附件ID，失败返回None
        """
        # 验证文件
        is_valid, error_msg = self.validate_file(source_path)
        if not is_valid:
            if parent_widget:
                QMessageBox.warning(parent_widget, "文件验证失败", error_msg)
            return None
        
        try:
            # 生成目标路径
            file_name = os.path.basename(source_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(file_name)
            safe_name = f"{timestamp}_{name}{ext}"
            
            target_dir = os.path.join(self.base_path, entity_type + "s", str(entity_id))
            os.makedirs(target_dir, exist_ok=True)
            
            target_path = os.path.join(target_dir, safe_name)
            
            # 复制文件
            shutil.copy2(source_path, target_path)
            
            # 生成缩略图（如果是图片）
            thumbnail_path = None
            if self.is_image(source_path) and PIL_AVAILABLE:
                thumbnail_path = self.generate_thumbnail(source_path, entity_type, entity_id, safe_name)
            
            # 获取文件信息
            file_size = os.path.getsize(target_path)
            file_type = self.get_file_type(source_path)
            
            # 保存到数据库
            if self.database:
                attachment_id = self.database.add_attachment(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    file_name=file_name,
                    file_path=target_path,
                    file_size=file_size,
                    file_type=file_type,
                    thumbnail_path=thumbnail_path
                )
                
                if attachment_id > 0:
                    print(f"[附件管理] 上传成功: {file_name}")
                    return attachment_id
            
            return None
            
        except Exception as e:
            print(f"[附件管理] 上传失败: {e}")
            if parent_widget:
                QMessageBox.critical(parent_widget, "上传失败", f"文件上传失败：\n{str(e)}")
            return None
    
    def generate_thumbnail(self, image_path: str, entity_type: str, 
                          entity_id: int, file_name: str, 
                          max_size: tuple[int, int] = (200, 200)) -> Optional[str]:
        """
        生成缩略图
        
        Args:
            image_path: 原图路径
            entity_type: 实体类型
            entity_id: 实体ID
            file_name: 文件名
            max_size: 最大尺寸（宽，高）
        
        Returns:
            缩略图路径，失败返回None
        """
        if not PIL_AVAILABLE:
            return None
        
        try:
            # 打开图片
            img = Image.open(image_path)
            
            # 转换为RGB（如果是RGBA）
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # 生成缩略图
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 保存缩略图
            name, ext = os.path.splitext(file_name)
            thumbnail_name = f"thumb_{name}.jpg"
            thumbnail_dir = os.path.join(self.base_path, "thumbnails", entity_type + "s", str(entity_id))
            os.makedirs(thumbnail_dir, exist_ok=True)
            
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_name)
            img.save(thumbnail_path, "JPEG", quality=85)
            
            return thumbnail_path
            
        except Exception as e:
            print(f"[附件管理] 生成缩略图失败: {e}")
            return None
    
    def get_attachment_path(self, attachment_id: int) -> Optional[str]:
        """获取附件文件路径"""
        if not self.database:
            return None
        
        # 这里需要从数据库获取附件信息
        # 为了简化，假设有get_attachment方法
        # 实际使用时需要实现
        return None
    
    def delete_attachment(self, attachment_id: int, parent_widget=None) -> bool:
        """
        删除附件
        
        Args:
            attachment_id: 附件ID
            parent_widget: 父窗口
        
        Returns:
            是否成功
        """
        if not self.database:
            return False
        
        try:
            # 获取附件信息（需要实现get_attachment方法）
            # 这里简化处理
            if self.database.delete_attachment(attachment_id):
                print(f"[附件管理] 删除附件成功: ID={attachment_id}")
                return True
            return False
            
        except Exception as e:
            print(f"[附件管理] 删除附件失败: {e}")
            if parent_widget:
                QMessageBox.critical(parent_widget, "删除失败", f"删除附件失败：\n{str(e)}")
            return False
    
    def get_attachment_list(self, entity_type: str, entity_id: int) -> List[Dict]:
        """获取实体的附件列表"""
        if not self.database:
            return []
        
        return self.database.get_attachments(entity_type, entity_id)
    
    def open_file_dialog(self, parent_widget=None, 
                        title="选择文件") -> Optional[str]:
        """
        打开文件选择对话框
        
        Returns:
            选中的文件路径，取消返回None
        """
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget,
            title,
            "",
            "所有支持的文件 (*.jpg *.jpeg *.png *.gif *.bmp *.webp *.pdf *.doc *.docx *.xls *.xlsx *.ppt *.pptx *.txt *.md);;"
            "图片文件 (*.jpg *.jpeg *.png *.gif *.bmp *.webp);;"
            "文档文件 (*.pdf *.doc *.docx *.xls *.xlsx *.ppt *.pptx *.txt *.md);;"
            "所有文件 (*.*)"
        )
        
        return file_path if file_path else None
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / 1024 / 1024:.1f} MB"
    
    def get_file_icon_path(self, file_type: str) -> Optional[str]:
        """获取文件类型图标路径（未来实现）"""
        # 可以根据文件类型返回对应的图标路径
        return None


# 测试代码
if __name__ == "__main__":
    print("附件管理模块测试")
    manager = AttachmentManager()
    print(f"附件存储路径: {manager.base_path}")

