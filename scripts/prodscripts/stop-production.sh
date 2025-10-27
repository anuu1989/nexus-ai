#!/bin/bash

# NexusAI Production Server Stop Script
# Gracefully stops all production processes

echo "🛑 NexusAI - Production Server Stop"
echo "==================================="

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

# Function to stop processes by name
stop_process() {
    local process_name=$1
    local pids=$(pgrep -f "$process_name")
    
    if [ -n "$pids" ]; then
        print_info "Stopping $process_name processes: $pids"
        echo $pids | xargs kill -TERM
        sleep 2
        
        # Check if processes are still running
        local remaining_pids=$(pgrep -f "$process_name")
        if [ -n "$remaining_pids" ]; then
            print_warning "Force killing remaining $process_name processes: $remaining_pids"
            echo $remaining_pids | xargs kill -KILL
        fi
        
        print_status "$process_name processes stopped"
    else
        print_info "No $process_name processes found"
    fi
}

# Function to stop systemd service
stop_systemd_service() {
    if systemctl is-active --quiet nexusai; then
        print_info "Stopping systemd service: nexusai"
        if [ "$EUID" -eq 0 ]; then
            systemctl stop nexusai
            print_status "Systemd service stopped"
        else
            print_warning "Root privileges required to stop systemd service"
            print_info "Run: sudo systemctl stop nexusai"
        fi
    else
        print_info "Systemd service not running"
    fi
}

# Function to stop Docker containers
stop_docker() {
    if command -v docker-compose &> /dev/null; then
        # Check if production containers are running
        if docker-compose -f docker-compose.prod.yml ps -q | grep -q .; then
            print_info "Stopping Docker production containers..."
            docker-compose -f docker-compose.prod.yml down
            print_status "Docker containers stopped"
        elif docker-compose ps -q | grep -q .; then
            print_info "Stopping Docker development containers..."
            docker-compose down
            print_status "Docker containers stopped"
        else
            print_info "No Docker containers running"
        fi
    else
        print_info "Docker Compose not available"
    fi
}

# Function to stop PID file based process
stop_pid_file() {
    if [ -f "nexusai.pid" ]; then
        local pid=$(cat nexusai.pid)
        if kill -0 $pid 2>/dev/null; then
            print_info "Stopping process with PID: $pid"
            kill -TERM $pid
            sleep 2
            
            # Check if process is still running
            if kill -0 $pid 2>/dev/null; then
                print_warning "Force killing process: $pid"
                kill -KILL $pid
            fi
            
            rm -f nexusai.pid
            print_status "PID file process stopped"
        else
            print_warning "Process in PID file not running, removing stale PID file"
            rm -f nexusai.pid
        fi
    else
        print_info "No PID file found"
    fi
}

# Main stop logic
echo "🔍 Detecting running NexusAI processes..."
echo ""

# Check what's running
running_processes=0

# Check for Gunicorn processes
if pgrep -f "gunicorn.*wsgi:app" > /dev/null; then
    print_info "Found Gunicorn processes"
    running_processes=$((running_processes + 1))
fi

# Check for systemd service
if systemctl is-active --quiet nexusai 2>/dev/null; then
    print_info "Found systemd service"
    running_processes=$((running_processes + 1))
fi

# Check for Docker containers
if command -v docker-compose &> /dev/null; then
    if docker-compose -f docker-compose.prod.yml ps -q 2>/dev/null | grep -q . || docker-compose ps -q 2>/dev/null | grep -q .; then
        print_info "Found Docker containers"
        running_processes=$((running_processes + 1))
    fi
fi

# Check for PID file
if [ -f "nexusai.pid" ]; then
    print_info "Found PID file"
    running_processes=$((running_processes + 1))
fi

if [ $running_processes -eq 0 ]; then
    print_warning "No NexusAI processes found running"
    echo ""
    print_info "💡 If you believe processes are still running, try:"
    print_info "   ps aux | grep -E 'gunicorn|nexusai|python.*app.py'"
    exit 0
fi

echo ""
print_info "🛑 Stopping NexusAI production server..."
echo ""

# Stop in order of preference
# 1. Try systemd service first (most graceful)
stop_systemd_service

# 2. Stop Docker containers
stop_docker

# 3. Stop PID file based processes
stop_pid_file

# 4. Stop any remaining Gunicorn processes
stop_process "gunicorn.*wsgi:app"

# 5. Stop any remaining Python processes that might be NexusAI
stop_process "python.*app.py"

# 6. Clean up any remaining processes (last resort)
if pgrep -f "nexusai" > /dev/null; then
    print_warning "Found remaining nexusai processes, stopping..."
    stop_process "nexusai"
fi

echo ""
print_info "🧹 Cleaning up..."

# Remove any stale PID files
if [ -f "nexusai.pid" ]; then
    rm -f nexusai.pid
    print_status "Removed PID file"
fi

# Check for any remaining processes
remaining=$(pgrep -f "gunicorn.*wsgi:app|python.*app.py" | wc -l)
if [ $remaining -gt 0 ]; then
    print_warning "$remaining processes may still be running"
    print_info "Check with: ps aux | grep -E 'gunicorn|python.*app.py'"
else
    print_status "All NexusAI processes stopped successfully"
fi

echo ""
print_info "📊 Final status check:"
echo ""

# Status check
if systemctl is-active --quiet nexusai 2>/dev/null; then
    print_warning "Systemd service still active"
else
    print_status "Systemd service stopped"
fi

if pgrep -f "gunicorn.*wsgi:app" > /dev/null; then
    print_warning "Gunicorn processes still running"
else
    print_status "No Gunicorn processes running"
fi

if command -v docker-compose &> /dev/null; then
    if docker-compose -f docker-compose.prod.yml ps -q 2>/dev/null | grep -q . || docker-compose ps -q 2>/dev/null | grep -q .; then
        print_warning "Docker containers still running"
    else
        print_status "No Docker containers running"
    fi
fi

echo ""
print_status "🎉 NexusAI production server stop completed!"
echo ""
print_info "💡 To start again:"
print_info "   ./run-prod-simple.sh     # Simple production"
print_info "   ./run-production.sh      # Full production setup"
print_info "   docker-compose -f docker-compose.prod.yml up -d  # Docker"
echo ""
print_info "📊 To check if anything is still running:"
print_info "   ps aux | grep -E 'gunicorn|nexusai|python.*app.py'"
print_info "   docker ps"
print_info "   systemctl status nexusai"