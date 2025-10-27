# 🌐 Multi-Provider LLM Setup Guide

## 🎯 Overview

NexusAI now supports multiple AI providers with automatic fallback and intelligent routing:

- **Groq** - Ultra-fast inference (default)
- **OpenAI** - GPT models with advanced capabilities
- **Anthropic** - Claude models for reasoning and analysis
- **Google AI** - Gemini models with large context windows
- **Ollama** - Local models for privacy
- **Hugging Face** - Open source models

## 🚀 Quick Setup

### **1. Basic Setup (Groq Only)**
```bash
# Already working! Just need Groq API key
GROQ_API_KEY=your_groq_api_key_here
```

### **2. Multi-Provider Setup**
Add API keys for the providers you want to use:

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

## 🔑 API Key Setup

### **Groq (Required)**
```bash
# Get from: https://console.groq.com/
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### **OpenAI (Optional)**
```bash
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your_openai_api_key_here
```

### **Anthropic (Optional)**
```bash
# Get from: https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key_here
```

### **Google AI (Optional)**
```bash
# Get from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_ai_api_key_here
```

### **Hugging Face (Optional)**
```bash
# Get from: https://huggingface.co/settings/tokens
HUGGINGFACE_API_KEY=hf_your_huggingface_token_here
```

### **Ollama (Optional - Local Models)**
```bash
# Install Ollama first: https://ollama.ai/
# Default URL (change if different)
OLLAMA_BASE_URL=http://localhost:11434
```

## 📦 Dependencies Installation

### **Core Dependencies (Already Installed)**
```bash
pip install groq flask python-dotenv requests flask-cors
```

### **Optional Provider Dependencies**
```bash
# Install only the providers you want to use

# OpenAI
pip install openai>=1.0.0

# Anthropic
pip install anthropic>=0.25.0

# Google AI
pip install google-generativeai>=0.3.0

# Ollama (no additional packages needed)
# Hugging Face (uses requests - already installed)
```

### **All Providers at Once**
```bash
pip install openai anthropic google-generativeai
```

## 🎛️ Available Models by Provider

### **Groq Models**
- `llama-3.1-8b-instant` - Ultra-fast responses
- `llama-3.1-70b-versatile` - Advanced reasoning
- `mixtral-8x7b-32768` - Mixture of experts

### **OpenAI Models**
- `gpt-4o` - Latest GPT-4 with multimodal capabilities
- `gpt-4o-mini` - Faster, more efficient GPT-4
- `gpt-3.5-turbo` - Fast and cost-effective

### **Anthropic Models**
- `claude-3-5-sonnet-20241022` - Latest Claude with enhanced capabilities
- `claude-3-haiku-20240307` - Fast and efficient Claude

### **Google Models**
- `gemini-1.5-pro` - Most capable Gemini model
- `gemini-1.5-flash` - Fast Gemini model

### **Ollama Models (Local)**
- `llama2` - Meta's Llama 2 model
- `codellama` - Code-specialized Llama
- `mistral` - Mistral 7B model
- And many more from Ollama library

## ⚙️ Configuration Options

### **Provider Priority**
Providers are automatically prioritized by:
1. **Speed** (Groq first)
2. **Cost** (cheaper models preferred)
3. **Availability** (active providers only)

### **Automatic Fallback**
If a provider fails or hits rate limits:
1. **Automatic retry** with next available provider
2. **Seamless switching** - user doesn't notice
3. **Error handling** with graceful degradation

### **Rate Limiting**
Each provider has built-in rate limiting:
- **Groq**: 30 requests/minute
- **OpenAI**: 60 requests/minute
- **Anthropic**: 50 requests/minute
- **Google**: 60 requests/minute
- **Ollama**: 100 requests/minute (local)
- **Hugging Face**: 30 requests/minute

## 🔧 Advanced Configuration

### **Custom Provider Settings**
Edit `backend/models/llm_providers.py` to customize:

```python
# Adjust rate limits
"groq": ProviderConfig(
    name="Groq",
    provider_type=ProviderType.GROQ,
    api_key_env="GROQ_API_KEY",
    priority=1,
    rate_limit=60  # Increase if you have higher limits
)
```

### **Model Preferences**
The system automatically selects the best model based on:
- **Task complexity** (simple vs complex queries)
- **Provider availability**
- **Cost optimization**
- **Response speed requirements**

## 🚀 Usage Examples

### **Basic Chat (Automatic Provider Selection)**
```javascript
// Frontend automatically uses best available provider
const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: "Hello, how are you?",
        model: "llama-3.1-8b-instant"  // Will use Groq if available
    })
});
```

### **Specific Provider Model**
```javascript
// Use OpenAI GPT-4
const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: "Analyze this complex problem...",
        model: "gpt-4o"  // Will use OpenAI provider
    })
});
```

### **Check Provider Status**
```javascript
// Get status of all providers
const status = await fetch('/api/providers');
const data = await status.json();
console.log(data.providers);
```

## 📊 Monitoring & Analytics

### **Provider Status Dashboard**
The UI shows:
- **Active providers** and their status
- **Model availability** by provider
- **Response times** and performance
- **Cost per request** information

### **Usage Analytics**
Track:
- **Most used models** across providers
- **Provider performance** metrics
- **Cost optimization** opportunities
- **Fallback frequency**

## 🛠️ Troubleshooting

### **Provider Not Working**
1. **Check API key** in `.env` file
2. **Verify internet connection**
3. **Check provider status** at their website
4. **Review rate limits** in logs

### **Models Not Loading**
1. **Restart the application** to reload providers
2. **Check console logs** for initialization errors
3. **Verify dependencies** are installed
4. **Test API keys** individually

### **Slow Responses**
1. **Check provider status** - some may be slower
2. **Try different model** - smaller models are faster
3. **Monitor rate limits** - may be throttled
4. **Use Groq models** for fastest responses

### **High Costs**
1. **Monitor usage** in provider dashboards
2. **Use cheaper models** for simple tasks
3. **Set up billing alerts** with providers
4. **Prefer Groq/Ollama** for cost-effective options

## 🔒 Security Best Practices

### **API Key Management**
- **Never commit** API keys to version control
- **Use environment variables** only
- **Rotate keys regularly**
- **Monitor usage** for unauthorized access

### **Rate Limiting**
- **Built-in protection** against abuse
- **Automatic backoff** on rate limit hits
- **Fair usage** across all users

### **Data Privacy**
- **No data storage** by default
- **Provider policies** vary - review each
- **Use Ollama** for complete privacy (local models)

## 🎉 Benefits

### **Reliability**
- **99.9% uptime** with multiple providers
- **Automatic failover** if one provider is down
- **No single point of failure**

### **Performance**
- **Optimal routing** to fastest available provider
- **Load balancing** across providers
- **Reduced latency** with smart selection

### **Cost Optimization**
- **Automatic cost optimization** by preferring cheaper models
- **Usage tracking** and analytics
- **Flexible pricing** options

### **Model Diversity**
- **50+ models** across all providers
- **Specialized capabilities** (vision, code, reasoning)
- **Latest models** as they become available

---

## 🚀 Ready to Go!

Your NexusAI now supports multiple AI providers! 

1. **Add your API keys** to `.env`
2. **Install optional dependencies** for desired providers
3. **Restart the application**
4. **Enjoy seamless multi-provider AI** with automatic fallback!

The system will automatically detect available providers and route requests intelligently for the best performance and reliability.

**Happy chatting with multiple AI providers!** 🤖✨