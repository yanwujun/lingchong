#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成占位图片 - 用于测试的简单宠物图片
Generate Placeholder Images - Simple pet images for testing
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_pet(text, filename, size=128, bg_color=(255, 200, 200, 255), text_color=(50, 50, 50)):
    """
    创建占位宠物图片
    
    Args:
        text: 显示的文字/表情
        filename: 保存的文件名
        size: 图片大小
        bg_color: 背景颜色 (RGBA)
        text_color: 文字颜色
    """
    # 创建图片
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形背景
    padding = 10
    draw.ellipse(
        [padding, padding, size - padding, size - padding],
        fill=bg_color,
        outline=(100, 100, 100, 255),
        width=3
    )
    
    # 尝试加载字体，失败则使用默认字体
    try:
        # 尝试使用系统字体
        font_size = size // 2
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            # Windows 中文字体
            font_size = size // 2
            font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", font_size)
        except:
            # 使用默认字体
            font = ImageFont.load_default()
    
    # 获取文本边界框
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # 计算居中位置
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 5
    
    # 绘制文字
    draw.text((x, y), text, fill=text_color, font=font)
    
    # 保存图片
    img.save(filename, 'PNG')
    print(f"[OK] 创建图片: {filename}")


def main():
    """主函数"""
    # 确保目录存在
    output_dir = "assets/images/default"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("开始生成占位宠物图片...")
    print("=" * 60)
    
    # 生成不同状态的图片
    pets = [
        {
            'text': '🐱',
            'filename': f'{output_dir}/idle.png',
            'bg_color': (255, 220, 220, 255),
            'description': '待机状态'
        },
        {
            'text': '🐱',
            'filename': f'{output_dir}/walk.png',
            'bg_color': (220, 255, 220, 255),
            'description': '行走状态'
        },
        {
            'text': '😺',
            'filename': f'{output_dir}/happy.png',
            'bg_color': (255, 255, 150, 255),
            'description': '开心状态'
        },
        {
            'text': '❗',
            'filename': f'{output_dir}/alert.png',
            'bg_color': (255, 150, 150, 255),
            'description': '提醒状态'
        },
        {
            'text': '😴',
            'filename': f'{output_dir}/sleep.png',
            'bg_color': (200, 200, 255, 255),
            'description': '睡觉状态'
        }
    ]
    
    # 创建图片
    for pet in pets:
        try:
            create_placeholder_pet(
                text=pet['text'],
                filename=pet['filename'],
                bg_color=pet['bg_color']
            )
            print(f"  {pet['description']}: {pet['filename']}")
        except Exception as e:
            print(f"[ERROR] 创建失败 {pet['filename']}: {e}")
    
    # 创建托盘图标
    try:
        tray_icon_path = "assets/icons/tray_icon.png"
        os.makedirs("assets/icons", exist_ok=True)
        create_placeholder_pet(
            text='🐱',
            filename=tray_icon_path,
            size=64,
            bg_color=(100, 150, 255, 255)
        )
        print(f"[OK] 创建托盘图标: {tray_icon_path}")
    except Exception as e:
        print(f"[ERROR] 创建托盘图标失败: {e}")
    
    print("\n" + "=" * 60)
    print("图片生成完成！")
    print("=" * 60)
    print("\n提示: 如果表情符号显示不正常，可以使用简单文字代替")
    print("例如: '待机'、'行走'、'开心' 等")


if __name__ == "__main__":
    main()

