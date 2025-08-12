#!/bin/bash

echo "Setting up Enterprise RAG Bot..."

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads outputs backups chroma_db

# Setup Angular frontend
cd angular-frontend
npm install
cd ..

# Create environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please edit .env file with your API keys"
fi

echo "Setup complete!"
echo "To start the backend: uvicorn app.main:app --reload"
echo "To start the frontend: cd angular-frontend && ng serve"
