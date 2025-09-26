#!/bin/bash
# Carbon Credit Platform Test Runner

echo "🧪 Carbon Credit Platform - Test Suite"
echo "======================================"

# Check if server is running
echo "🔍 Checking if server is running on port 8000..."
if curl -s http://127.0.0.1:8000/docs > /dev/null; then
    echo "✅ Server is running"
    
    # Activate virtual environment and run tests
    source .venv/bin/activate
    echo "🧪 Running API tests..."
    python test_api.py
    
    echo ""
    echo "🏆 Test completed!"
    echo "📖 Visit http://127.0.0.1:8000/docs to explore the API"
else
    echo "❌ Server is not running on port 8000"
    echo "💡 Please start the server first:"
    echo "   ./start_server.sh"
    echo ""
    echo "   OR run manually:"
    echo "   source .venv/bin/activate"
    echo "   python -m uvicorn main:app --reload --port 8000"
    exit 1
fi