#!/bin/bash

# Frontend Development Server
# Simple HTTP server for frontend development

echo "🎨 NexusAI - Frontend Development Server"
echo "======================================="

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend/ directory not found"
    echo "   Please run this script from the project root directory"
    exit 1
fi

echo "📂 Serving frontend files from: $(pwd)/frontend"
echo "🌐 Frontend will be available at: http://localhost:8000"
echo "⚠️  Note: This serves static files only. For full functionality, use run-local.sh"
echo ""
echo "💡 Tips:"
echo "   - This is useful for frontend-only development"
echo "   - API calls will fail without the backend server"
echo "   - Use run-local.sh for full development with backend"
echo "   - Press Ctrl+C to stop the server"
echo ""

# Start simple HTTP server in frontend directory
cd frontend && python3 -m http.server 8000