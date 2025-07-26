@echo off
echo 🚀 SecurityAI Full Stack Startup
echo ==================================================
echo.
echo This will start:
echo - Docker services (PostgreSQL, Redis, InfluxDB, Elasticsearch)
echo - FastAPI Backend
echo - React Frontend
echo.
echo Press any key to continue...
pause >nul

python start_full_stack.py

pause 