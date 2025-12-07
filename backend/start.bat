@echo off
REM Socify Backend Startup Script for Local OpenSearch

echo ========================================
echo Socify SIEM Backend - Local OpenSearch
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo Please edit .env file with your OpenSearch configuration
    echo Press any key to continue...
    pause >nul
)

echo.
echo ========================================
echo Starting Socify Backend...
echo ========================================
@echo off
REM Socify Backend Startup Script for Local OpenSearch

echo ========================================
echo Socify SIEM Backend - Local OpenSearch
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo Please edit .env file with your OpenSearch configuration
    echo Press any key to continue...
    pause >nul
)

echo.
echo ========================================
echo Starting Socify Backend...
echo ========================================
echo OpenSearch: http://localhost:9200
echo Backend API: http://localhost:8001
echo API Docs: http://localhost:8001/api/docs
echo ========================================
echo.

REM Start the backend
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
