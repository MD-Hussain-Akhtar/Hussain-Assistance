@echo off
REM ADA V2 - Master Startup Script for Windows
REM This starts Backend + Frontend + Electron in one go

cls
echo.
echo ========================================================================
echo         ADA V2 - COMPLETE STARTUP (Backend + Frontend + Electron)
echo ========================================================================
echo.

cd /d g:\ada_v2-main

echo Starting Backend Server...
start "ADA Backend" python backend\server.py

timeout /t 3 /nobreak

echo Starting Frontend + Electron...
start "ADA Frontend" npm run dev

echo.
echo ========================================================================
echo          ALL SERVICES STARTED!
echo ========================================================================
echo.
echo Services Running:
echo   - Backend:   http://localhost:8000
echo   - Frontend:  http://localhost:5173
echo   - Electron:  Desktop window (opening soon...)
echo.
echo Ready to accept voice commands!
echo.
pause
