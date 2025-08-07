#!/bin/bash
# Quick setup script for Healthcare AI System

echo "🏥 Healthcare AI System Setup"
echo "============================"

# Check Python version
python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env from example
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

# Create uploads directory
mkdir -p uploads

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the system:"
echo "1. source venv/bin/activate"
echo "2. python intelligent_orchestrator.py"
echo "3. Open http://localhost:8000"
