#!/bin/bash
# Quick launcher script for the Healthcare AI System

cd /Users/nandichandana/Downloads/healthcare-ai-multiagent-system

echo "🏥 Healthcare AI Multi-Agent System"
echo "=================================="
echo ""
echo "🚀 Starting the web server..."
echo "   URL: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Try to run with Python 3
if command -v python3 &> /dev/null; then
    python3 intelligent_orchestrator.py
elif command -v python &> /dev/null; then
    python intelligent_orchestrator.py
else
    echo "❌ Python not found. Please install Python 3.8+"
fi
