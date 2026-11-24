@echo off
REM run_v7.bat: Windows double-click launcher for run_v7.ps1 (same options, e.g. run_v7.bat -SkipPit)
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_v7.ps1" %*
pause
