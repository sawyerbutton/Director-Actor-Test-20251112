#!/bin/bash
# Script to run the Web Server for Script Analysis System

echo "============================================"
echo "剧本叙事结构分析系统 - Web 服务器"
echo "Script Analysis System - Web Server"
echo "============================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q
pip install -r requirements-web.txt -q

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one from .env.example"
    echo "   cp .env.example .env"
    echo "   and add your API keys"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting web server..."
echo "📍 Server will be available at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the web server (set PYTHONPATH to project root)
PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$(pwd)" python -m uvicorn src.web.app:app --reload --host 0.0.0.0 --port 8000
