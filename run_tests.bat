@echo off
echo 🏥 Biomedical Assistant - Test Runner
echo ============================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ and add it to PATH.
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo Installing test dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies.
        pause
        exit /b 1
    )
)

REM Run tests
echo Running tests...
python run_tests.py %*

if errorlevel 1 (
    echo.
    echo ❌ Some tests failed. Please check the output above.
    pause
    exit /b 1
) else (
    echo.
    echo 🎉 All tests completed successfully!
)

pause
