#!/bin/bash
# Script to install and setup Ollama for the Healthcare AI System

echo "🤖 Setting up TRUE AI for Healthcare System"
echo "=========================================="

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is already installed"
else
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Pull a medical-friendly model
echo ""
echo "📥 Downloading AI models..."
echo "This may take a few minutes..."

# Try to pull models in order of preference
if ollama pull llama2:7b-chat 2>/dev/null; then
    echo "✅ Downloaded Llama 2 (7B) - Good for medical reasoning"
elif ollama pull mistral 2>/dev/null; then
    echo "✅ Downloaded Mistral - Fast and efficient"
else
    echo "⚠️  Could not download models. You may need to run: ollama pull mistral"
fi

# Test that Ollama is working
echo ""
echo "🧪 Testing Ollama..."
if ollama list &> /dev/null; then
    echo "✅ Ollama is working!"
    echo ""
    echo "Available models:"
    ollama list
else
    echo "❌ Ollama is not running. Please start it with: ollama serve"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Make sure Ollama is running: ollama serve"
echo "2. Update your .env file with: LLM_PROVIDER=ollama"
echo "3. Run the AI-powered system!"
