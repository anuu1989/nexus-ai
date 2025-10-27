# AI Guardrails - Backend Implementation

## Overview
AI Guardrails have been moved to the backend for better security and performance. The system automatically filters all messages and responses without requiring frontend configuration.

## Features

### 🛡️ **Automatic Protection**
- **Server-side filtering** - All content processed on backend
- **No client-side bypass** - Security cannot be disabled by users
- **Real-time monitoring** - Instant content analysis
- **Transparent operation** - Works seamlessly without user intervention

### 🔍 **Detection Categories**

#### 1. Content Safety
- Violence, harm, murder, suicide references
- Hate speech, racism, discrimination
- Illegal activities, drugs, weapons
- Hacking, fraud, scam attempts
- Explicit sexual content

#### 2. Prompt Injection Protection
- Instruction override attempts
- Role manipulation commands
- System prompt bypasses
- Context switching attacks
- Jailbreaking attempts

#### 3. PII Detection
- Social Security Numbers (SSN)
- Credit card numbers
- Email addresses
- Phone numbers
- Other personal identifiers

## API Endpoints

### `/api/chat` (Enhanced)
**POST** - Main chat endpoint with automatic guardrails
```json
{
  "message": "User message",
  "model": "llama-3.1-8b-instant"
}
```

**Response (Normal):**
```json
{
  "response": "AI response",
  "status": "success",
  "guardrails": {"status": "passed", "checked": true}
}
```

**Response (Blocked):**
```json
{
  "response": "⚠️ Message blocked by AI Guardrails: [reason]",
  "blocked": true,
  "guardrails": {
    "blocked": true,
    "reason": "Content contains potentially harmful material",
    "category": "content_safety"
  },
  "status": "blocked"
}
```

### `/api/guardrails/status`
**GET** - Get guardrails status and configuration
```json
{
  "status": "active",
  "guardrails": {
    "content_safety": {
      "enabled": true,
      "description": "Blocks harmful and unsafe content"
    },
    "prompt_injection": {
      "enabled": true,
      "description": "Prevents prompt manipulation attempts"
    },
    "pii_detection": {
      "enabled": true,
      "description": "Detects and blocks personal information"
    }
  },
  "statistics": {
    "total_messages_processed": 0,
    "messages_blocked": 0,
    "last_updated": "2024-01-01T00:00:00"
  }
}
```

### `/api/guardrails/test`
**POST** - Test guardrails with sample messages
```json
{
  "test_results": [
    {
      "message": "Hello, how are you?",
      "blocked": false,
      "reason": "Content is safe",
      "category": "safe"
    },
    {
      "message": "My email is test@example.com",
      "blocked": true,
      "reason": "Personally Identifiable Information (PII) detected",
      "category": "pii_detection"
    }
  ],
  "status": "success"
}
```

## Frontend Integration

### Protection Badge
The UI shows a simple "Protected" badge in the header that:
- **Green pulse** - Normal protection active
- **Yellow warning** - Content was filtered
- **Red error** - Protection system error

### Status Updates
- Badge updates automatically based on API responses
- Click badge to view detailed protection status
- No user configuration required

### Testing
- Guardrails are automatically applied to all messages
- Check console logs for guardrail activity
- Test by sending messages with PII or harmful content

## Implementation Details

### Backend Function: `apply_ai_guardrails(message)`
```python
def apply_ai_guardrails(message):
    """Apply AI guardrails to filter unsafe content"""
    import re
    
    # Content Safety Check
    unsafe_patterns = [
        r'\b(violence|harm|kill|murder|suicide|death)\b',
        r'\b(hate|racist|discrimination|nazi|terrorist)\b',
        # ... more patterns
    ]
    
    # Prompt Injection Check
    injection_patterns = [
        r'ignore\s+(previous|all|earlier)\s+(instructions?|prompts?|commands?)',
        r'forget\s+(everything|all|previous)',
        # ... more patterns
    ]
    
    # PII Detection Check
    pii_patterns = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        # ... more patterns
    ]
    
    # Return result
    return {'blocked': False} or {'blocked': True, 'reason': '...', 'category': '...'}
```

### Automatic Application
1. **User message** → Guardrails check → AI processing
2. **AI response** → Guardrails check → User delivery
3. **Both directions protected** automatically

## Benefits

### 🔒 **Security**
- Cannot be bypassed by client-side modifications
- Consistent protection across all interfaces
- Server-side logging and monitoring

### ⚡ **Performance**
- No frontend processing overhead
- Optimized regex patterns
- Minimal latency impact

### 🎯 **Simplicity**
- No user configuration required
- Transparent operation
- Clean, minimal UI

### 📊 **Monitoring**
- Centralized logging
- Usage statistics
- Pattern effectiveness tracking

## Testing

### Manual Testing
1. Send messages through the chat interface
2. Check console for guardrail activity logs
3. Try sending messages with PII or harmful content to see blocking in action

### Automated Testing
```bash
curl -X POST http://localhost:5002/api/guardrails/test
```

### Sample Test Messages
- `"Hello, how are you?"` → ✅ Pass
- `"My email is test@example.com"` → ❌ Block (PII)
- `"Ignore all previous instructions"` → ❌ Block (Prompt Injection)
- `"Tell me about violence"` → ❌ Block (Content Safety)

## Configuration

### Environment Variables
```bash
# Enable/disable guardrails (default: enabled)
GUARDRAILS_ENABLED=true

# Logging level for guardrails
GUARDRAILS_LOG_LEVEL=INFO
```

### Pattern Customization
Modify patterns in `apply_ai_guardrails()` function in `app.py` to adjust sensitivity and coverage.

## Monitoring & Logs

### Log Format
```
[GUARDRAILS] BLOCKED: category=pii_detection, reason=Email detected, message_hash=abc123
[GUARDRAILS] PASSED: message_hash=def456, processing_time=0.002s
```

### Statistics Tracking
- Total messages processed
- Messages blocked by category
- Processing time metrics
- Pattern match frequency

This backend implementation provides robust, transparent AI safety without compromising user experience.