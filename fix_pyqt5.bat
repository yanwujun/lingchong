@echo off
echo ========================================
echo 修复 PyQt5 平台插件问题
echo ========================================
echo.

echo [步骤1] 卸载现有PyQt5组件...
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip -y

echo.
echo [步骤2] 清理pip缓存...
pip cache purge

echo.
echo [步骤3] 重新安装PyQt5（完整版）...
pip install PyQt5==5.15.10 PyQt5-Qt5==5.15.2 PyQt5-sip==12.13.0

echo.
echo [步骤4] 验证安装...
pip show PyQt5
pip show PyQt5-Qt5
pip show PyQt5-sip

echo.
echo [步骤5] 测试Qt平台插件...
python -c "from PyQt5.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); print('✓ Qt平台插件加载成功！')"

echo.
echo ========================================
echo 修复完成！按任意键继续...
echo ========================================
pause > nul

