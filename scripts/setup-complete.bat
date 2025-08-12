@echo off
echo ========================================
echo Enterprise RAG Bot - Complete Setup
echo ========================================

echo Step 1: Setting up Backend...
call scripts\start-simple.bat &

timeout /t 5 /nobreak >nul

echo Step 2: Setting up Frontend...
start cmd /k "scripts\start-frontend.bat"

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:4200
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Both services are starting...
echo The frontend will open automatically in your browser.
echo.
pause
