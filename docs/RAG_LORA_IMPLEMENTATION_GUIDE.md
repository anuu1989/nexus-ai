# RAG and LoRA Implementation Guide for NexusAI

## 🚀 Overview

This guide explains how to implement and use the RAG (Retrieval-Augmented Generation) and LoRA (Low-Rank Adaptation) features in your NexusAI chat interface.

## 📋 Prerequisites

### System Requirements
- Python 3.8+
- CUDA-compatible GPU (recommended for LoRA training)
- At least 8GB RAM (16GB+ recommended for LoRA)
- 10GB+ free disk space

### Dependencies Installation

```bash
# Install all required dependencies
pip install -r requirements.txt

# Or install individually:
pip install transformers torch sentence-transformers faiss-cpu
pip install langchain chromadb peft accelerate
pip install pypdf2 python-docx beautifulsoup4 markdown
```

## 🔧 Setup Instructions

### 1. Environment Configuration

Add these optional environment variables to your `.env` file:

```env
# Existing Groq API key
GROQ_API_KEY=<your-groq-api-key>

# Optional: Custom model configurations
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
LORA_BASE_MODEL=microsoft/DialoGPT-medium
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
```

### 2. Start the Application

```bash
./run-local.sh
# OR manually: cd backend && python app.py
```

The application will automatically:
- Initialize RAG and LoRA systems
- Create necessary directories (`./rag_data`, `./lora_models`)
- Load embedding models and set up vector stores

## 📚 RAG (Retrieval-Augmented Generation)

### What is RAG?
RAG enhances AI responses by retrieving relevant information from your knowledge base before generating answers.

### Features
- **Document Upload**: Support for text, PDF, and other formats
- **Vector Search**: Fast semantic search using FAISS and ChromaDB
- **Chunk Management**: Intelligent document splitting and indexing
- **Real-time Retrieval**: Context-aware information retrieval

### Usage

#### 1. Upload Documents via UI
1. Open the sidebar and find the "Knowledge Base (RAG)" panel
2. Click "Upload Document"
3. Paste your content or upload files
4. Add metadata (title, tags, etc.)
5. Click "Save Document"

#### 2. Upload Documents via API
```javascript
// Upload a document
const response = await fetch('/api/rag/upload', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        content: "Your document content here...",
        metadata: {
            title: "Document Title",
            source: "source_name",
            tags: ["tag1", "tag2"]
        }
    })
});
```

#### 3. Enable RAG in Chat
1. Toggle "Use Knowledge Base" in the input area
2. Your messages will now be enhanced with relevant context
3. The AI will use retrieved information to provide better answers

#### 4. Search Your Knowledge Base
```javascript
// Search documents
const response = await fetch('/api/rag/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        query: "your search query",
        limit: 10
    })
});
```

### RAG Configuration

The RAG system can be configured in `rag_system.py`:

```python
config = {
    'embedding_model': 'all-MiniLM-L6-v2',  # Embedding model
    'chunk_size': 1000,                      # Document chunk size
    'chunk_overlap': 200,                    # Overlap between chunks
    'max_chunks_per_query': 5,               # Max chunks to retrieve
    'similarity_threshold': 0.7,             # Minimum similarity score
    'vector_store_type': 'faiss',            # 'faiss' or 'chroma'
}
```

## 🧠 LoRA (Low-Rank Adaptation)

### What is LoRA?
LoRA allows you to fine-tune large language models efficiently by training only a small number of additional parameters.

### Features
- **Efficient Fine-tuning**: Train models with minimal computational resources
- **Multiple Adapters**: Create and manage multiple specialized adapters
- **Custom Training Data**: Use your own conversation data
- **Model Switching**: Switch between different fine-tuned versions

### Usage

#### 1. Create an Adapter via UI
1. Open the "Model Fine-tuning (LoRA)" panel
2. Click "Create Adapter"
3. Enter adapter name
4. Provide training data in JSON format:
```json
[
    {"input": "Hello", "output": "Hi there! How can I help you?"},
    {"input": "What's the weather?", "output": "I'd be happy to help with weather information!"}
]
```
5. Click "Create & Train"

#### 2. Create an Adapter via API
```javascript
// Create adapter
const createResponse = await fetch('/api/lora/adapters', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: "Customer Support Bot",
        config: {
            lora_r: 16,
            lora_alpha: 32,
            lora_dropout: 0.1
        }
    })
});

// Train adapter
const trainResponse = await fetch(`/api/lora/adapters/${adapterId}/train`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        training_data: [
            {"input": "Hello", "output": "Hi! How can I assist you today?"},
            // ... more training examples
        ],
        training_args: {
            num_train_epochs: 3,
            learning_rate: 5e-4
        }
    })
});
```

#### 3. Use Fine-tuned Models
1. Toggle "Use Fine-tuned Model" in the input area
2. Select your trained adapter from the dropdown
3. Your messages will now use the fine-tuned model

### LoRA Configuration

Configure LoRA parameters in `lora_system.py`:

```python
config = {
    'base_model': 'microsoft/DialoGPT-medium',  # Base model
    'lora_r': 16,                               # Rank of adaptation
    'lora_alpha': 32,                           # LoRA scaling parameter
    'lora_dropout': 0.1,                        # Dropout rate
    'target_modules': ['c_attn', 'c_proj'],     # Modules to adapt
    'max_length': 512,                          # Max sequence length
    'training_args': {
        'num_train_epochs': 3,
        'learning_rate': 5e-4,
        'per_device_train_batch_size': 4
    }
}
```

## 🔗 API Endpoints

### RAG Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/rag/upload` | POST | Upload a document |
| `/api/rag/search` | POST | Search documents |
| `/api/rag/stats` | GET | Get RAG statistics |

### LoRA Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/lora/adapters` | GET | List all adapters |
| `/api/lora/adapters` | POST | Create new adapter |
| `/api/lora/adapters/{id}/train` | POST | Train an adapter |
| `/api/lora/adapters/{id}` | GET | Get adapter info |
| `/api/lora/adapters/{id}` | DELETE | Delete adapter |
| `/api/lora/stats` | GET | Get LoRA statistics |

### Feature Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/features` | GET | Check feature availability |

## 💡 Best Practices

### RAG Best Practices

1. **Document Quality**: Use well-structured, relevant documents
2. **Chunk Size**: Adjust chunk size based on your content type
3. **Metadata**: Add rich metadata for better retrieval
4. **Regular Updates**: Keep your knowledge base current
5. **Query Optimization**: Use specific, well-formed queries

### LoRA Best Practices

1. **Training Data**: Use high-quality, diverse training examples
2. **Data Format**: Ensure consistent input/output formatting
3. **Hyperparameters**: Start with default values, then tune
4. **Evaluation**: Test your adapters thoroughly before deployment
5. **Resource Management**: Monitor GPU memory usage during training

## 🛠️ Troubleshooting

### Common Issues

#### RAG Issues
- **No results found**: Check similarity threshold and query phrasing
- **Slow retrieval**: Consider reducing chunk size or using FAISS
- **Memory issues**: Use smaller embedding models

#### LoRA Issues
- **Training fails**: Check GPU memory and reduce batch size
- **Poor performance**: Increase training data or epochs
- **CUDA errors**: Ensure proper PyTorch CUDA installation

### Performance Optimization

#### RAG Optimization
```python
# Use smaller embedding model for faster inference
config['embedding_model'] = 'all-MiniLM-L6-v2'

# Reduce chunk size for faster processing
config['chunk_size'] = 500
config['chunk_overlap'] = 100

# Use FAISS for faster search
config['vector_store_type'] = 'faiss'
```

#### LoRA Optimization
```python
# Reduce memory usage
config['training_args']['per_device_train_batch_size'] = 2
config['training_args']['gradient_accumulation_steps'] = 4

# Use mixed precision training
config['training_args']['fp16'] = True

# Reduce model size
config['base_model'] = 'gpt2'  # Smaller base model
```

## 📊 Monitoring and Analytics

### RAG Analytics
- Document count and chunk statistics
- Search query performance
- Retrieval accuracy metrics
- Storage usage

### LoRA Analytics
- Adapter count and training status
- Training time and resource usage
- Model performance metrics
- Inference speed

## 🔒 Security Considerations

1. **Data Privacy**: Ensure sensitive documents are properly secured
2. **Access Control**: Implement user-based access controls
3. **Model Security**: Validate training data to prevent poisoning
4. **API Security**: Use proper authentication for API endpoints

## 🚀 Advanced Usage

### Custom Embedding Models
```python
# Use custom embedding model
from sentence_transformers import SentenceTransformer

custom_model = SentenceTransformer('your-custom-model')
rag_system.embedding_model = custom_model
```

### Custom LoRA Configurations
```python
# Advanced LoRA configuration
lora_config = {
    'r': 32,                    # Higher rank for more capacity
    'lora_alpha': 64,           # Higher alpha for stronger adaptation
    'target_modules': ['q_proj', 'v_proj', 'k_proj', 'o_proj'],  # More modules
    'modules_to_save': ['embed_tokens', 'lm_head']  # Additional modules
}
```

## 📈 Scaling Considerations

### Production Deployment
1. **Database Integration**: Replace in-memory storage with persistent databases
2. **Caching**: Implement Redis for faster retrieval
3. **Load Balancing**: Distribute requests across multiple instances
4. **Monitoring**: Set up comprehensive logging and monitoring
5. **Backup**: Regular backups of models and knowledge base

### Resource Planning
- **RAG**: 4-8GB RAM, SSD storage for vector indices
- **LoRA**: 8-16GB GPU memory for training, 4-8GB for inference
- **Combined**: 16-32GB total system memory recommended

## 🤝 Contributing

To contribute to the RAG/LoRA implementation:

1. Fork the repository
2. Create feature branches for RAG or LoRA improvements
3. Add comprehensive tests
4. Update documentation
5. Submit pull requests

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation
- Open GitHub issues for bugs
- Join community discussions

---

**Note**: This implementation provides a solid foundation for RAG and LoRA features. For production use, consider additional optimizations, security measures, and scalability improvements based on your specific requirements.