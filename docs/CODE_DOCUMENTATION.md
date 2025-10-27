# NexusAI - Complete Code Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [File Structure](#file-structure)
4. [Core Components](#core-components)
5. [Frontend Components](#frontend-components)
6. [Backend Components](#backend-components)
7. [Styling System](#styling-system)
8. [JavaScript Modules](#javascript-modules)
9. [API Endpoints](#api-endpoints)
10. [Configuration Files](#configuration-files)

---

## 🎯 Project Overview

**NexusAI** is a modern, advanced AI chat interface built with Flask and vanilla JavaScript. It provides a sophisticated user experience with support for multiple AI models, RAG (Retrieval-Augmented Generation), and LoRA (Low-Rank Adaptation) fine-tuning.

### Key Features
- **Multi-Model AI Chat**: Integration with Groq API for fast inference
- **RAG System**: Knowledge-enhanced responses using document retrieval
- **LoRA System**: Model fine-tuning capabilities
- **Modern UI**: Glass morphism design with smooth animations
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Accessibility**: WCAG compliant with keyboard navigation support

---

## 🏗️ Architecture

### Frontend Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HTML Layer    │    │   CSS Layer     │    │   JS Layer      │
│                 │    │                 │    │                 │
│ • Structure     │    │ • Styling       │    │ • Interactions  │
│ • Semantic      │    │ • Animations    │    │ • API Calls     │
│ • Accessibility │    │ • Responsive    │    │ • State Mgmt    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Backend Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │   AI Systems    │    │   Data Layer    │
│                 │    │                 │    │                 │
│ • Routes        │    │ • RAG System    │    │ • JSON Storage  │
│ • API Endpoints │    │ • LoRA System   │    │ • Session Mgmt  │
│ • Session Mgmt  │    │ • Groq Client   │    │ • File System   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 📁 File Structure

```
NexusAI/
├── 📄 app.py                          # Main Flask application
├── 📄 index.html                      # Main HTML template
├── 📄 simple_rag_system.py           # Simplified RAG/LoRA systems
├── 📄 rag_system.py                  # Full RAG system (optional)
├── 📄 lora_system.py                 # Full LoRA system (optional)
├── 📄 requirements.txt               # Python dependencies
├── 📄 .env.example                   # Environment variables template
├── 📄 CODE_DOCUMENTATION.md          # This documentation file
├── 📄 RAG_LORA_IMPLEMENTATION_GUIDE.md # Implementation guide
│
├── 📁 static/                         # Static assets
│   ├── 📁 css/                       # Stylesheets
│   │   ├── 📄 modern-ui-enhanced.css # Core UI styles
│   │   ├── 📄 enhanced-styling.css   # Glass morphism effects
│   │   ├── 📄 rag-lora-ui.css       # RAG/LoRA component styles
│   │   └── 📄 modern-theme.css       # Professional color theme
│   │
│   └── 📁 js/                        # JavaScript modules
│       ├── 📄 modern-ui-enhanced.js  # Core UI functionality
│       ├── 📄 rag-lora-ui.js        # RAG/LoRA UI components
│       ├── 📄 modern-chat.js         # Chat functionality
│       ├── 📄 conversation-manager.js # Conversation management
│       ├── 📄 ui-components.js       # Reusable UI components
│       ├── 📄 advanced-features.js   # Advanced features
│       └── 📄 app-init.js            # Application initialization
│
├── 📁 rag_data/                      # RAG system data storage
│   ├── 📄 documents.json            # Document metadata
│   └── 📄 chunks.json               # Document chunks
│
├── 📁 lora_data/                     # LoRA system data storage
│   └── 📄 adapters.json             # Adapter metadata
│
└── 📁 docs/                          # Documentation
    └── 📄 various documentation files
```

---

## 🔧 Core Components

### 1. Flask Application (app.py)

**Purpose**: Main backend server handling API requests and serving the web interface.

**Key Functions**:
```python
# Main chat endpoint - handles AI model interactions
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Processes chat messages with optional RAG/LoRA enhancement
    - Accepts user messages and optional image data
    - Integrates with RAG for knowledge enhancement
    - Supports LoRA adapter selection
    - Returns AI responses with metadata
    """

# RAG document upload endpoint
@app.route('/api/rag/upload', methods=['POST'])
def upload_document():
    """
    Uploads documents to the RAG knowledge base
    - Accepts document content and metadata
    - Processes and chunks documents
    - Stores in vector database
    """

# LoRA adapter management endpoints
@app.route('/api/lora/adapters', methods=['POST'])
def create_lora_adapter():
    """
    Creates new LoRA adapters for model fine-tuning
    - Accepts adapter configuration
    - Initializes training pipeline
    - Returns adapter ID for future use
    """
```

**Architecture Patterns**:
- **Dependency Injection**: RAG/LoRA systems are injected based on availability
- **Fallback Strategy**: Uses simplified systems when full ML libraries unavailable
- **Session Management**: Maintains user conversations and preferences
- **Error Handling**: Comprehensive error handling with user-friendly messages

### 2. HTML Structure (index.html)

**Purpose**: Semantic HTML structure with accessibility and SEO optimization.

**Key Sections**:
```html
<!-- Application Header -->
<header class="app-header">
    <!-- Logo, model selector, notifications, theme toggle -->
</header>

<!-- Main Content Area -->
<main class="main-content">
    <!-- Sidebar with conversations and RAG/LoRA panels -->
    <aside class="sidebar">
        <!-- Conversation list -->
        <!-- RAG knowledge base panel -->
        <!-- LoRA fine-tuning panel -->
    </aside>
    
    <!-- Chat Interface -->
    <section class="chat-container">
        <!-- Welcome screen -->
        <!-- Messages area -->
        <!-- Input area with enhancements -->
    </section>
</main>

<!-- Footer -->
<footer class="app-footer">
    <!-- Attribution and social links -->
</footer>
```

**Accessibility Features**:
- Semantic HTML5 elements
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- High contrast support

---

## 🎨 Frontend Components

### 1. Styling System

#### Modern UI Enhanced CSS (modern-ui-enhanced.css)
**Purpose**: Core UI styles with modern components and animations.

**Key Features**:
```css
/* CSS Custom Properties for theming */
:root {
    --primary-500: #0ea5e9;    /* NexusAI brand blue */
    --glass-primary: rgba(255, 255, 255, 0.05);  /* Glass morphism */
    --text-primary: #ffffff;    /* High contrast text */
}

/* Glass morphism components */
.glass-card {
    background: var(--glass-primary);
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Modern animations */
@keyframes slideInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}
```

#### Enhanced Styling CSS (enhanced-styling.css)
**Purpose**: Advanced glass morphism effects and sophisticated animations.

**Key Features**:
- Background gradient animations
- Enhanced button hover effects
- Conversation item animations
- Message bubble styling
- Welcome screen effects

#### Modern Theme CSS (modern-theme.css)
**Purpose**: Professional color theme with consistent NexusAI branding.

**Key Features**:
```css
/* NexusAI Brand Gradients */
:root {
    --nexus-gradient: linear-gradient(135deg, #0ea5e9, #0284c7);
    --nexus-gradient-hover: linear-gradient(135deg, #0284c7, #0369a1);
    --nexus-gradient-text: linear-gradient(135deg, #0ea5e9, #38bdf8);
}

/* Consistent gradient application */
.send-btn, .action-btn.primary {
    background: var(--nexus-gradient);
}
```

### 2. JavaScript Modules

#### Modern UI Enhanced JS (modern-ui-enhanced.js)
**Purpose**: Core UI functionality and interactions.

**Class Structure**:
```javascript
class ModernUIEnhanced {
    constructor() {
        this.theme = 'dark';           // Theme management
        this.animations = { enabled: true };  // Animation control
        this.notifications = [];       // Notification system
        this.tooltips = new Map();     // Tooltip management
    }
    
    // Key Methods:
    setupTheme()              // Theme switching logic
    setupAnimations()         // Animation initialization
    setupTooltips()          // Tooltip system
    updateNotificationBadge() // Notification management
    toggleNotificationDropdown() // Notification UI
}
```

#### RAG/LoRA UI JS (rag-lora-ui.js)
**Purpose**: Advanced AI features user interface.

**Class Structure**:
```javascript
class RAGLoRAUI {
    constructor() {
        this.ragEnabled = false;       // RAG availability
        this.loraEnabled = false;      // LoRA availability
        this.availableAdapters = [];   // LoRA adapters
        this.ragStats = {};           // RAG statistics
        this.loraStats = {};          // LoRA statistics
    }
    
    // Key Methods:
    checkFeatureAvailability() // Backend feature detection
    saveDocument()            // RAG document upload
    createAndTrainAdapter()   // LoRA adapter creation
    testRAG()                // RAG functionality testing
    testLoRA()               // LoRA functionality testing
}
```

---

## 🔙 Backend Components

### 1. RAG System (simple_rag_system.py)

**Purpose**: Lightweight RAG implementation without heavy ML dependencies.

**Class Structure**:
```python
class SimpleRAGSystem:
    def __init__(self):
        self.documents = {}          # Document storage
        self.document_chunks = {}    # Chunked documents
        self.data_dir = './rag_data' # Data directory
    
    # Key Methods:
    def add_document(content, metadata):
        """Add document to knowledge base"""
        # 1. Generate unique document ID
        # 2. Split document into chunks
        # 3. Store document and chunks
        # 4. Save to JSON files
    
    def retrieve_relevant_chunks(query, top_k):
        """Retrieve relevant chunks for query"""
        # 1. Tokenize query
        # 2. Score chunks by keyword matching
        # 3. Return top-k results
    
    def search_documents(query, limit):
        """Search documents and return results"""
        # 1. Get relevant chunks
        # 2. Group by document
        # 3. Return formatted results
```

**How RAG Works**:
1. **Document Ingestion**: Documents are split into chunks using word-based splitting
2. **Storage**: Chunks stored in JSON with metadata
3. **Retrieval**: Keyword matching with TF-IDF-like scoring
4. **Enhancement**: Retrieved chunks added to chat context

### 2. LoRA System (simple_rag_system.py)

**Purpose**: Simulated LoRA fine-tuning without actual model training.

**Class Structure**:
```python
class SimpleLoRASystem:
    def __init__(self):
        self.adapters = {}           # Adapter storage
        self.training_data = []      # Training examples
        self.data_dir = './lora_data' # Data directory
    
    # Key Methods:
    def create_lora_adapter(name, config):
        """Create new LoRA adapter"""
        # 1. Generate adapter ID
        # 2. Store adapter metadata
        # 3. Initialize training state
    
    def train_lora_adapter(adapter_id, training_args):
        """Simulate adapter training"""
        # 1. Validate training data
        # 2. Simulate training process
        # 3. Mark adapter as trained
    
    def list_adapters():
        """List all available adapters"""
        # Return formatted adapter list
```

**How LoRA Works**:
1. **Adapter Creation**: Metadata stored for new adapters
2. **Training Data**: JSON format conversation examples
3. **Training Simulation**: Mock training process with delays
4. **Integration**: Trained adapters available for chat enhancement

---

## 🔌 API Endpoints

### Chat Endpoints
```python
POST /api/chat
# Main chat endpoint
# Body: { message, model, use_rag, use_lora, lora_adapter_id }
# Response: { response, model_used, response_time, enhanced_with }

GET /api/models
# Get available AI models
# Response: { models: { available, text_models, vision_models } }
```

### RAG Endpoints
```python
POST /api/rag/upload
# Upload document to knowledge base
# Body: { content, metadata }
# Response: { document_id, status }

POST /api/rag/search
# Search knowledge base
# Body: { query, limit }
# Response: { results, count }

GET /api/rag/stats
# Get RAG system statistics
# Response: { documents, chunks, embedding_model }
```

### LoRA Endpoints
```python
GET /api/lora/adapters
# List all LoRA adapters
# Response: { adapters, count }

POST /api/lora/adapters
# Create new LoRA adapter
# Body: { name, config }
# Response: { adapter_id, name }

POST /api/lora/adapters/{id}/train
# Train LoRA adapter
# Body: { training_data, training_args }
# Response: { status, message }

GET /api/lora/stats
# Get LoRA system statistics
# Response: { total_adapters, trained_adapters }
```

### System Endpoints
```python
GET /api/features
# Check feature availability
# Response: { features: { rag, lora, groq } }

GET /api/status
# System health check
# Response: { status, rag_available, lora_available }
```

---

## ⚙️ Configuration Files

### Environment Variables (.env)
```bash
# Groq API Configuration
GROQ_API_KEY=<your-groq-api-key>

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# Optional: Custom model configurations
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
LORA_BASE_MODEL=microsoft/DialoGPT-medium
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
```

### Python Dependencies (requirements.txt)
```txt
# Core Flask dependencies
Flask==2.3.3
Werkzeug==2.3.7

# AI/ML dependencies (optional)
groq==0.4.1
transformers==4.36.0
torch==2.1.0
sentence-transformers==2.2.2
faiss-cpu==1.7.4
langchain==0.1.0
chromadb==0.4.18
peft==0.7.1

# Utility dependencies
python-dotenv==1.0.0
requests==2.31.0
flask-cors==4.0.0
```

---

## 🚀 Getting Started

### 1. Installation
```bash
# Clone repository
git clone <repository-url>
cd nexusai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Running the Application
```bash
# Start the Flask server
./run-local.sh

# Open browser to http://localhost:5002
```

### 3. Testing Features
```bash
# Test RAG functionality
# 1. Click "Upload Document" in Knowledge Base panel
# 2. Click "Load Sample" for demo content
# 3. Save document and test search

# Test LoRA functionality
# 1. Click "Create Adapter" in Model Fine-tuning panel
# 2. Click "Load Sample" for demo training data
# 3. Create and train adapter
```

---

## 🔧 Development Guidelines

### Code Style
- **Python**: Follow PEP 8 standards
- **JavaScript**: Use ES6+ features, camelCase naming
- **CSS**: Use BEM methodology, CSS custom properties
- **HTML**: Semantic elements, accessibility attributes

### Performance Considerations
- **CSS**: Use transform and opacity for animations
- **JavaScript**: Debounce user inputs, lazy load components
- **Backend**: Implement caching for frequently accessed data
- **Images**: Optimize and use appropriate formats

### Security Best Practices
- **API Keys**: Store in environment variables
- **Input Validation**: Sanitize all user inputs
- **CORS**: Configure appropriate origins
- **Session Management**: Use secure session cookies

---

## 📚 Additional Resources

- **RAG Implementation Guide**: `RAG_LORA_IMPLEMENTATION_GUIDE.md`
- **Project Overview**: `PROJECT_OVERVIEW.md`
- **API Documentation**: Available at `/api/docs` when running
- **Component Library**: Interactive examples in development mode

---

**Author**: Anurag Vaidhya  
**Powered by**: KIRO AI  
**Last Updated**: Current Date  
**Version**: 2.0