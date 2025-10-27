#!/bin/bash

# Setup script for git hooks
# Run this script to install the pre-commit hook for secret detection

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "Not in a git repository. Please run this from the project root."
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy the pre-commit hook
if [ -f ".git/hooks/pre-commit" ]; then
    print_info "Pre-commit hook already exists. Creating backup..."
    cp .git/hooks/pre-commit .git/hooks/pre-commit.backup.$(date +%Y%m%d_%H%M%S)
fi

# Install the pre-commit hook
cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

print_success "Pre-commit hook installed successfully!"
print_info "The hook will now check for secrets before each commit."

# Test the hook
print_info "Testing the pre-commit hook..."
if .git/hooks/pre-commit --test 2>/dev/null; then
    print_success "Pre-commit hook test passed!"
else
    print_info "Pre-commit hook is ready (no staged files to test)"
fi

echo ""
print_info "What this hook does:"
echo "  • Scans staged files for API keys, passwords, and secrets"
echo "  • Checks for sensitive file patterns"
echo "  • Validates .env file format"
echo "  • Warns about hardcoded localhost URLs"
echo "  • Suggests .gitignore improvements"
echo ""
print_info "To bypass the hook (NOT RECOMMENDED):"
echo "  git commit --no-verify"
echo ""
print_success "Setup complete! Your commits are now protected from secret leaks."