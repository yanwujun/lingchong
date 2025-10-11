@echo off
chcp 65001 >nul
echo ========================================
echo Desktop Pet - Build with Virtual Environment
echo ========================================
echo.

REM Variables
set VENV_DIR=pack_env
set APP_NAME=DesktopPet

echo [1/8] Cleaning old files...
if exist %VENV_DIR% (
    rmdir /s /q %VENV_DIR%
)
if exist dist (
    rmdir /s /q dist
)
if exist build (
    rmdir /s /q build
)
echo   [OK] Cleaned

echo.
echo [2/8] Creating virtual environment...
python -m venv %VENV_DIR%
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment!
    pause
    exit /b 1
)
echo   [OK] Virtual environment created

echo.
echo [3/8] Activating virtual environment...
call %VENV_DIR%\Scripts\activate.bat
echo   [OK] Virtual environment activated

echo.
echo [4/8] Installing dependencies...
echo   This may take a few minutes...
pip install PyQt5 Pillow pyinstaller -q
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)
echo   [OK] Dependencies installed

echo.
echo [5/8] Building executable...
echo   This may take 5-10 minutes, please wait...
python -m PyInstaller --onefile --windowed --name=%APP_NAME% main.py
if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    deactivate
    exit /b 1
)
echo   [OK] Build successful

echo.
echo [6/8] Copying resources...
xcopy /E /I /Y assets dist\assets >nul
copy config.ini dist\ >nul
mkdir dist\data 2>nul
echo   [OK] Resources copied

echo.
echo [7/8] Cleaning up...
rmdir /s /q build 2>nul
del %APP_NAME%.spec 2>nul
echo   [OK] Cleaned

echo.
echo [8/8] Deactivating virtual environment...
deactivate
echo   [OK] Deactivated

echo.
echo ========================================
echo [SUCCESS] Build Complete!
echo ========================================
echo.
echo Executable: dist\%APP_NAME%.exe
echo.
echo Files in dist:
echo   - %APP_NAME%.exe
echo   - assets\
echo   - config.ini
echo   - data\
echo.
echo To test: cd dist ^&^& %APP_NAME%.exe
echo.
echo You can delete pack_env folder if you want.
echo.
pause

