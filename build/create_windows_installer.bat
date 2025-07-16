@echo off
REM Create Windows installer
REM This script should be run on Windows

set APP_NAME=DeSciOS Launcher
set EXE_NAME=descios.exe
set EXE_PATH=dist\%EXE_NAME%
set INSTALLER_NAME=descios-launcher-0.1.0-windows.exe

REM Check if exe exists
if not exist "%EXE_PATH%" (
    echo Error: %EXE_PATH% not found. Build the exe first.
    exit /b 1
)

echo Creating Windows installer for %APP_NAME%...

REM Create a simple batch installer
echo @echo off > dist\install_descios.bat
echo echo Installing %APP_NAME%... >> dist\install_descios.bat
echo copy "%EXE_NAME%" "C:\Program Files\DeSciOS\" >> dist\install_descios.bat
echo echo %APP_NAME% installed successfully! >> dist\install_descios.bat
echo pause >> dist\install_descios.bat

echo ✓ Windows installer created: dist\install_descios.bat
echo Note: For a proper installer, use tools like NSIS or Inno Setup
