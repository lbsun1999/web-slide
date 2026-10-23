@echo off
chcp 65001 >nul
setlocal
if "%~1"=="" (
  python "%~dp0scripts\export-pdf.py" "%~dp0template.html"
) else (
  python "%~dp0scripts\export-pdf.py" "%~1"
)
set "beike_export_status=%errorlevel%"
echo.
pause
exit /b %beike_export_status%
