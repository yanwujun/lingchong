#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
桌面灵宠 - 自动打包脚本
Automatic Build Script for Desktop Pet
"""

import os
import shutil
import subprocess
import sys

def print_step(step, total, message):
    """打印步骤信息"""
    print(f"\n[{step}/{total}] {message}")

def clean_build():
    """清理旧的打包文件"""
    print_step(1, 5, "清理旧的打包文件...")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['桌面灵宠.spec', 'DesktopPet.spec']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"  [OK] 已删除: {dir_name}")
            except Exception as e:
                print(f"  [WARN] 无法删除 {dir_name}: {e}")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"  [OK] 已删除: {file_name}")
            except Exception as e:
                print(f"  [WARN] 无法删除 {file_name}: {e}")

def check_pyinstaller():
    """检查并安装 PyInstaller"""
    print_step(2, 5, "检查 PyInstaller...")
    
    try:
        import PyInstaller
        print("  [OK] PyInstaller 已安装")
        return True
    except ImportError:
        print("  [INFO] PyInstaller 未安装，正在安装...")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
                check=True
            )
            print("  [OK] PyInstaller 安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] PyInstaller 安装失败: {e}")
            return False

def build_exe():
    """打包成 exe"""
    print_step(3, 5, "开始打包...")
    
    # 检查图标文件
    icon_path = 'assets/icons/tray_icon.png'
    icon_arg = []
    
    if os.path.exists(icon_path):
        print(f"  [INFO] 使用图标: {icon_path}")
        # 注意：PyInstaller 需要 .ico 文件，如果只有 .png，会使用默认图标
        # icon_arg = ['--icon', icon_path]
    else:
        print("  [WARN] 未找到图标文件，使用默认图标")
    
    # 使用 python -m PyInstaller 来调用，避免 PATH 问题
    cmd = [
        sys.executable,        # Python 解释器路径
        '-m',                  # 作为模块运行
        'PyInstaller',         # PyInstaller 模块
        '--onefile',           # 打包成单个文件
        '--windowed',          # 不显示控制台窗口
        '--name=DesktopPet',   # 使用英文名避免路径问题
        'main.py'
    ] + icon_arg
    
    print(f"  [INFO] 执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  [OK] 打包成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] 打包失败！")
        if e.stderr:
            print(f"  错误信息: {e.stderr}")
        if e.stdout:
            print(f"  输出信息: {e.stdout}")
        return False
    except FileNotFoundError as e:
        print(f"  [ERROR] 找不到文件: {e}")
        print(f"  [INFO] 请确保 PyInstaller 已正确安装")
        return False

def copy_resources():
    """复制资源文件"""
    print_step(4, 5, "复制资源文件...")
    
    if not os.path.exists('dist'):
        print("  [ERROR] dist 目录不存在，打包可能失败")
        return False
    
    # 复制 assets 文件夹
    if os.path.exists('assets'):
        try:
            dest = 'dist/assets'
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree('assets', dest)
            print("  [OK] 已复制: assets/")
        except Exception as e:
            print(f"  [ERROR] 复制 assets 失败: {e}")
            return False
    else:
        print("  [WARN] assets 文件夹不存在")
    
    # 复制配置文件
    if os.path.exists('config.ini'):
        try:
            shutil.copy('config.ini', 'dist/')
            print("  [OK] 已复制: config.ini")
        except Exception as e:
            print(f"  [ERROR] 复制 config.ini 失败: {e}")
    else:
        print("  [WARN] config.ini 不存在")
    
    # 创建 data 目录
    try:
        os.makedirs('dist/data', exist_ok=True)
        print("  [OK] 已创建: data/")
    except Exception as e:
        print(f"  [ERROR] 创建 data 目录失败: {e}")
    
    # 复制文档
    docs = ['README.md', 'MVP使用说明.md', 'LICENSE']
    for doc in docs:
        if os.path.exists(doc):
            try:
                shutil.copy(doc, 'dist/')
                print(f"  [OK] 已复制: {doc}")
            except Exception as e:
                print(f"  [WARN] 复制 {doc} 失败: {e}")
    
    return True

def cleanup():
    """清理临时文件"""
    print_step(5, 5, "清理临时文件...")
    
    # 清理 build 目录
    if os.path.exists('build'):
        try:
            shutil.rmtree('build')
            print("  [OK] 已删除: build/")
        except Exception as e:
            print(f"  [WARN] 无法删除 build: {e}")
    
    # 清理 spec 文件
    spec_files = ['桌面灵宠.spec', 'DesktopPet.spec']
    for spec_file in spec_files:
        if os.path.exists(spec_file):
            try:
                os.remove(spec_file)
                print(f"  [OK] 已删除: {spec_file}")
            except Exception as e:
                print(f"  [WARN] 无法删除 {spec_file}: {e}")

def create_readme():
    """创建发布版本的 README"""
    readme_content = """桌面灵宠 Desktop Pet v1.0
===============================

【快速开始】
1. 双击运行 DesktopPet.exe
2. 宠物会出现在桌面上
3. 右键点击宠物查看菜单

【基本操作】
- 拖动宠物：左键拖动
- 打开菜单：右键点击宠物或托盘图标
- 添加任务：右键 → 待办事项 → 添加任务
- 调整设置：右键 → 设置

【系统要求】
- Windows 7/8/10/11
- 无需安装 Python 或其他依赖

【文件说明】
- DesktopPet.exe - 主程序
- assets/ - 资源文件（请勿删除）
- config.ini - 配置文件
- data/ - 数据存储目录

【注意事项】
- 首次运行会自动创建数据库
- 关闭窗口不会退出，程序最小化到托盘
- 要完全退出请使用右键菜单的"退出"选项

【功能特性】
✓ 可爱的桌面宠物
✓ 待办事项管理
✓ 智能提醒系统
✓ 系统托盘集成
✓ 自动保存数据

【问题反馈】
如遇到问题，请查看详细文档或反馈给开发者。

版权所有 © 2025
开源协议：MIT License
"""
    
    try:
        with open('dist/使用说明.txt', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("\n  [OK] 已创建使用说明.txt")
    except Exception as e:
        print(f"\n  [WARN] 创建使用说明失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("桌面灵宠 - 自动打包脚本")
    print("Desktop Pet - Automatic Build Script")
    print("=" * 60)
    
    try:
        # 步骤1: 清理
        clean_build()
        
        # 步骤2: 检查工具
        if not check_pyinstaller():
            print("\n[ERROR] 无法安装 PyInstaller，打包终止")
            return False
        
        # 步骤3: 打包
        if not build_exe():
            print("\n[ERROR] 打包失败，请检查错误信息")
            return False
        
        # 步骤4: 复制资源
        if not copy_resources():
            print("\n[WARN] 资源复制不完整，程序可能无法正常运行")
        
        # 步骤5: 清理
        cleanup()
        
        # 创建说明文档
        create_readme()
        
        # 成功信息
        print("\n" + "=" * 60)
        print("[SUCCESS] 打包完成！")
        print("=" * 60)
        print("\n可执行文件位置: dist/DesktopPet.exe")
        print("\ndist 目录包含：")
        print("  - DesktopPet.exe  (主程序)")
        print("  - assets/         (资源文件)")
        print("  - config.ini      (配置文件)")
        print("  - data/           (数据目录)")
        print("  - 使用说明.txt     (使用文档)")
        print("\n现在可以：")
        print("  1. 测试运行: cd dist && DesktopPet.exe")
        print("  2. 打包发布: 压缩 dist 文件夹为 zip")
        print()
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n[INFO] 用户取消打包")
        return False
    except Exception as e:
        print(f"\n[ERROR] 打包过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    # 如果是 Windows，暂停以便查看结果
    if sys.platform == 'win32' and not success:
        input("\n按回车键退出...")
    
    sys.exit(0 if success else 1)

