#!/bin/bash

# NexusAI Local Development Script
# Organized workspace with backend/frontend separation

echo "🚀 NexusAI - Local Development Server"
echo "======================================"

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Expected structure: backend/ and frontend/ folders"
    exit 1
fi

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
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found, installing minimal dependencies..."
    pip install Flask Werkzeug python-dotenv requests flask-cors groq
fi

# Install additional AI provider packages
echo "🤖 Installing AI provider packages..."
echo "   - Installing OpenAI package..."
pip install openai --quiet
echo "   - Installing Anthropic package..."
pip install anthropic --quiet
echo "✅ AI provider packages installed successfully!"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env template..."
    cat > .env << EOL
# AI Provider API Keys
GROQ_API_KEY=<your-groq-api-key>
OPENAI_API_KEY=<your-openai-api-key>
ANTHROPIC_API_KEY=<your-anthropic-api-key>

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
PORT=5002

# Optional: Model cache directory
TRANSFORMERS_CACHE=./backend/data/models_cache
HF_HOME=./backend/data/models_cache
EOL
    echo "✏️  Please edit .env file with your API keys:"
    echo "🔗 Groq API key: https://console.groq.com"
    echo "🔗 OpenAI API key: https://platform.openai.com/api-keys"
    echo "🔗 Anthropic API key: https://console.anthropic.com"
    echo "💡 Note: You can use any combination of providers (Groq is required)"
    exit 1
fi

# Display project structure
echo ""
echo "📁 Project Structure:"
echo "   ├── backend/          # Python Flask API"
echo "   │   ├── app.py        # Main application"
echo "   │   ├── models/       # RAG/LoRA systems"
echo "   │   └── data/         # Databases & data files"
echo "   ├── frontend/         # HTML/CSS/JS"
echo "   │   ├── index.html    # Main UI"
echo "   │   ├── static/       # CSS/JS assets"
echo "   │   └── public/       # PWA files"
echo "   └── docs/             # Documentation"
echo ""

# Start the backend server
echo "🚀 Starting NexusAI backend server..."
echo "📂 Backend directory: $(pwd)/backend"
echo "📂 Frontend directory: $(pwd)/frontend"
echo "🌐 Server will be available at: http://localhost:5002"
echo ""
echo "💡 Tips:"
echo "   - Press Ctrl+C to stop the server"
echo "   - Edit files in frontend/ for UI changes"
echo "   - Edit files in backend/ for API changes"
echo "   - Check console for debug information"
echo ""

# Change to backend directory and start the server
cd backend && python app.py