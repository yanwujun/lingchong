@echo off
chcp 65001 >nul
echo ========================================
echo 桌面灵宠 - 自动打包脚本
echo Desktop Pet - Build Script
echo ========================================
echo.

REM 运行 Python 打包脚本
python build.py

echo.
pause

