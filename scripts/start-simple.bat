@echo off
echo Starting Enterprise RAG Bot (Simple Setup)...

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

echo Installing minimal dependencies...
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv requests beautifulsoup4 chromadb

echo Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "backups" mkdir backups
if not exist "chroma_db" mkdir chroma_db

echo Creating .env file if it doesn't exist...
if not exist ".env" (
    echo # Minimal configuration > .env
    echo OPENROUTER_API_KEY= >> .env
    echo VOYAGE_API_KEY= >> .env
    echo OLLAMA_BASE_URL=http://localhost:11434 >> .env
    echo DATABASE_URL=sqlite:///./ragbot.db >> .env
    echo CHROMA_PERSIST_DIRECTORY=./chroma_db >> .env
)

echo.
echo ========================================
echo Enterprise RAG Bot - Simple Setup
echo ========================================
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo ========================================
echo.
echo Starting FastAPI backend...
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
