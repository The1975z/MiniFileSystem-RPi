@echo off
title FILE-MANAGEMENT-SYSTEM-OS
python run_integrated.py
if errorlevel 1 (
    echo.
    echo Application exited with errors
    pause
)
