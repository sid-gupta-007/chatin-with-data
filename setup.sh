#!/bin/bash
# Data Intelligence Suite - Quick Setup Script

echo "🚀 Data Intelligence Suite - Backend Setup"
echo "==========================================="

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Install Python 3.11+"
    exit 1
fi

echo "✅ Python found: $(python --version)"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate venv
echo "🔌 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the backend:"
echo "  source venv/bin/activate  (Mac/Linux)"
echo "  venv\\Scripts\\activate     (Windows)"
echo "  python main.py"
echo ""
echo "Server will run on http://localhost:8000"
