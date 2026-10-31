@echo off
chcp 65001 >nul
title NEU Calendar Launcher

cd /d "%~dp0"

echo ===================================================
echo     DANG KHOI DONG NEU CALENDAR (SMART PLANNER)
echo ===================================================

cd backend
set PYTHONPATH=%cd%
set DATABASE_URL=sqlite:///./neu_calendar.db
set ENVIRONMENT=development

echo 1. Dang khoi tao co so du lieu va du lieu mau...
.venv\Scripts\python -m app.seed.seed_data

echo 2. Dang bat Backend Server (FastAPI)...
start "NEU Calendar - Backend API (Port 8000)" cmd /k "set PYTHONPATH=%cd%&& set DATABASE_URL=sqlite:///./neu_calendar.db&& set ENVIRONMENT=development&& .venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

cd ..\frontend
echo 3. Dang bat Frontend Server (Web)...
start "NEU Calendar - Frontend Web (Port 8080)" cmd /k "..\backend\.venv\Scripts\python -m http.server 8080"

echo 4. Dang mo trinh duyet...
start http://localhost:8080

echo ===================================================
echo   DA KHOI DONG THANH CONG!
echo   Dia chi Web: http://localhost:8080
echo   API Docs:    http://127.0.0.1:8000/docs
echo ===================================================
pause
