#!/bin/bash
# Carbon Credit Platform Startup Script

echo "🌳 Starting Carbon Credit Platform - Offset"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python -m venv .venv"
    echo "   source .venv/bin/activate" 
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python -c "import fastapi, sqlalchemy, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

echo "🚀 Starting FastAPI server..."
echo "📖 API Documentation will be available at: http://127.0.0.1:8000/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the server
python -m uvicorn main:app --reload --port 8000