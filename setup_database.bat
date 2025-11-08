@echo off
REM National Highways Management System - Database Setup Script for Windows
REM This script sets up the complete database system

echo ========================================
echo NH Management System - Database Setup
echo ========================================
echo.

REM Configuration
set DB_HOST=localhost
set DB_USER=root
set DB_NAME=nh_management

REM Prompt for password
set /p DB_PASSWORD="Enter MySQL root password: "

echo.
echo Step 1: Creating database...
mysql -h %DB_HOST% -u %DB_USER% -p%DB_PASSWORD% -e "CREATE DATABASE IF NOT EXISTS %DB_NAME% CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

if %errorlevel% neq 0 (
    echo ERROR: Failed to create database
    pause
    exit /b 1
)

echo SUCCESS: Database created
echo.

echo Step 2: Creating schema (tables, indexes, constraints)...
mysql -h %DB_HOST% -u %DB_USER% -p%DB_PASSWORD% %DB_NAME% < database_schema.sql

if %errorlevel% neq 0 (
    echo ERROR: Failed to create schema
    pause
    exit /b 1
)

echo SUCCESS: Schema created
echo.

echo Step 3: Creating triggers...
mysql -h %DB_HOST% -u %DB_USER% -p%DB_PASSWORD% %DB_NAME% < triggers.sql

if %errorlevel% neq 0 (
    echo ERROR: Failed to create triggers
    pause
    exit /b 1
)

echo SUCCESS: Triggers created
echo.

echo Step 4: Creating views and stored procedures...
mysql -h %DB_HOST% -u %DB_USER% -p%DB_PASSWORD% %DB_NAME% < validation_queries.sql

if %errorlevel% neq 0 (
    echo ERROR: Failed to create views and procedures
    pause
    exit /b 1
)

echo SUCCESS: Views and procedures created
echo.

echo Step 5: Loading sample data...
set /p LOAD_SAMPLE="Do you want to load sample data? (y/n): "

if /i "%LOAD_SAMPLE%"=="y" (
    mysql -h %DB_HOST% -u %DB_USER% -p%DB_PASSWORD% %DB_NAME% < sample_data.sql
    
    if %errorlevel% neq 0 (
        echo WARNING: Failed to load sample data
    ) else (
        echo SUCCESS: Sample data loaded
    )
) else (
    echo Skipping sample data...
)

echo.
echo Step 6: Verifying installation...
mysql -h %DB_HOST% -u %DB_USER% -p%DB_PASSWORD% %DB_NAME% -e "SHOW TABLES;"

if %errorlevel% neq 0 (
    echo ERROR: Database verification failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo Database: %DB_NAME%
echo Host: %DB_HOST%
echo.
echo Next steps:
echo 1. Copy .env.example to .env and update configuration
echo 2. Install Python dependencies: pip install -r requirements.txt
echo 3. Run the application: python nh_management.py
echo.
echo For more information, see README.md
echo.

pause
