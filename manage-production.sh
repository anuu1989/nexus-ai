#!/bin/bash

# NexusAI Production Management Script
# One script to rule them all!

echo "🎛️  NexusAI - Production Management"
echo "=================================="

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_title() { echo -e "${PURPLE}🎯 $1${NC}"; }
print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

show_menu() {
    echo ""
    print_title "NexusAI Production Management"
    echo ""
    echo "1️⃣  🚀 Start Production (Simple)"
    echo "2️⃣  🏭 Start Production (Full Setup)"
    echo "3️⃣  🐳 Start Docker Production"
    echo "4️⃣  🛑 Stop Production"
    echo "5️⃣  📊 Check Status"
    echo "6️⃣  📋 View Logs"
    echo "7️⃣  🔄 Restart Production"
    echo "8️⃣  🧹 Clean Up"
    echo "9️⃣  ⚙️  Configuration Help"
    echo "0️⃣  ❌ Exit"
    echo ""
}

start_simple() {
    print_info "Starting NexusAI in simple production mode..."
    if [ -f "./run-prod-simple.sh" ]; then
        chmod +x ./run-prod-simple.sh
        ./run-prod-simple.sh
    else
        print_error "run-prod-simple.sh not found!"
    fi
}

start_full() {
    print_info "Starting NexusAI with full production setup..."
    if [ -f "./run-production.sh" ]; then
        chmod +x ./run-production.sh
        ./run-production.sh
    else
        print_error "run-production.sh not found!"
    fi
}

start_docker() {
    print_info "Starting NexusAI with Docker..."
    if [ -f "docker-compose.prod.yml" ]; then
        docker-compose -f docker-compose.prod.yml up -d
        print_status "Docker containers started"
    else
        print_error "docker-compose.prod.yml not found!"
    fi
}

stop_production() {
    print_info "Stopping NexusAI production..."
    if [ -f "./stop-production.sh" ]; then
        chmod +x ./stop-production.sh
        ./stop-production.sh
    else
        print_warning "stop-production.sh not found, trying manual stop..."
        pkill -f "gunicorn.*app:app"
        docker-compose -f docker-compose.yml down 2>/dev/null
        print_status "Manual stop completed"
    fi
}

check_status() {
    if [ -f "./status-production.sh" ]; then
        chmod +x ./status-production.sh
        ./status-production.sh
    else
        print_info "Quick status check..."
        if pgrep -f "gunicorn.*app:app" > /dev/null; then
            print_status "Gunicorn processes running"
        else
            print_info "No Gunicorn processes found"
        fi
        
        if curl -f -s http://localhost:5002/ > /dev/null 2>&1; then
            print_status "Application responding on http://localhost:5002/"
        else
            print_error "Application not responding"
        fi
    fi
}

view_logs() {
    print_info "Viewing recent logs..."
    if [ -d "logs" ]; then
        echo ""
        print_info "📊 Access Log (last 10 lines):"
        if [ -f "logs/access.log" ]; then
            tail -10 logs/access.log
        else
            print_warning "No access.log found"
        fi
        
        echo ""
        print_info "🚨 Error Log (last 10 lines):"
        if [ -f "logs/error.log" ]; then
            tail -10 logs/error.log
        else
            print_warning "No error.log found"
        fi
        
        echo ""
        print_info "📋 To follow logs in real-time:"
        print_info "   tail -f logs/access.log logs/error.log"
    else
        print_warning "No logs directory found"
    fi
}

restart_production() {
    print_info "Restarting NexusAI production..."
    stop_production
    sleep 2
    start_simple
}

clean_up() {
    print_info "Cleaning up NexusAI..."
    
    # Stop all processes
    stop_production
    
    # Remove PID files
    if [ -f "nexusai.pid" ]; then
        rm -f nexusai.pid
        print_status "Removed PID file"
    fi
    
    # Clean old logs (optional)
    read -p "🗑️  Remove old log files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -d "logs" ]; then
            find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null
            print_status "Cleaned old log files"
        fi
    fi
    
    print_status "Cleanup completed"
}

show_config_help() {
    print_title "Configuration Help"
    echo ""
    print_info "📁 Required Files:"
    echo "   • .env - Environment configuration"
    echo "   • backend/app.py - Main application"
    echo "   • requirements.txt - Dependencies"
    echo ""
    print_info "🔧 Environment Setup:"
    echo "   1. Copy .env.production to .env"
    echo "   2. Set GROQ_API_KEY in .env"
    echo "   3. Set SECRET_KEY in .env"
    echo ""
    print_info "🚀 Quick Start:"
    echo "   cp .env.production .env"
    echo "   # Edit .env with your values"
    echo "   ./manage-production.sh"
    echo ""
    print_info "📚 Documentation:"
    echo "   • README.md - Project overview"
    echo "   • PRODUCTION_DEPLOYMENT.md - Detailed guide"
}

# Main loop
while true; do
    show_menu
    read -p "🤔 Choose an option (0-9): " choice
    
    case $choice in
        1)
            start_simple
            ;;
        2)
            start_full
            ;;
        3)
            start_docker
            ;;
        4)
            stop_production
            ;;
        5)
            check_status
            ;;
        6)
            view_logs
            ;;
        7)
            restart_production
            ;;
        8)
            clean_up
            ;;
        9)
            show_config_help
            ;;
        0)
            print_info "👋 Goodbye! Thanks for using NexusAI!"
            exit 0
            ;;
        *)
            print_warning "Invalid option. Please choose 0-9."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..." -r
done