@echo off
echo Starting Enterprise RAG Bot on Windows...

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.11 and try again
    pause
    exit /b 1
)

echo Activating virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing/updating dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "backups" mkdir backups
if not exist "chroma_db" mkdir chroma_db

echo Creating .env file if it doesn't exist...
if not exist ".env" (
    copy ".env.example" ".env"
    echo Please edit .env file with your API keys
)

echo Starting FastAPI backend...
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
