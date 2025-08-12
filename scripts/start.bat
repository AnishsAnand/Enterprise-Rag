@echo off
echo 🚀 Starting Enterprise RAG Bot...
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11+
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18+
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Install Node.js dependencies
echo 📦 Installing Node.js dependencies...
cd angular-frontend
call npm install
cd ..

REM Create necessary directories
echo 📁 Creating directories...
if not exist "chroma_db" mkdir chroma_db
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs

REM Start backend
echo 🚀 Starting FastAPI backend...
start "Backend" python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

REM Wait for backend to start
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend
echo 🚀 Starting Angular frontend...
cd angular-frontend
start "Frontend" npm start

echo.
echo ✅ Enterprise RAG Bot is starting!
echo ==================================
echo 🌐 Frontend: http://localhost:4200
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 🤖 RAG Widget: Available on frontend
echo.
echo Press any key to exit...
pause >nul
