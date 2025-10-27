#!/bin/bash

# Pre-commit hook to prevent secrets from being committed
# This hook scans staged files for API keys, passwords, and other sensitive information

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Icons
SUCCESS="✅"
ERROR="❌"
WARNING="⚠️"
INFO="ℹ️"
LOCK="🔒"
STOP="🚫"

# Check if this is a test run
if [[ "$1" == "--test" ]]; then
    echo -e "${INFO} INFO: Pre-commit hook test mode"
    exit 0
fi

echo -e "${INFO} INFO: ${LOCK} Running pre-commit security checks..."

# Get list of staged files
staged_files=$(git diff --cached --name-only --diff-filter=ACM)

if [[ -z "$staged_files" ]]; then
    echo -e "${INFO} INFO: No staged files to check"
    exit 0
fi

echo -e "${INFO} INFO: Checking staged files for secrets..."

# Function to check for secrets in a file
check_secrets() {
    local file="$1"
    local found_secrets=false
    
    # Skip binary files, images, and certain file types
    if file "$file" | grep -q "binary\|image\|executable"; then
        return 0
    fi
    
    # Skip certain file extensions
    case "$file" in
        *.png|*.jpg|*.jpeg|*.gif|*.ico|*.svg|*.pdf|*.zip|*.tar|*.gz) return 0 ;;
        *.min.js|*.min.css) return 0 ;;
        *node_modules*|*venv*|*.git*) return 0 ;;
    esac
    
    # Check for various secret patterns
    if grep -qiE "(gsk_[a-zA-Z0-9]{48,})" "$file"; then
        echo -e "${ERROR} ERROR: Found Groq API Keys in: $file"
        found_secrets=true
    fi
    
    if grep -qiE "(sk-[a-zA-Z0-9]{48,})" "$file"; then
        echo -e "${ERROR} ERROR: Found OpenAI API Keys in: $file"
        found_secrets=true
    fi
    
    if grep -qiE "(sk-ant-[a-zA-Z0-9_-]{95,})" "$file"; then
        echo -e "${ERROR} ERROR: Found Anthropic API Keys in: $file"
        found_secrets=true
    fi
    
    if grep -qiE "(AKIA[0-9A-Z]{16})" "$file"; then
        echo -e "${ERROR} ERROR: Found AWS Access Keys in: $file"
        found_secrets=true
    fi
    
    if grep -qiE "(AIza[0-9A-Za-z_-]{35})" "$file"; then
        echo -e "${ERROR} ERROR: Found Google API Keys in: $file"
        found_secrets=true
    fi
    
    if grep -qiE "(gh[pousr]_[A-Za-z0-9_]{36,255})" "$file"; then
        echo -e "${ERROR} ERROR: Found GitHub Tokens in: $file"
        found_secrets=true
    fi
    
    if grep -qiE "(xox[baprs]-[0-9a-zA-Z-]+)" "$file"; then
        echo -e "${ERROR} ERROR: Found Slack Tokens in: $file"
        found_secrets=true
    fi
    
    if grep -qiE "((api[_-]?key|apikey|secret|password|passwd|pwd|token|auth)[[:space:]]*[=:][[:space:]]*['\"]?[a-zA-Z0-9_@#\$%^&*!-]{8,}['\"]?)" "$file"; then
        echo -e "${ERROR} ERROR: Found Generic Secrets in: $file"
        # Show the actual lines with secrets (redacted)
        grep -niE "((api[_-]?key|apikey|secret|password|passwd|pwd|token|auth)[[:space:]]*[=:][[:space:]]*['\"]?[a-zA-Z0-9_@#\$%^&*!-]{8,}['\"]?)" "$file" | while read -r line; do
            line_num=$(echo "$line" | cut -d: -f1)
            redacted_line=$(echo "$line" | sed 's/[=:][[:space:]]*['\''"][a-zA-Z0-9_@#$%^&*!-]\{8,\}['\''"]*/="***REDACTED***"/g')
            echo -e "${WARNING} WARNING:   Line $line_num: $redacted_line"
        done
        found_secrets=true
    fi
    
    if grep -q -- "-----BEGIN.*PRIVATE KEY-----" "$file"; then
        echo -e "${ERROR} ERROR: Found Private Keys in: $file"
        found_secrets=true
    fi
    
    if grep -qiE "(mongodb|mysql|postgresql|redis)://[a-zA-Z0-9_:@.-]+/[a-zA-Z0-9_-]+" "$file"; then
        echo -e "${ERROR} ERROR: Found Database URLs in: $file"
        found_secrets=true
    fi
    
    if [[ "$found_secrets" == true ]]; then
        return 1
    fi
    
    return 0
}

# Check each staged file
secrets_found=false
for file in $staged_files; do
    if [[ -f "$file" ]]; then
        if ! check_secrets "$file"; then
            secrets_found=true
        fi
    fi
done

# Check .gitignore for recommended patterns
echo -e "${INFO} INFO: Checking .gitignore for secret file patterns..."
if [[ -f ".gitignore" ]]; then
    required_patterns=(".env" "*.key" "*.pem" "config.json" "secrets.json")
    missing_patterns=()
    
    for pattern in "${required_patterns[@]}"; do
        if ! grep -q "^$pattern" .gitignore; then
            missing_patterns+=("$pattern")
        fi
    done
    
    if [[ ${#missing_patterns[@]} -gt 0 ]]; then
        echo -e "${WARNING} WARNING: Consider adding these patterns to .gitignore:"
        for pattern in "${missing_patterns[@]}"; do
            echo -e "${WARNING} WARNING:   $pattern"
        done
    else
        echo -e "${SUCCESS} SUCCESS: .gitignore contains recommended secret file patterns"
    fi
else
    echo -e "${WARNING} WARNING: No .gitignore file found"
fi

# Check for hardcoded URLs and credentials
echo -e "${INFO} INFO: Checking for hardcoded URLs and credentials..."
hardcoded_found=false
for file in $staged_files; do
    if [[ -f "$file" && "$file" =~ \.(py|js|ts|java|php|rb|go|rs|cpp|c|h)$ ]]; then
        if grep -qiE "https?://[a-zA-Z0-9_-]+:[a-zA-Z0-9_@#\$%^&*!-]+@[a-zA-Z0-9.-]+/" "$file"; then
            echo -e "${WARNING} WARNING: Found URLs with credentials in: $file"
            hardcoded_found=true
        fi
        if grep -qE "localhost:[0-9]+" "$file" && ! grep -q "example\|demo\|test" "$file"; then
            echo -e "${WARNING} WARNING: Found hardcoded localhost URL in: $file"
            hardcoded_found=true
        fi
    fi
done

if [[ "$hardcoded_found" == false ]]; then
    echo -e "${SUCCESS} SUCCESS: No hardcoded values detected"
fi

# Validate .env files if present
for file in $staged_files; do
    if [[ "$file" == *.env* && -f "$file" ]]; then
        echo -e "${INFO} INFO: Validating $file format..."
        if grep -qE '^[A-Z_][A-Z0-9_]*=[^[:space:]]' "$file"; then
            echo -e "${SUCCESS} SUCCESS: $file format looks good"
        else
            echo -e "${WARNING} WARNING: $file may have formatting issues"
        fi
    fi
done

# Final result
if [[ "$secrets_found" == true ]]; then
    echo -e "${STOP} Security checks failed!"
    echo -e "${ERROR} ERROR: Commit blocked to prevent secret exposure."
    echo -e "${INFO} INFO: Fix the issues above and try again."
    echo -e "${WARNING} WARNING: Use 'git commit --no-verify' to bypass (NOT RECOMMENDED)"
    exit 1
else
    echo -e "${SUCCESS} SUCCESS: No secrets detected. Commit allowed."
    exit 0
fi