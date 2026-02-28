@echo off
echo ============================================
echo Loading Sample Data into HRMS Lite Database
echo ============================================
echo.
echo Database: hrms_lite
echo Host: 127.0.0.1:3306
echo User: root
echo.
echo This will insert:
echo - 50 Employees
echo - 1,400 Attendance Records
echo.
pause

mysql -h 127.0.0.1 -P 3306 -u root -p12345678 hrms_lite < sample_data.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo SUCCESS! Sample data loaded successfully.
    echo ============================================
    echo.
    echo You can now:
    echo 1. Start the backend: uvicorn main:app --reload
    echo 2. Start the frontend: npm run dev
    echo 3. View the data in the application
    echo.
) else (
    echo.
    echo ============================================
    echo ERROR! Failed to load sample data.
    echo ============================================
    echo.
    echo Please check:
    echo 1. MySQL is running
    echo 2. Database 'hrms_lite' exists
    echo 3. Credentials are correct
    echo.
)

pause
