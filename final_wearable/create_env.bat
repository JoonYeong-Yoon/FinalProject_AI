@echo off
echo =============================================
echo Creating Python 3.10 Virtual Environment
echo =============================================

REM Ensure python3.10 exists
where python3.10 >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: python3.10 not found in PATH.
    echo Please install Python 3.10 from https://www.python.org/downloads/
    pause
    exit /b
)

python3.10 -m venv venv
call venv\Scripts\activate

echo.
echo =============================================
echo Installing Dependencies
echo =============================================
pip install --upgrade pip
pip install fastapi uvicorn python-multipart pydantic python-dotenv openai chromadb

echo.
echo =============================================
echo All Done!
echo Activate with: venv\Scripts\activate
echo =============================================
pause
