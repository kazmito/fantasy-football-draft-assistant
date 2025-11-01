#!/bin/bash

# Fantasy Football Draft Assistant Startup Script
echo "🏈 Starting Fantasy Football Draft Assistant..."
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "draft_env" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv draft_env
    echo "✅ Virtual environment created."
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source draft_env/bin/activate

# Check if dependencies are installed
if ! python -c "import pandas, xgboost, fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed."
else
    echo "✅ Dependencies already installed."
fi

echo ""
echo "🚀 Draft Assistant is ready!"
echo ""
echo "Choose an option:"
echo "1. Run CLI Demo (python cli_demo.py)"
echo "2. Start API Server (python api_server.py)"
echo "3. Start Web Interface (python web_interface.py)"
echo "4. Run Tests (python test_draft_assistant.py)"
echo "5. Run Example (python example_usage.py)"
echo "6. Exit"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo "Starting CLI Demo..."
        python cli_demo.py
        ;;
    2)
        echo "Starting API Server..."
        echo "Server will be available at: http://localhost:8000"
        echo "API docs at: http://localhost:8000/docs"
        echo "Press Ctrl+C to stop the server"
        python api_server.py
        ;;
    3)
        echo "Starting Web Interface..."
        echo "Web interface will be available at: http://localhost:8001"
        echo "Press Ctrl+C to stop the server"
        python web_interface.py
        ;;
    4)
        echo "Running Tests..."
        python test_draft_assistant.py
        ;;
    5)
        echo "Running Example..."
        python example_usage.py
        ;;
    6)
        echo "Goodbye! Good luck with your draft! 🏈"
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
