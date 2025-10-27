#!/bin/bash

# Modern AI Assistant Startup Script

echo "🤖 Starting Modern AI Assistant..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env template..."
    cat > .env << EOL
# Groq API Configuration
GROQ_API_KEY=<your-groq-api-key>

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
PORT=5001
EOL
    echo "✏️  Please edit .env file with your Groq API key"
    echo "🔗 Get your API key at: https://console.groq.com"
    exit 1
fi

# Start the application
echo "🚀 Starting application on port 5001..."
echo "🌐 Open http://localhost:5001 in your browser"
cd backend && python app.py