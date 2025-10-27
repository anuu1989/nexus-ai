# 🔒 Security Guidelines

## Pre-Commit Hook Setup

This project includes a comprehensive pre-commit hook to prevent secrets from being accidentally committed to the repository.

### 🚀 Quick Setup

```bash
# Install the pre-commit hook
./scripts/setup-git-hooks.sh
```

### 🔍 What the Hook Checks

#### **🔑 Secret Detection:**
- **API Keys**: Groq, OpenAI, Anthropic, Google, AWS
- **Tokens**: GitHub, JWT, Slack, Discord, Stripe, PayPal
- **Credentials**: Passwords, database URLs, email credentials
- **Private Keys**: SSH keys, SSL certificates, PGP keys
- **Sensitive Files**: .env, config.json, credentials.json

#### **📋 File Validation:**
- **Format Checking**: .env file format validation
- **JSON Validation**: Syntax checking for JSON files
- **Hardcoded URLs**: Detection of localhost and IP addresses
- **Security TODOs**: Flags security-related TODO/FIXME comments

#### **🛡️ Protection Levels:**
- **Critical**: Blocks commit immediately (API keys, passwords)
- **Warning**: Shows warnings but allows commit (localhost URLs)
- **Info**: Provides suggestions (.gitignore improvements)

### 🔧 Manual Hook Installation

If the setup script doesn't work, install manually:

```bash
# Copy the hook
cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Test the hook
.git/hooks/pre-commit --test
```

### 🚫 Bypassing the Hook

**⚠️ NOT RECOMMENDED** - Only use in emergencies:

```bash
git commit --no-verify
```

### 📝 Best Practices

#### **Environment Variables:**
```bash
# ✅ Good - Use .env file
GROQ_API_KEY=<your-api-key>
SECRET_KEY=<your-secret>

# ❌ Bad - Hardcoded in code
api_key = "gsk_" + "NEVER_HARDCODE_KEYS"
```

#### **Code Examples:**
```python
# ✅ Good - Environment variables
import os
api_key = os.environ.get('GROQ_API_KEY')

# ❌ Bad - Hardcoded secrets
api_key = "gsk_" + "EXAMPLE_NEVER_USE_THIS"
```

```javascript
// ✅ Good - Environment variables (server-side)
const apiKey = process.env.GROQ_API_KEY;

// ❌ Bad - Hardcoded secrets
const apiKey = "gsk_" + "NEVER_HARDCODE_IN_JS";
```

### 🔍 Secret Patterns Detected

| Type | Pattern | Example |
|------|---------|---------|
| Groq API Keys | `gsk_[a-zA-Z0-9]{48,}` | `gsk_1234...` |
| OpenAI API Keys | `sk-[a-zA-Z0-9]{48,}` | `sk-1234...` |
| AWS Access Keys | `AKIA[0-9A-Z]{16}` | `AKIA1234...` |
| GitHub Tokens | `gh[pousr]_[A-Za-z0-9_]{36,255}` | `ghp_1234...` |
| JWT Tokens | `eyJ[a-zA-Z0-9_-]*\..*` | `eyJ1234...` |
| Private Keys | SSH/SSL key patterns | Private key files |

### 🛠️ Troubleshooting

#### **False Positives:**
If the hook incorrectly flags legitimate content:

1. **Check the pattern**: Is it actually a secret?
2. **Add to exclusions**: Modify the hook to exclude specific patterns
3. **Use placeholders**: Replace with `YOUR_API_KEY_HERE` in examples

#### **Hook Not Running:**
```bash
# Check if hook is executable
ls -la .git/hooks/pre-commit

# Make executable if needed
chmod +x .git/hooks/pre-commit

# Test manually
.git/hooks/pre-commit
```

#### **Git Hooks Disabled:**
```bash
# Check git config
git config --get core.hooksPath

# Enable hooks (if disabled)
git config --unset core.hooksPath
```

### 📚 Additional Security Measures

#### **Environment File Security:**
```bash
# Set proper permissions on .env files
chmod 600 .env

# Never commit .env files
echo ".env" >> .gitignore
```

#### **Production Security:**
- Use environment variables for all secrets
- Enable HTTPS in production
- Implement rate limiting
- Use secure session cookies
- Validate all user inputs
- Keep dependencies updated

#### **Development Security:**
- Use different API keys for development/production
- Rotate API keys regularly
- Monitor API usage for anomalies
- Use least-privilege access principles

### 🚨 Incident Response

If secrets are accidentally committed:

1. **Immediate Actions:**
   ```bash
   # Remove from history (if recent)
   git reset --soft HEAD~1
   git reset HEAD .
   
   # Or rewrite history (dangerous)
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch path/to/secret/file' \
   --prune-empty --tag-name-filter cat -- --all
   ```

2. **Rotate Compromised Secrets:**
   - Generate new API keys immediately
   - Update all environments with new keys
   - Revoke old keys from provider dashboards

3. **Verify Clean History:**
   ```bash
   # Check git history for secrets
   git log --all --full-history -- path/to/secret/file
   ```

### 📞 Security Contact

For security-related issues:
- Create a private GitHub issue
- Email: security@yourproject.com
- Follow responsible disclosure practices

---

**Remember**: Security is everyone's responsibility! 🛡️