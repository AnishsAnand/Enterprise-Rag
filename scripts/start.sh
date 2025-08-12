#!/bin/bash

echo "🚀 Starting Enterprise RAG Bot..."
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd angular-frontend
npm install
cd ..

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p chroma_db uploads outputs

# Start backend in background
echo "🚀 Starting FastAPI backend..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Start frontend
echo "🚀 Starting Angular frontend..."
cd angular-frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Enterprise RAG Bot is starting!"
echo "=================================="
echo "🌐 Frontend: http://localhost:4200"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🤖 RAG Widget: Available on frontend"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait $FRONTEND_PID $BACKEND_PID
