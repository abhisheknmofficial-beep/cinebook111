@echo off
title CineBook - Starting Server...
echo.
echo  ================================================
echo    CineBook - Movie and Event Booking App
echo  ================================================
echo.
echo  Starting server... Please wait.
echo.
cd /d "C:\Users\Gayatri\.gemini\antigravity\scratch\cinebook"
echo  Server is running at: http://127.0.0.1:8000
echo  API Docs:             http://127.0.0.1:8000/docs
echo  DSA Explorer:         http://127.0.0.1:8000/dsa-explorer
echo.
echo  Opening browser...
timeout /t 2 /nobreak >nul
start http://127.0.0.1:8000
echo.
echo  [Keep this window open while using the app]
echo  [Press Ctrl+C to stop the server]
echo.
python run.py
pause
