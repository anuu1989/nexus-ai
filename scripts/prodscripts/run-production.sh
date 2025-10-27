#!/bin/bash

# NexusAI Production Deployment Script
# Optimized for production environments with security and performance

echo "🚀 NexusAI - Production Deployment"
echo "===================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Please run this script from the project root directory"
    print_info "Expected structure: backend/ and frontend/ folders"
    exit 1
fi

# Check for required files
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found!"
    exit 1
fi

if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_info "Please create .env file with production configuration"
    print_info "Copy from .env.example and update with production values"
    exit 1
fi

# Production environment setup
echo ""
print_info "Setting up production environment..."

# Create production virtual environment if it doesn't exist
if [ ! -d "venv-prod" ]; then
    print_info "Creating production virtual environment..."
    python3 -m venv venv-prod
fi

# Activate production virtual environment
print_info "Activating production virtual environment..."
source venv-prod/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install production dependencies
print_info "Installing production dependencies..."
echo ""
echo "📦 Installing core dependencies..."
pip install Flask>=2.3.0 Werkzeug>=2.3.0 python-dotenv>=1.0.0 requests>=2.31.0 flask-cors>=4.0.0 groq>=0.4.0

echo "🏭 Installing production server..."
pip install gunicorn>=21.2.0 gevent>=23.9.0

echo "🛡️ Installing security packages..."
pip install cryptography>=41.0.0

echo "📊 Installing monitoring..."
pip install sentry-sdk[flask]>=1.38.0

echo "🗄️ Installing database support..."
pip install SQLAlchemy>=2.0.0 Flask-SQLAlchemy>=3.1.0

echo "⚡ Installing performance packages..."
pip install Flask-Compress>=1.14

print_status "Dependencies installed successfully"

# Create production directories
print_info "Creating production directories..."
mkdir -p logs
mkdir -p backend/data/uploads
mkdir -p backend/data/backups
chmod 755 logs backend/data/uploads backend/data/backups

# Set production environment variables
print_info "Configuring production environment..."
export FLASK_ENV=production
export FLASK_DEBUG=False
export PYTHONPATH="${PWD}/backend:${PYTHONPATH}"

# Check environment configuration
print_info "Validating environment configuration..."

# Check for required environment variables
if ! grep -q "GROQ_API_KEY" .env; then
    print_error "GROQ_API_KEY not found in .env file"
    exit 1
fi

if ! grep -q "SECRET_KEY" .env; then
    print_warning "SECRET_KEY not found in .env file"
    print_info "Generating secure SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "SECRET_KEY=${SECRET_KEY}" >> .env
    print_status "SECRET_KEY generated and added to .env"
fi

# Set production defaults if not specified
if ! grep -q "PORT" .env; then
    echo "PORT=5000" >> .env
fi

if ! grep -q "WORKERS" .env; then
    echo "WORKERS=4" >> .env
fi

# Database initialization
print_info "Initializing production database..."
cd backend
python -c "
try:
    import app
    print('✅ Application imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    print_error "Application failed to import. Check dependencies and configuration."
    exit 1
fi

cd ..

# Create systemd service file (optional)
print_info "Creating systemd service configuration..."
cat > nexusai.service << EOL
[Unit]
Description=NexusAI Production Server
After=network.target

[Service]
Type=notify
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$(pwd)/backend
Environment=PATH=$(pwd)/venv-prod/bin
EnvironmentFile=$(pwd)/.env
ExecStart=$(pwd)/venv-prod/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class gevent --worker-connections 1000 --max-requests 1000 --max-requests-jitter 100 --timeout 30 --keep-alive 2 --log-level info --access-logfile ../logs/access.log --error-logfile ../logs/error.log --capture-output --enable-stdio-inheritance wsgi:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

print_status "Systemd service file created: nexusai.service"
print_info "To install: sudo cp nexusai.service /etc/systemd/system/ && sudo systemctl enable nexusai"

# Create nginx configuration (optional)
print_info "Creating nginx configuration..."
cat > nexusai-nginx.conf << EOL
server {
    listen 80;
    server_name your-domain.com;  # Change this to your domain
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Serve static files directly
    location /static/ {
        alias $(pwd)/frontend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        gzip on;
        gzip_types text/css application/javascript image/svg+xml;
    }
    
    # Proxy API requests to Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
EOL

print_status "Nginx configuration created: nexusai-nginx.conf"
print_info "To install: sudo cp nexusai-nginx.conf /etc/nginx/sites-available/nexusai"
print_info "Then: sudo ln -s /etc/nginx/sites-available/nexusai /etc/nginx/sites-enabled/"

# Production startup options
echo ""
print_info "Production deployment ready!"
echo ""
echo "🚀 Choose your deployment method:"
echo ""
echo "1️⃣  Direct Gunicorn (Recommended for testing):"
echo "   cd backend && ../venv-prod/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app"
echo ""
echo "2️⃣  Background Process:"
echo "   cd backend && nohup ../venv-prod/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --daemon --pid ../nexusai.pid wsgi:app"
echo ""
echo "3️⃣  Systemd Service (Recommended for production):"
echo "   sudo cp nexusai.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable nexusai"
echo "   sudo systemctl start nexusai"
echo ""
echo "4️⃣  Docker Production:"
echo "   docker-compose -f docker-compose.prod.yml up -d"
echo ""

# Ask user which method to use
read -p "🤔 Which deployment method would you like to use? (1-4): " choice

case $choice in
    1)
        print_info "Starting Gunicorn server..."
        print_info "Server will be available at: http://localhost:5000"
        print_info "Press Ctrl+C to stop"
        cd backend && ../venv-prod/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class gevent --access-logfile ../logs/access.log --error-logfile ../logs/error.log wsgi:app
        ;;
    2)
        print_info "Starting background process..."
        cd backend && nohup ../venv-prod/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --daemon --pid ../nexusai.pid --access-logfile ../logs/access.log --error-logfile ../logs/error.log wsgi:app
        print_status "NexusAI started in background (PID: $(cat nexusai.pid))"
        print_info "Server available at: http://localhost:5000"
        print_info "To stop: kill $(cat nexusai.pid)"
        ;;
    3)
        print_info "Setting up systemd service..."
        if [ "$EUID" -eq 0 ]; then
            cp nexusai.service /etc/systemd/system/
            systemctl daemon-reload
            systemctl enable nexusai
            systemctl start nexusai
            print_status "NexusAI service installed and started"
            print_info "Status: systemctl status nexusai"
            print_info "Logs: journalctl -u nexusai -f"
        else
            print_warning "Root privileges required for systemd service"
            print_info "Run: sudo $0 and choose option 3 again"
        fi
        ;;
    4)
        print_info "Starting Docker production deployment..."
        if command -v docker-compose &> /dev/null; then
            if [ -f "docker-compose.prod.yml" ]; then
                docker-compose -f docker-compose.prod.yml up -d --build
                print_status "Docker containers started"
                print_info "Server available at: http://localhost:5000"
            else
                docker-compose up -d --build
                print_status "Docker containers started"
                print_info "Server available at: http://localhost:5000"
            fi
        else
            print_error "Docker Compose not found. Please install Docker and Docker Compose."
        fi
        ;;
    *)
        print_info "No deployment method selected. You can run the commands manually."
        ;;
esac

echo ""
print_status "Production deployment script completed!"
echo ""
print_info "📊 Monitoring:"
print_info "  • Logs: tail -f logs/access.log logs/error.log"
print_info "  • Process: ps aux | grep gunicorn"
print_info "  • Health: curl http://localhost:5000/"
echo ""
print_info "🛡️ Security:"
print_info "  • Configure firewall to allow only necessary ports"
print_info "  • Set up SSL/TLS certificates"
print_info "  • Regular security updates"
echo ""
print_info "📈 Performance:"
print_info "  • Monitor resource usage"
print_info "  • Adjust worker count based on CPU cores"
print_info "  • Use nginx for static file serving"
echo ""
print_status "🎉 NexusAI is ready for production!"