@echo off
chcp 65001 >nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install-skill.ps1"
set "lntu_install_status=%errorlevel%"
echo.
pause
exit /b %lntu_install_status%
