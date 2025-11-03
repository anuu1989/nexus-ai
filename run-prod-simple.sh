#!/bin/bash

# Simple Production Script for NexusAI
# Quick deployment without all the bells and whistles

echo "🚀 NexusAI - Simple Production Mode"
echo "==================================="

# Check basic requirements
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "💡 Copy .env.example to .env and configure your API keys"
    exit 1
fi

# Set production environment
export FLASK_ENV=production
export FLASK_DEBUG=False
export PYTHONPATH="${PWD}/backend:${PYTHONPATH}"

# Create logs directory
mkdir -p logs

# Install production dependencies if needed
if ! command -v gunicorn &> /dev/null; then
    echo "📦 Installing gunicorn..."
    pip install gunicorn gevent
fi

echo "🔧 Production Configuration:"
echo "  • Environment: Production"
echo "  • Debug: Disabled"
echo "  • Workers: 4"
echo "  • Port: 5000"
echo "  • Logs: logs/"
echo ""

echo "🚀 Starting NexusAI in production mode..."
echo "🌐 Server will be available at: http://localhost:5000"
echo "📊 Logs: tail -f logs/access.log logs/error.log"
echo "🛑 Stop: Press Ctrl+C"
echo ""

# Start the production server
cd backend && gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --worker-class gevent \
    --worker-connections 1000 \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --log-level info \
    --access-logfile ../logs/access.log \
    --error-logfile ../logs/error.log \
    --capture-output \
    wsgi:app