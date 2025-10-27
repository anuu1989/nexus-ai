# 🚀 NexusAI Installation Guide

## Quick Start (Minimal Installation)

For basic functionality with simplified RAG/LoRA systems:

```bash
# Install core dependencies only
pip install Flask Werkzeug python-dotenv requests flask-cors groq
```

## Full Installation (All Features)

For complete functionality with advanced ML features:

1. **Edit `requirements.txt`** - Uncomment the sections you need:
   - AI/ML Advanced Features (for full RAG/LoRA)
   - Document Processing (for file uploads)
   - Vector Databases (for advanced search)
   - LangChain Ecosystem (for advanced RAG)

2. **Install all dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Production Installation

For production deployment:

1. **Edit `requirements.txt`** - Uncomment these sections:
   - Database (for persistent storage)
   - Security & Production
   - Production Server
   - Caching & Performance
   - Monitoring & Logging

2. **Install production dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Installation Profiles

### 🏃‍♂️ **Minimal Profile** (Fastest setup)
- Core Flask app
- Basic AI chat functionality
- Simplified RAG/LoRA systems
- **Size**: ~50MB

### 🧠 **Full ML Profile** (Complete features)
- All AI/ML capabilities
- Advanced RAG with vector search
- Full LoRA fine-tuning
- Document processing
- **Size**: ~2-3GB

### 🏭 **Production Profile** (Enterprise ready)
- Database support
- Caching and performance optimization
- Security features
- Monitoring and logging
- Production WSGI server
- **Size**: ~100-200MB (without ML)

## Environment Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install dependencies** (choose your profile above)

4. **Run the application**:
   ```bash
   ./run-local.sh
   # OR manually: cd backend && python app.py
   ```

## Troubleshooting

### Common Issues:

**PyTorch Installation Issues**:
```bash
# For CPU-only (smaller, faster install)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# For GPU support (if you have CUDA)
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

**Memory Issues with Large Models**:
- Use minimal installation for development
- Consider cloud deployment for full ML features

**Dependency Conflicts**:
```bash
# Create fresh environment
pip freeze > old_requirements.txt
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
# Install step by step
```

## Docker Installation (Alternative)

For containerized deployment:

```bash
# Build and run with Docker
docker-compose up --build
```

This uses the Dockerfile which automatically handles all dependencies.

## Verification

Test your installation:

```bash
python -c "import flask, groq; print('✅ Core dependencies installed')"

# For full ML installation:
python -c "import torch, transformers; print('✅ ML dependencies installed')"
```

## Support

- **Minimal issues**: Check Flask and Groq API setup
- **ML issues**: Verify PyTorch and transformers installation
- **Production issues**: Check database and server configuration

Choose the installation profile that matches your needs and system resources! 🎯