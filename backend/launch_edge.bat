@echo off
REM Khởi động backend FastAPI
start cmd /k "cd /d %~dp0 && cd backend && uvicorn main:app --reload"
REM Đợi backend khởi động (có thể chỉnh lại thời gian nếu cần)
timeout /t 3
REM Mở frontend trên Microsoft Edge
start msedge "file:///%~dp0frontend/index.html" 