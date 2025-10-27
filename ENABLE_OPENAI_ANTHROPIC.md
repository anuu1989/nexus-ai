# 🚀 Enable OpenAI & Anthropic Real-Time Model Fetching

## ✅ **Current Status**

- **Groq**: ✅ Active (19 models detected)
- **Ollama**: ✅ Active (2 models detected)
- **OpenAI**: 🔑 Ready (needs API key)
- **Anthropic**: 🔑 Ready (needs API key)

## 🔧 **How to Enable OpenAI**

### 1. Get OpenAI API Key

```bash
# Visit: https://platform.openai.com/api-keys
# Create new API key
```

### 2. Set Environment Variable

```bash
# Add to your .env file
echo "OPENAI_API_KEY=sk-your-openai-api-key-here" >> backend/.env

# Or export directly
export OPENAI_API_KEY="sk-your-openai-api-key-here"
```

### 3. Install OpenAI Library

```bash
pip install openai
```

### 4. Restart Backend

```bash
cd backend && python app.py
```

### 5. Test Real-Time Fetching

```bash
curl -s -X POST http://localhost:5000/api/models/refresh | jq '.total_count'
# Should show increased model count with OpenAI models
```

---

## 🧠 **How to Enable Anthropic**

### 1. Get Anthropic API Key

```bash
# Visit: https://console.anthropic.com/
# Create new API key
```

### 2. Set Environment Variable

```bash
# Add to your .env file
echo "ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here" >> backend/.env

# Or export directly
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
```

### 3. Install Anthropic Library

```bash
pip install anthropic
```

### 4. Restart Backend

```bash
cd backend && python app.py
```

### 5. Test Real-Time Fetching

```bash
curl -s -X POST http://localhost:5000/api/models/refresh | jq '.total_count'
# Should show increased model count with Claude models
```

---

## 🎯 **Expected Results**

### **With All Providers Enabled:**

```json
{
  "total_count": 25,
  "providers": {
    "groq": { "enabled": true, "name": "Groq" },
    "ollama": { "enabled": true, "name": "Ollama" },
    "openai": { "enabled": true, "name": "OpenAI" },
    "anthropic": { "enabled": true, "name": "Anthropic" }
  }
}
```

### **Model Distribution:**

- **Groq**: 19 models (Llama, Mixtral, Whisper, etc.)
- **Ollama**: 2+ models (Local models you've pulled)
- **OpenAI**: 3+ models (GPT-4o, GPT-4 Turbo, etc.)
- **Anthropic**: 3 models (Claude 3.5 Sonnet, Haiku, Opus)

---

## 🔄 **Real-Time API Calls**

### **OpenAI Real-Time Fetching:**

```python
def _get_openai_models(self):
    client = self.clients["openai"]
    models_response = client.models.list()  # Live API call

    # Filters for chat models only
    chat_models = [m for m in models_response.data if 'gpt' in m.id.lower()]
    return enhanced_model_info
```

### **Anthropic Real-Time Fetching:**

```python
def _get_anthropic_models(self):
    # Uses known available models + client verification
    # Anthropic doesn't have public models endpoint
    return claude_models_if_client_works
```

---

## 🧪 **Testing Commands**

### **Test Current Setup:**

```bash
# Check current providers
curl -s http://localhost:5000/api/providers | jq '.providers'

# Check current models
curl -s http://localhost:5000/api/models | jq '.total_count'

# Force refresh from all APIs
curl -s -X POST http://localhost:5000/api/models/refresh
```

### **Test with API Keys:**

```bash
# Set keys temporarily for testing
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Restart backend
cd backend && python app.py

# Test refresh
curl -s -X POST http://localhost:5000/api/models/refresh | jq '{
  total: .total_count,
  by_provider: (.models | group_by(.provider) | map({
    provider: .[0].provider,
    count: length
  }))
}'
```

---

## 🎨 **Frontend Integration**

### **Automatic Detection:**

- Models appear in selection modal immediately
- Provider status updates in real-time
- Cost-based sorting (free local → paid cloud)
- Capability-based filtering (vision, reasoning, etc.)

### **User Experience:**

1. **Click 🤖 AI Models** → Fresh models from all APIs
2. **See all providers** → Groq, Ollama, OpenAI, Claude
3. **Select any model** → Seamless switching
4. **Real-time updates** → New models appear instantly

---

## 🔮 **Advanced Features Ready**

### **Cost Optimization:**

- Automatic selection of cheapest model for task
- Usage tracking per provider
- Budget alerts and limits

### **Performance Monitoring:**

- Response time tracking per provider
- Error rate monitoring
- Automatic failover to backup providers

### **Smart Routing:**

- Vision tasks → GPT-4o or Claude 3.5 Sonnet
- Code tasks → GPT-4 Turbo or Llama 70B
- Fast chat → Groq Llama 8B or GPT-4o Mini
- Local privacy → Ollama models

**Your NexusAI is ready for enterprise-grade multi-provider AI! 🚀**
