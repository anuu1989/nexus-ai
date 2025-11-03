#!/bin/bash

# NexusAI Production Status Check Script
echo "📊 NexusAI - Production Status Check"
echo "===================================="

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

echo ""
print_info "🔍 Checking NexusAI production processes..."
echo ""

# Check processes
total_processes=0

# Systemd service
echo "🔧 Systemd Service:"
if systemctl is-active --quiet nexusai 2>/dev/null; then
    print_status "nexusai service is running"
    total_processes=$((total_processes + 1))
else
    print_info "nexusai service is not running"
fi

echo ""

# Gunicorn processes
echo "🐍 Gunicorn Processes:"
if pgrep -f "gunicorn.*wsgi:app" > /dev/null; then
    print_status "Gunicorn processes found"
    ps aux | grep "gunicorn.*wsgi:app" | grep -v grep
    total_processes=$((total_processes + 1))
else
    print_info "No Gunicorn processes running"
fi

echo ""

# Network check
echo "🌐 Network Status:"
if netstat -tlnp 2>/dev/null | grep ":5000 " > /dev/null || ss -tlnp 2>/dev/null | grep ":5000 " > /dev/null; then
    print_status "Port 5000 is in use"
else
    print_info "Port 5000 is not in use"
fi

echo ""

# Health check
echo "🏥 Application Health:"
if curl -f -s http://localhost:5000/ > /dev/null 2>&1; then
    print_status "Application is responding"
    print_info "🌐 Access: http://localhost:5000/"
else
    print_error "Application is not responding"
fi

echo ""

# Summary
echo "📊 Summary:"
if [ $total_processes -gt 0 ]; then
    print_status "NexusAI is running"
else
    print_info "NexusAI is not running"
    print_info "💡 Start with: ./run-prod-simple.sh"
fi

echo ""
print_info "🔧 Commands: ./run-prod-simple.sh | ./stop-production.sh | ./status-production.sh"
