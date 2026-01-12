#!/bin/bash
# Setup script for Video Content Repurposing Agency

echo "🚀 Setting up Video Content Repurposing Agency..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🎯 To run the application:"
echo "   python run_app.py"
echo ""
echo "🌐 Or directly with Streamlit:"
echo "   streamlit run frontend/app.py"
