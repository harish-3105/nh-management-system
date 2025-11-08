@echo off
echo ========================================
echo NH Management System - Production Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if MySQL is running
echo Checking MySQL connection...
python -c "import mysql.connector; mysql.connector.connect(host='localhost', user='root', password='WJ28@krhps', database='nh_management')" >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Cannot connect to MySQL database
    echo Please ensure MySQL is running and credentials are correct
    pause
    exit /b 1
)

echo.
echo Starting production server...
echo.
echo Server will be available at:
echo   Local:    http://localhost:5000
echo   Network:  Check terminal output for network address
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python server.py

pause
