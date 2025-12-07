@echo off
REM Change to the script's directory (fixes Administrator mode issue)
cd /d "%~dp0"

echo ========================================
echo Socify Windows Event Log Collector
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Checking Python dependencies...
pip show pywin32 >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [2/3] Checking if running as Administrator...
net session >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Not running as Administrator!
    echo Security logs will not be accessible without admin privileges.
    echo Please right-click this script and select "Run as Administrator"
    echo.
    echo Press any key to continue anyway, or Ctrl+C to exit...
    pause >nul
)

echo [3/3] Starting Windows Event Log Collector...
echo.
echo Backend URL: http://localhost:8000/api/ingest
echo Monitoring: Application, System, Security logs
echo.
echo Press Ctrl+C to stop the collector
echo ========================================
echo.

python windows_event_collector.py --config config_windows.yaml

if errorlevel 1 (
    echo.
    echo ERROR: Collector failed to start
    echo Check windows_event_collector.log for details
    pause
    exit /b 1
)
