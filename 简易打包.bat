@echo off
chcp 65001 >nul
echo ========================================
echo 桌面灵宠 - 简易打包
echo ========================================
echo.

echo [提示] 如果遇到 enum34 错误，请：
echo   1. 以管理员身份运行命令提示符
echo   2. 执行: pip uninstall enum34 -y
echo   3. 然后重新运行本脚本
echo.
pause

echo.
echo [1/3] 开始打包...
python -m PyInstaller --onefile --windowed --name=DesktopPet main.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    echo.
    echo 可能的解决方法：
    echo 1. 卸载 enum34: 以管理员身份运行命令提示符，执行 pip uninstall enum34 -y
    echo 2. 检查 PyInstaller 安装: pip install pyinstaller --upgrade
    echo 3. 查看上面的错误信息
    echo.
    pause
    exit /b 1
)

echo.
echo [2/3] 复制资源文件...
xcopy /E /I /Y assets dist\assets
copy config.ini dist\ >nul 2>&1
mkdir dist\data >nul 2>&1

echo.
echo [3/3] 清理临时文件...
rmdir /s /q build >nul 2>&1
del DesktopPet.spec >nul 2>&1

echo.
echo ========================================
echo [成功] 打包完成！
echo ========================================
echo.
echo 可执行文件: dist\DesktopPet.exe
echo.
echo 运行测试: cd dist ^&^& DesktopPet.exe
echo.
pause

