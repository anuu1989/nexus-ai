"""
NexusAI - Advanced AI Chat Interface
====================================

A modern Flask-based web application that provides an advanced AI chat interface
with support for multiple AI models, RAG (Retrieval-Augmented Generation), 
and LoRA (Low-Rank Adaptation) fine-tuning capabilities.

Features:
- Multi-model AI chat (Groq API integration)
- RAG system for knowledge-enhanced responses
- LoRA system for model fine-tuning
- Modern glass morphism UI design
- Real-time conversation management
- Template system for common prompts
- Model comparison capabilities
- Analytics and usage tracking

Author: Anurag Vaidhya
Powered by: KIRO AI
"""

# === CORE IMPORTS ===
from flask import Flask, request, jsonify, render_template, session
import os
import time
import json
import hashlib
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv

# === MODULAR IMPORTS ===
from api.chat_routes import register_chat_routes
from utils.helpers import get_session_id

# === AI MODEL CLIENT IMPORT ===
# Import multi-provider LLM system
try:
    from models.llm_providers import get_llm_manager, initialize_llm_providers
    print("✅ Multi-provider LLM system imported successfully")
    LLM_PROVIDERS_AVAILABLE = True
except ImportError:
    print("❌ Error: Could not import LLM providers system")
    LLM_PROVIDERS_AVAILABLE = False

# Legacy Groq client for backward compatibility
try:
    from groq import Groq
    print("✅ Groq client library imported successfully")
except ImportError:
    print("❌ Error: Could not import Groq client. Please install with: pip install groq")
    Groq = None

# === RAG AND LORA SYSTEMS IMPORT ===
# Try to import advanced RAG/LoRA systems first, fallback to simplified versions
try:
    # Attempt to import full-featured systems with ML dependencies
    from models.rag_system import get_rag_system, initialize_rag
    from models.lora_system import get_lora_system, initialize_lora
    RAG_AVAILABLE = True
    LORA_AVAILABLE = True
    print("✅ Using full RAG/LoRA systems with ML capabilities")
except ImportError as e:
    try:
        # Fallback to simplified systems that work without heavy ML dependencies
        from models.simple_rag_system import get_rag_system, initialize_rag, get_lora_system, initialize_lora
        RAG_AVAILABLE = True
        LORA_AVAILABLE = True
        print("✅ Using simplified RAG/LoRA systems")
    except ImportError as e2:
        print(f"RAG/LoRA systems not available: {e2}")
        RAG_AVAILABLE = False
        LORA_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configure Flask to serve frontend files
app = Flask(__name__, 
            static_folder='../frontend/static',
            template_folder='../frontend')
app.secret_key = os.environ.get('SECRET_KEY', 'ai-assistant-secret-key-2024')

# In-memory storage for demo (use database in production)
conversations = defaultdict(list)
templates_db = []
model_comparisons = []

# Initialize multi-provider LLM system
llm_manager = None
if LLM_PROVIDERS_AVAILABLE:
    try:
        if initialize_llm_providers():
            llm_manager = get_llm_manager()
            print("✅ Multi-provider LLM system initialized successfully")
        else:
            print("❌ Error initializing multi-provider LLM system")
    except Exception as e:
        print(f"❌ Error initializing LLM providers: {e}")

# Legacy Groq client for backward compatibility
client = None
if Groq is not None:
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        try:
            client = Groq(api_key=api_key)
            print("✅ Legacy Groq client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing legacy Groq client: {e}")
    else:
        print("❌ GROQ_API_KEY not found in environment variables")

# Initialize RAG and LoRA systems
rag_system = None
lora_system = None

if RAG_AVAILABLE:
    try:
        if initialize_rag():
            rag_system = get_rag_system()
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        RAG_AVAILABLE = False

if LORA_AVAILABLE:
    try:
        if initialize_lora():
            lora_system = get_lora_system()
    except Exception as e:
        print(f"❌ Error initializing LoRA system: {e}")

# Register modular routes
register_chat_routes(app, llm_manager, client, rag_system, lora_system)

def get_max_tokens_for_model(model_name: str) -> int:
    """Get appropriate max_tokens for a given model"""
    # Model-specific token limits (very conservative to avoid errors)
    model_limits = {
        # Groq models - conservative limits
        "llama-3.1-8b-instant": 1024,
        "llama-3.1-70b-versatile": 1024,
        "llama-3.2-1b-preview": 256,
        "llama-3.2-3b-preview": 512,
        "llama-3.2-11b-text-preview": 1024,
        "llama-3.2-90b-text-preview": 1024,
        "llama-3.2-11b-vision-preview": 1024,
        "mixtral-8x7b-32768": 1024,
        "gemma-7b-it": 512,
        "gemma2-9b-it": 512,
        
        # OpenAI models
        "gpt-4o": 2048,
        "gpt-4o-mini": 2048,
        "gpt-4-turbo": 2048,
        "gpt-4": 1024,
        "gpt-3.5-turbo": 1024,
        
        # Anthropic models
        "claude-3-5-sonnet-20241022": 2048,
        "claude-3-haiku-20240307": 1024,
    }
    
    # Get limit for specific model, or use very conservative default
    # Get limit for specific model, or use very conservative default
    limit = model_limits.get(model_name, 256)
    
    # Safety check: never exceed 512 tokens to avoid API errors
    return min(limit, 512)

@app.route('/')
def home():
    with open('../frontend/index.html', 'r') as f:
        return f.read()

@app.route('/manifest.json')
def manifest():
    """Serve the PWA manifest file"""
    try:
        with open('../frontend/public/manifest.json', 'r') as f:
            manifest_data = f.read()
        response = app.response_class(
            response=manifest_data,
            status=200,
            mimetype='application/json'
        )
        return response
    except FileNotFoundError:
        return jsonify({'error': 'Manifest file not found'}), 404

def apply_ai_guardrails(message):
    """Apply AI guardrails to filter unsafe content"""
    import re
    
    # Content Safety Check
    unsafe_patterns = [
        r'\b(violence|harm|kill|murder|suicide|death)\b',
        r'\b(hate|racist|discrimination|nazi|terrorist)\b',
        r'\b(illegal|drugs|weapons|bomb|explosive)\b',
        r'\b(hack|crack|steal|fraud|scam)\b',
        r'\b(porn|sexual|explicit|nude)\b'
    ]
    
    for pattern in unsafe_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return {
                'blocked': True,
                'reason': 'Content contains potentially harmful or unsafe material',
                'category': 'content_safety'
            }
    
    # Prompt Injection Check
    injection_patterns = [
        r'ignore\s+(previous|all|earlier)\s+(instructions?|prompts?|commands?)',
        r'forget\s+(everything|all|previous)',
        r'you\s+are\s+now\s+',
        r'system\s*:\s*',
        r'\[INST\]',
        r'\<\|system\|\>',
        r'override\s+(previous|system)',
        r'new\s+(instructions?|role|persona)',
        r'act\s+as\s+if',
        r'pretend\s+(you\s+are|to\s+be)',
        r'roleplay\s+as',
        r'simulate\s+being'
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return {
                'blocked': True,
                'reason': 'Potential prompt injection detected',
                'category': 'prompt_injection'
            }
    
    # PII Detection Check
    pii_patterns = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b',  # Credit card
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{3}-\d{3}-\d{4}\b'  # Phone number
    ]
    
    for pattern in pii_patterns:
        if re.search(pattern, message):
            return {
                'blocked': True,
                'reason': 'Personally Identifiable Information (PII) detected',
                'category': 'pii_detection'
            }
    
    return {'blocked': False}

# Chat route now handled by modular system

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Get status of all LLM providers"""
    try:
        if llm_manager is not None:
            provider_status = llm_manager.get_provider_status()
            return jsonify({
                'providers': provider_status,
                'multi_provider_enabled': True,
                'status': 'success'
            })
        else:
            # Fallback to legacy Groq-only status
            groq_status = {
                'groq': {
                    'name': 'Groq',
                    'enabled': client is not None,
                    'priority': 1,
                    'rate_limit': 30,
                    'requests_last_minute': 0
                }
            }
            return jsonify({
                'providers': groq_status,
                'multi_provider_enabled': False,
                'status': 'success'
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/models/refresh', methods=['POST'])
def refresh_models():
    """Force refresh models from all providers in real-time"""
    try:
        if llm_manager is not None:
            # Clear any cached data and fetch fresh from APIs
            fresh_models = llm_manager.get_available_models()
            
            return jsonify({
                'models': fresh_models,
                'total_count': len(fresh_models),
                'providers': llm_manager.get_provider_status(),
                'timestamp': time.time(),
                'status': 'success',
                'message': f'Refreshed {len(fresh_models)} models from active providers'
            })
        else:
            return jsonify({
                'error': 'Multi-provider system not available',
                'status': 'error'
            }), 500
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/guardrails/status', methods=['GET'])
def get_guardrails_status():
    """Get AI Guardrails status and statistics"""
    return jsonify({
        'status': 'active',
        'guardrails': {
            'content_safety': {'enabled': True, 'description': 'Blocks harmful and unsafe content'},
            'prompt_injection': {'enabled': True, 'description': 'Prevents prompt manipulation attempts'},
            'pii_detection': {'enabled': True, 'description': 'Detects and blocks personal information'}
        },
        'statistics': {
            'total_messages_processed': 0,  # This would be tracked in a real implementation
            'messages_blocked': 0,
            'last_updated': datetime.now().isoformat()
        }
    })


@app.route('/api/rag/upload', methods=['POST'])
def upload_documents():
    """Upload documents to the knowledge base"""
    try:
        if 'documents' not in request.files:
            return jsonify({'error': 'No documents provided', 'status': 'error'}), 400
        
        files = request.files.getlist('documents')
        processed_docs = []
        
        for file in files:
            if file.filename == '':
                continue
                
            # Simulate document processing
            doc_info = {
                'id': hashlib.md5(f"{file.filename}{time.time()}".encode()).hexdigest(),
                'name': file.filename,
                'size': len(file.read()),
                'type': file.filename.split('.')[-1].upper() if '.' in file.filename else 'UNKNOWN',
                'chunks_created': 25,  # Simulated
                'processed_at': datetime.now().isoformat()
            }
            processed_docs.append(doc_info)
        
        return jsonify({
            'message': f'Successfully processed {len(processed_docs)} documents',
            'documents': processed_docs,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/rag/search', methods=['POST'])
def search_knowledge_base():
    """Search the knowledge base"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided', 'status': 'error'}), 400
        
        # Simulate intelligent search
        search_results = [
            {
                'document': 'NexusAI Documentation.pdf',
                'chunk': f'This section covers {query} in detail, explaining the core concepts and implementation strategies.',
                'relevance': 0.95,
                'page': 12,
                'chunk_id': 'doc1_chunk12'
            },
            {
                'document': 'Machine Learning Guide.docx',
                'chunk': f'Advanced techniques for {query} are discussed here, including best practices and common pitfalls.',
                'relevance': 0.87,
                'page': 8,
                'chunk_id': 'doc2_chunk8'
            }
        ]
        
        return jsonify({
            'query': query,
            'results': search_results,
            'total_results': len(search_results),
            'search_time': 0.8,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/rag/analyze', methods=['GET'])
def analyze_knowledge_base():
    """Analyze the knowledge base and provide insights"""
    try:
        # Simulate knowledge base analysis
        analysis = {
            'total_documents': 3,
            'total_chunks': 95,
            'total_queries': 12,
            'top_topics': ['AI', 'Documentation', 'Machine Learning', 'API', 'Development'],
            'coverage_score': 85,
            'freshness_score': 92,
            'searchability_score': 88,
            'recommendations': [
                'Consider adding more content on emerging AI topics',
                'Update older documentation for better relevance',
                'Optimize chunk sizes for better search performance'
            ],
            'query_patterns': {
                'most_common': 'AI features',
                'recent_trends': ['machine learning', 'API usage', 'documentation'],
                'search_frequency': 'High'
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({
            'analysis': analysis,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/rag/summary', methods=['GET'])
def get_knowledge_summary():
    """Get a summary of the knowledge base"""
    try:
        summary = {
            'overview': {
                'total_documents': 3,
                'total_chunks': 95,
                'storage_used': '4.6 MB',
                'last_updated': datetime.now().isoformat()
            },
            'top_documents': [
                {'name': 'NexusAI Documentation.pdf', 'chunks': 45, 'size': '2.3 MB'},
                {'name': 'Machine Learning Guide.docx', 'chunks': 32, 'size': '1.8 MB'},
                {'name': 'API Reference.md', 'chunks': 18, 'size': '0.5 MB'}
            ],
            'topic_distribution': {
                'AI': 35,
                'Documentation': 28,
                'Machine Learning': 22,
                'API': 15
            },
            'usage_stats': {
                'total_searches': 12,
                'avg_relevance': 0.89,
                'most_queried_topic': 'AI'
            }
        }
        
        return jsonify({
            'summary': summary,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/lora/adapters', methods=['GET'])
def get_lora_adapters():
    """Get all LoRA adapters"""
    try:
        # Simulate adapter data
        adapters = [
            {
                'id': 1,
                'name': 'Customer Support Specialist',
                'type': 'Task-Specific',
                'status': 'trained',
                'performance': 0.94,
                'rank': 16,
                'alpha': 32,
                'training_time': 15,
                'dataset': 'customer_support_1k.json',
                'created': datetime.now().isoformat(),
                'active': True
            },
            {
                'id': 2,
                'name': 'Code Documentation Writer',
                'type': 'Domain-Specific',
                'status': 'trained',
                'performance': 0.87,
                'rank': 8,
                'alpha': 16,
                'training_time': 8,
                'dataset': 'code_docs_500.json',
                'created': datetime.now().isoformat(),
                'active': False
            }
        ]
        
        return jsonify({
            'adapters': adapters,
            'total_count': len(adapters),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/lora/create', methods=['POST'])
def create_lora_adapter():
    """Create a new LoRA adapter"""
    try:
        data = request.get_json()
        name = data.get('name', 'Untitled Adapter')
        adapter_type = data.get('type', 'General')
        rank = data.get('rank', 16)
        alpha = data.get('alpha', 32)
        
        # Simulate adapter creation
        new_adapter = {
            'id': hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:8],
            'name': name,
            'type': adapter_type,
            'status': 'draft',
            'performance': 0.0,
            'rank': rank,
            'alpha': alpha,
            'training_time': 0,
            'dataset': 'No dataset',
            'created': datetime.now().isoformat(),
            'active': False
        }
        
        return jsonify({
            'adapter': new_adapter,
            'message': f'Adapter "{name}" created successfully',
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/lora/train', methods=['POST'])
def train_lora_adapter():
    """Start training a LoRA adapter"""
    try:
        data = request.get_json()
        adapter_id = data.get('adapter_id')
        dataset_path = data.get('dataset_path', 'default_dataset.json')
        
        if not adapter_id:
            return jsonify({'error': 'Adapter ID required', 'status': 'error'}), 400
        
        # Simulate training process
        training_job = {
            'job_id': hashlib.md5(f"{adapter_id}{time.time()}".encode()).hexdigest()[:8],
            'adapter_id': adapter_id,
            'status': 'training',
            'progress': 0,
            'estimated_time': 15,  # minutes
            'started_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'training_job': training_job,
            'message': 'Training started successfully',
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/lora/analyze', methods=['GET'])
def analyze_lora_performance():
    """Analyze LoRA adapter performance"""
    try:
        # Simulate performance analysis
        analysis = {
            'total_adapters': 3,
            'trained_adapters': 2,
            'average_performance': 0.905,
            'best_performing': {
                'name': 'Customer Support Specialist',
                'performance': 0.94
            },
            'training_efficiency': {
                'average_time': 11.5,
                'success_rate': 0.85
            },
            'recommendations': [
                'Consider increasing LoRA rank for better performance',
                'Experiment with different learning rates',
                'Use larger datasets for improved generalization'
            ],
            'hyperparameter_insights': {
                'optimal_rank_range': [8, 32],
                'recommended_alpha': 32,
                'best_learning_rate': '3e-4'
            }
        }
        
        return jsonify({
            'analysis': analysis,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/lora/optimize', methods=['POST'])
def optimize_hyperparameters():
    """Optimize hyperparameters for LoRA training"""
    try:
        data = request.get_json()
        dataset_size = data.get('dataset_size', 1000)
        task_type = data.get('task_type', 'general')
        
        # Simulate hyperparameter optimization
        import random
        
        optimal_params = {
            'rank': random.choice([8, 16, 32]),
            'alpha': random.choice([16, 32, 64]),
            'learning_rate': random.choice(['1e-4', '3e-4', '1e-3']),
            'batch_size': random.choice([1, 2, 4]),
            'epochs': random.choice([3, 5, 10]),
            'warmup_steps': random.choice([100, 200, 500])
        }
        
        optimization_results = {
            'optimal_parameters': optimal_params,
            'expected_performance': round(0.75 + random.random() * 0.2, 3),
            'estimated_training_time': random.randint(8, 25),
            'confidence_score': round(0.8 + random.random() * 0.15, 2),
            'reasoning': {
                'rank': f"Rank {optimal_params['rank']} balances capacity and efficiency",
                'alpha': f"Alpha {optimal_params['alpha']} provides stable training",
                'learning_rate': f"Learning rate {optimal_params['learning_rate']} optimizes convergence"
            }
        }
        
        return jsonify({
            'optimization': optimization_results,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

# Models route now handled by modular system

def format_model_name(model_id):
    """Format model ID into a human-readable name"""
    name_map = {
        'llama-3.1-8b-instant': 'Llama 3.1 8B (Lightning Fast)',
        'llama-3.1-70b-versatile': 'Llama 3.1 70B (Ultra Smart)',
        'llama-3.2-1b-preview': 'Llama 3.2 1B (Compact)',
        'llama-3.2-3b-preview': 'Llama 3.2 3B (Efficient)',
        'llama-3.2-11b-text-preview': 'Llama 3.2 11B (Balanced)',
        'llama-3.2-90b-text-preview': 'Llama 3.2 90B (Powerful)',
        'llama-3.2-11b-vision-preview': 'Llama 3.2 Vision (Image AI)',
        'llama-3.2-90b-vision-preview': 'Llama 3.2 Vision Pro (Advanced)',
        'mixtral-8x7b-32768': 'Mixtral 8x7B (Expert Mix)',
        'gemma-7b-it': 'Gemma 7B (Google)',
        'gemma2-9b-it': 'Gemma 2 9B (Google Next)'
    }
    
    return name_map.get(model_id, model_id.replace('-', ' ').title())

def get_model_description(model_id):
    """Get detailed description for a model"""
    descriptions = {
        'llama-3.1-8b-instant': 'Ultra-fast responses for everyday conversations and quick tasks',
        'llama-3.3-70b-versatile': 'Advanced reasoning for complex problems, coding, and analysis',
        'openai/gpt-oss-20b': 'OpenAI GPT model optimized for general tasks',
        'openai/gpt-oss-120b': 'Large OpenAI GPT model for complex reasoning',
        'groq/compound': 'Groq\'s advanced compound model for specialized tasks',
        'groq/compound-mini': 'Compact version of Groq\'s compound model',
        'deepseek-r1-distill-llama-70b': 'DeepSeek reasoning model for analytical tasks',
        'qwen/qwen3-32b': 'Qwen 3 model for multilingual and reasoning tasks',
        'moonshotai/kimi-k2-instruct': 'Moonshot AI instruction-following model',
        'allam-2-7b': 'IBM Allam model for general conversation',
        'meta-llama/llama-4-maverick-17b-128e-instruct': 'Latest Llama 4 model with vision and enhanced capabilities',
        'meta-llama/llama-4-scout-17b-16e-instruct': 'Llama 4 Scout with vision for exploration and analysis'
    }
    
    # Generate description based on model characteristics if not in map
    if model_id not in descriptions:
        if 'whisper' in model_id:
            return 'Audio transcription and speech recognition model'
        elif 'tts' in model_id:
            return 'Text-to-speech synthesis model'
        elif 'guard' in model_id:
            return 'Content safety and moderation model'
        elif 'prompt-guard' in model_id:
            return 'Prompt injection detection model'
        else:
            return f'Advanced AI model: {model_id}'
    
    return descriptions[model_id]

def get_model_category(model_id):
    """Categorize model by primary use case"""
    if 'vision' in model_id.lower():
        return 'vision'
    elif '70b' in model_id or '90b' in model_id:
        return 'advanced'
    elif '1b' in model_id or '3b' in model_id:
        return 'compact'
    elif 'mixtral' in model_id.lower():
        return 'expert'
    else:
        return 'general'

def get_model_category_from_capabilities(capabilities):
    """Categorize model by capabilities"""
    if 'vision' in capabilities:
        return 'vision'
    elif 'analysis' in capabilities:
        return 'advanced'
    elif 'code' in capabilities:
        return 'coding'
    else:
        return 'general'

def get_model_speed_from_cost(cost_per_1k_tokens):
    """Estimate model speed based on cost (lower cost usually means faster)"""
    if cost_per_1k_tokens < 0.0001:
        return 10  # Very fast
    elif cost_per_1k_tokens < 0.001:
        return 8   # Fast
    elif cost_per_1k_tokens < 0.003:
        return 6   # Medium
    else:
        return 4   # Slower but more capable

def get_model_speed(model_id):
    """Get relative speed score (higher = faster)"""
    # Assign speed based on model characteristics
    if 'instant' in model_id:
        return 10
    elif any(size in model_id for size in ['8b', '7b', '2b']):
        return 9
    elif any(size in model_id for size in ['20b', '17b']):
        return 7
    elif any(size in model_id for size in ['32b', '70b']):
        return 5
    elif any(size in model_id for size in ['120b']):
        return 3
    elif 'compound' in model_id:
        return 6 if 'mini' in model_id else 4
    else:
        return 5

def get_model_capabilities(model_id):
    """Get list of model capabilities"""
    base_caps = ['text_generation', 'conversation', 'question_answering']
    
    if 'vision' in model_id.lower():
        return base_caps + ['image_analysis', 'visual_reasoning', 'chart_reading']
    elif '70b' in model_id or '90b' in model_id:
        return base_caps + ['complex_reasoning', 'code_generation', 'mathematical_analysis', 'creative_writing']
    elif 'mixtral' in model_id.lower():
        return base_caps + ['specialized_tasks', 'expert_knowledge', 'multi_domain']
    else:
        return base_caps + ['general_tasks', 'quick_responses']

def get_fastest_model(models):
    """Get the fastest available model"""
    # Prefer instant models
    instant_models = [m for m in models if 'instant' in m['id']]
    if instant_models:
        return instant_models[0]['id']
    return models[0]['id'] if models else None

def get_smartest_model(models):
    """Get the most capable model for complex tasks"""
    # Look for larger models first
    smart_models = [m for m in models if any(size in m['id'] for size in ['70b', '120b', 'compound'])]
    if smart_models:
        return smart_models[0]['id']
    return get_fastest_model(models)

def get_coding_model(models):
    """Get best model for coding tasks"""
    # Prefer larger models or specialized ones
    coding_models = [m for m in models if any(keyword in m['id'].lower() for keyword in ['70b', '120b', 'compound', 'deepseek'])]
    if coding_models:
        return coding_models[0]['id']
    return get_fastest_model(models)

def get_creative_model(models):
    """Get best model for creative tasks"""
    # Prefer versatile or large models
    creative_models = [m for m in models if any(keyword in m['id'] for keyword in ['versatile', '70b', 'compound'])]
    if creative_models:
        return creative_models[0]['id']
    return get_fastest_model(models)

def get_fallback_models():
    """Fallback models when API is unavailable"""
    return [
        {
            'id': 'llama-3.1-8b-instant',
            'name': 'Llama 3.1 8B (Fast)',
            'description': 'Fast and efficient for general conversations',
            'supportsVision': False,
            'category': 'general',
            'speed': 10
        }
    ]

def select_best_model(message, has_image, preferred_model=None):
    """Intelligently select the best model based on input characteristics"""
    try:
        # Get available models
        models_response = client.models.list()
        available_model_ids = [model.id for model in models_response.data]
        
        # If user has a preference and it's available, use it
        if preferred_model and preferred_model in available_model_ids:
            return preferred_model
        
        # If image is present, use vision model
        if has_image:
            # Check for Llama 4 vision models first
            llama4_vision_models = ['meta-llama/llama-4-maverick-17b-128e-instruct', 'meta-llama/llama-4-scout-17b-16e-instruct']
            available_llama4_vision = [mid for mid in available_model_ids if mid in llama4_vision_models]
            
            if available_llama4_vision:
                # Prefer maverick over scout for better vision capabilities
                if 'meta-llama/llama-4-maverick-17b-128e-instruct' in available_llama4_vision:
                    return 'meta-llama/llama-4-maverick-17b-128e-instruct'
                else:
                    return available_llama4_vision[0]
            
            # Fallback to other vision models
            vision_models = [mid for mid in available_model_ids if 'vision' in mid.lower()]
            if vision_models:
                return vision_models[0]
        
        # Analyze message content for complexity
        if message:
            complexity_score = analyze_message_complexity(message)
            
            # High complexity - use powerful model
            if complexity_score >= 7:
                powerful_models = [mid for mid in available_model_ids if any(size in mid for size in ['70b', '90b'])]
                if powerful_models:
                    return powerful_models[0]
            
            # Medium complexity - use balanced model
            elif complexity_score >= 4:
                balanced_models = [mid for mid in available_model_ids if '11b' in mid and 'vision' not in mid]
                if balanced_models:
                    return balanced_models[0]
        
        # Default to fastest model for simple tasks
        fast_models = [mid for mid in available_model_ids if '8b-instant' in mid]
        if fast_models:
            return fast_models[0]
        
        # Fallback to first available model
        return available_model_ids[0] if available_model_ids else 'llama-3.1-8b-instant'
        
    except Exception as e:
        print(f"Error in model selection: {e}")
        return get_default_model(has_image)

def analyze_message_complexity(message):
    """Analyze message complexity and return a score (1-10)"""
    if not message:
        return 1
    
    complexity_score = 1
    message_lower = message.lower()
    
    # Length factor
    if len(message) > 200:
        complexity_score += 2
    elif len(message) > 100:
        complexity_score += 1
    
    # Technical keywords
    technical_keywords = [
        'code', 'programming', 'algorithm', 'function', 'class', 'variable',
        'database', 'sql', 'api', 'json', 'xml', 'regex', 'debug', 'error',
        'analyze', 'calculate', 'solve', 'optimize', 'implement', 'design'
    ]
    
    tech_count = sum(1 for keyword in technical_keywords if keyword in message_lower)
    complexity_score += min(tech_count, 3)
    
    # Mathematical content
    math_indicators = ['equation', 'formula', 'calculate', 'mathematics', 'statistics', 'probability']
    if any(indicator in message_lower for indicator in math_indicators):
        complexity_score += 2
    
    # Creative writing indicators
    creative_indicators = ['story', 'poem', 'creative', 'write', 'essay', 'article']
    if any(indicator in message_lower for indicator in creative_indicators):
        complexity_score += 1
    
    # Question complexity
    question_words = message_lower.count('?')
    if question_words > 1:
        complexity_score += 1
    
    # Multiple topics (semicolons, "and", "also")
    topic_indicators = message_lower.count(';') + message_lower.count(' and ') + message_lower.count('also')
    if topic_indicators > 2:
        complexity_score += 1
    
    return min(complexity_score, 10)

def get_default_model(needs_vision=False):
    """Get the default model based on requirements"""
    try:
        models_response = client.models.list()
        available_model_ids = [model.id for model in models_response.data]
        
        if needs_vision:
            # Prefer Llama 4 vision models
            llama4_vision_models = ['meta-llama/llama-4-maverick-17b-128e-instruct', 'meta-llama/llama-4-scout-17b-16e-instruct']
            available_llama4_vision = [mid for mid in available_model_ids if mid in llama4_vision_models]
            
            if available_llama4_vision:
                return 'meta-llama/llama-4-maverick-17b-128e-instruct' if 'meta-llama/llama-4-maverick-17b-128e-instruct' in available_llama4_vision else available_llama4_vision[0]
            
            # Fallback to other vision models
            vision_models = [mid for mid in available_model_ids if 'vision' in mid.lower()]
            return vision_models[0] if vision_models else 'meta-llama/llama-4-maverick-17b-128e-instruct'
        else:
            fast_models = [mid for mid in available_model_ids if '8b-instant' in mid]
            return fast_models[0] if fast_models else 'llama-3.1-8b-instant'
            
    except Exception:
        return 'meta-llama/llama-4-maverick-17b-128e-instruct' if needs_vision else 'llama-3.1-8b-instant'

def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in session:
        session['session_id'] = hashlib.md5(f"{time.time()}".encode()).hexdigest()
    return session['session_id']

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations for current session"""
    try:
        session_id = get_session_id()
        user_conversations = conversations.get(session_id, [])
        
        # Format conversations for frontend
        formatted_conversations = []
        for conv in user_conversations:
            formatted_conversations.append({
                'id': conv.get('id'),
                'title': conv.get('title', 'New Conversation'),
                'created': conv.get('created'),
                'updated': conv.get('updated'),
                'messageCount': len(conv.get('messages', [])),
                'model': conv.get('model'),
                'preview': conv.get('messages', [{}])[0].get('content', '')[:100] if conv.get('messages') else ''
            })
        
        return jsonify({
            'conversations': formatted_conversations,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/conversations', methods=['POST'])
def save_conversation():
    """Save a conversation"""
    try:
        session_id = get_session_id()
        data = request.get_json()
        
        conversation = {
            'id': data.get('id', hashlib.md5(f"{time.time()}".encode()).hexdigest()),
            'title': data.get('title', 'New Conversation'),
            'messages': data.get('messages', []),
            'model': data.get('model'),
            'created': data.get('created', datetime.now().isoformat()),
            'updated': datetime.now().isoformat()
        }
        
        # Find existing conversation or add new one
        user_conversations = conversations[session_id]
        existing_index = next((i for i, conv in enumerate(user_conversations) if conv['id'] == conversation['id']), None)
        
        if existing_index is not None:
            user_conversations[existing_index] = conversation
        else:
            user_conversations.insert(0, conversation)
        
        return jsonify({
            'conversation': conversation,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation"""
    try:
        session_id = get_session_id()
        user_conversations = conversations.get(session_id, [])
        
        conversation = next((conv for conv in user_conversations if conv['id'] == conversation_id), None)
        
        if not conversation:
            return jsonify({'error': 'Conversation not found', 'status': 'error'}), 404
        
        return jsonify({
            'conversation': conversation,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    try:
        session_id = get_session_id()
        user_conversations = conversations[session_id]
        
        conversations[session_id] = [conv for conv in user_conversations if conv['id'] != conversation_id]
        
        return jsonify({
            'message': 'Conversation deleted successfully',
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all message templates"""
    try:
        return jsonify({
            'templates': templates_db,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/templates', methods=['POST'])
def create_template():
    """Create a new template"""
    try:
        data = request.get_json()
        
        template = {
            'id': hashlib.md5(f"{time.time()}".encode()).hexdigest(),
            'title': data.get('title'),
            'content': data.get('content'),
            'category': data.get('category', 'general'),
            'tags': data.get('tags', []),
            'created': datetime.now().isoformat(),
            'usage_count': 0
        }
        
        templates_db.append(template)
        
        return jsonify({
            'template': template,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/templates/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a template"""
    try:
        global templates_db
        templates_db = [t for t in templates_db if t['id'] != template_id]
        
        return jsonify({
            'message': 'Template deleted successfully',
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/templates/<template_id>/use', methods=['POST'])
def use_template(template_id):
    """Use a template (increment usage count)"""
    try:
        template = next((t for t in templates_db if t['id'] == template_id), None)
        if template:
            template['usage_count'] += 1
        
        return jsonify({
            'template': template,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/models/compare', methods=['POST'])
def compare_models():
    """Compare responses from multiple models"""
    try:
        if client is None:
            return jsonify({
                'error': 'Groq client not initialized',
                'status': 'error'
            }), 500
        
        data = request.get_json()
        message = data.get('message', '')
        model_ids = data.get('models', [])
        
        if not message or not model_ids:
            return jsonify({
                'error': 'Message and models are required',
                'status': 'error'
            }), 400
        
        results = []
        
        for model_id in model_ids:
            try:
                start_time = time.time()
                
                # Create chat completion
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant. Provide clear, accurate responses."},
                        {"role": "user", "content": message}
                    ],
                    model=model_id,
                    temperature=0.7,
                    max_tokens=get_max_tokens_for_model(model_id)
                )
                
                response_time = time.time() - start_time
                response = chat_completion.choices[0].message.content
                
                results.append({
                    'model': model_id,
                    'response': response,
                    'response_time': round(response_time, 2),
                    'status': 'success'
                })
                
            except Exception as model_error:
                results.append({
                    'model': model_id,
                    'error': str(model_error),
                    'status': 'error'
                })
        
        # Save comparison for analytics
        comparison = {
            'id': hashlib.md5(f"{time.time()}".encode()).hexdigest(),
            'message': message,
            'models': model_ids,
            'results': results,
            'created': datetime.now().isoformat()
        }
        model_comparisons.append(comparison)
        
        return jsonify({
            'comparison': comparison,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get usage analytics"""
    try:
        session_id = get_session_id()
        user_conversations = conversations.get(session_id, [])
        
        # Calculate analytics
        total_conversations = len(user_conversations)
        total_messages = sum(len(conv.get('messages', [])) for conv in user_conversations)
        
        # Model usage
        model_usage = defaultdict(int)
        for conv in user_conversations:
            if conv.get('model'):
                model_usage[conv['model']] += 1
        
        # Template usage
        template_usage = sorted(templates_db, key=lambda x: x.get('usage_count', 0), reverse=True)[:5]
        
        analytics = {
            'conversations': {
                'total': total_conversations,
                'total_messages': total_messages,
                'avg_messages_per_conversation': round(total_messages / max(total_conversations, 1), 1)
            },
            'models': {
                'usage': dict(model_usage),
                'most_used': max(model_usage.items(), key=lambda x: x[1])[0] if model_usage else None
            },
            'templates': {
                'total': len(templates_db),
                'most_used': template_usage
            },
            'comparisons': {
                'total': len(model_comparisons)
            }
        }
        
        return jsonify({
            'analytics': analytics,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

# === RAG API ENDPOINTS ===

@app.route('/api/rag/upload', methods=['POST'])
def upload_document():
    """Upload a document to the RAG system"""
    try:
        if not RAG_AVAILABLE or not rag_system:
            return jsonify({
                'error': 'RAG system not available',
                'status': 'error'
            }), 503
        
        data = request.get_json()
        content = data.get('content', '')
        metadata = data.get('metadata', {})
        
        if not content:
            return jsonify({
                'error': 'No content provided',
                'status': 'error'
            }), 400
        
        doc_id = rag_system.add_document(content, metadata)
        
        if doc_id:
            return jsonify({
                'document_id': doc_id,
                'message': 'Document added successfully',
                'status': 'success'
            })
        else:
            return jsonify({
                'error': 'Failed to add document',
                'status': 'error'
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/rag/search', methods=['POST'])
def search_documents():
    """Search documents in the RAG system"""
    try:
        if not RAG_AVAILABLE or not rag_system:
            return jsonify({
                'error': 'RAG system not available',
                'status': 'error'
            }), 503
        
        data = request.get_json()
        query = data.get('query', '')
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({
                'error': 'No query provided',
                'status': 'error'
            }), 400
        
        results = rag_system.search_documents(query, limit)
        
        return jsonify({
            'results': results,
            'query': query,
            'count': len(results),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/rag/stats', methods=['GET'])
def get_rag_stats():
    """Get RAG system statistics"""
    try:
        if not RAG_AVAILABLE or not rag_system:
            return jsonify({
                'error': 'RAG system not available',
                'status': 'error'
            }), 503
        
        stats = rag_system.get_stats()
        
        return jsonify({
            'stats': stats,
            'available': True,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/features', methods=['GET'])
def get_available_features():
    """Get information about available features"""
    return jsonify({
        'features': {
            'rag': {
                'available': RAG_AVAILABLE,
                'description': 'Retrieval-Augmented Generation for knowledge-enhanced responses'
            },
            'lora': {
                'available': LORA_AVAILABLE,
                'description': 'Low-Rank Adaptation for model fine-tuning'
            },
            'groq': {
                'available': client is not None,
                'description': 'Groq API for fast inference'
            }
        },
        'status': 'success'
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'running',
        'rag_available': RAG_AVAILABLE,
        'lora_available': LORA_AVAILABLE,
        'groq_available': client is not None,
        'timestamp': datetime.now().isoformat()
    })

# Initialize with some default templates
if not templates_db:
    default_templates = [
        {
            'id': 'template_1',
            'title': 'Code Review',
            'content': 'Please review this code and provide feedback on:\n1. Code quality and best practices\n2. Potential bugs or issues\n3. Performance improvements\n4. Security considerations\n\nCode:\n```\n[PASTE YOUR CODE HERE]\n```',
            'category': 'coding',
            'tags': ['code', 'review', 'programming'],
            'created': datetime.now().isoformat(),
            'usage_count': 0
        },
        {
            'id': 'template_2',
            'title': 'Explain Concept',
            'content': 'Please explain [CONCEPT] in simple terms:\n1. What is it?\n2. How does it work?\n3. Why is it important?\n4. Can you provide a practical example?',
            'category': 'education',
            'tags': ['explain', 'concept', 'learning'],
            'created': datetime.now().isoformat(),
            'usage_count': 0
        },
        {
            'id': 'template_3',
            'title': 'Creative Writing',
            'content': 'Write a creative story with the following elements:\n- Setting: [SETTING]\n- Main character: [CHARACTER]\n- Conflict: [CONFLICT]\n- Tone: [TONE]\n\nMake it engaging and approximately [LENGTH] words.',
            'category': 'creative',
            'tags': ['writing', 'story', 'creative'],
            'created': datetime.now().isoformat(),
            'usage_count': 0
        },
        {
            'id': 'template_4',
            'title': 'Problem Solving',
            'content': 'Help me solve this problem step by step:\n\nProblem: [DESCRIBE YOUR PROBLEM]\n\nPlease provide:\n1. Analysis of the problem\n2. Possible solutions\n3. Pros and cons of each solution\n4. Your recommended approach',
            'category': 'problem-solving',
            'tags': ['problem', 'solution', 'analysis'],
            'created': datetime.now().isoformat(),
            'usage_count': 0
        }
    ]
    templates_db.extend(default_templates)

@app.route('/api/models/recommend', methods=['POST'])
def recommend_model():
    """Recommend the best model for a given input"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        has_image = data.get('has_image', False)
        
        recommended_model = select_best_model(message, has_image)
        complexity_score = analyze_message_complexity(message)
        
        return jsonify({
            'recommended_model': recommended_model,
            'complexity_score': complexity_score,
            'reasoning': get_recommendation_reasoning(message, has_image, complexity_score),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

def get_recommendation_reasoning(message, has_image, complexity_score):
    """Explain why a particular model was recommended"""
    reasons = []
    
    if has_image:
        reasons.append("Vision model selected for image analysis")
    
    if complexity_score >= 7:
        reasons.append("High complexity detected - using powerful model")
    elif complexity_score >= 4:
        reasons.append("Medium complexity - using balanced model")
    else:
        reasons.append("Simple task - using fast model for quick response")
    
    message_lower = message.lower() if message else ""
    
    if any(keyword in message_lower for keyword in ['code', 'programming', 'debug']):
        reasons.append("Coding task detected")
    
    if any(keyword in message_lower for keyword in ['analyze', 'calculate', 'solve']):
        reasons.append("Analytical task detected")
    
    if any(keyword in message_lower for keyword in ['story', 'creative', 'write']):
        reasons.append("Creative writing task detected")
    
    return reasons

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))  # Changed to 5001 to avoid AirPlay conflict
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting AI Assistant on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🌐 Access at: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

# === NEW FEATURES API ENDPOINTS ===

# Import database system
try:
    from database import get_database, initialize_database
    DB_AVAILABLE = initialize_database()
except ImportError:
    print("❌ Database system not available")
    DB_AVAILABLE = False

@app.route('/api/users', methods=['POST'])
def create_or_update_user():
    """Create or update user profile"""
    try:
        if not DB_AVAILABLE:
            return jsonify({'error': 'Database not available', 'status': 'error'}), 503
        
        data = request.get_json()
        db = get_database()
        
        user_id = db.create_user(data)
        user_data = db.get_user(user_id)
        
        return jsonify({
            'user': user_data,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Get user profile"""
    try:
        if not DB_AVAILABLE:
            return jsonify({'error': 'Database not available', 'status': 'error'}), 503
        
        db = get_database()
        user_data = db.get_user(user_id)
        
        if not user_data:
            return jsonify({'error': 'User not found', 'status': 'error'}), 404
        
        return jsonify({
            'user': user_data,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user_profile(user_id):
    """Update user profile"""
    try:
        if not DB_AVAILABLE:
            return jsonify({'error': 'Database not available', 'status': 'error'}), 503
        
        data = request.get_json()
        db = get_database()
        
        success = db.update_user(user_id, data)
        
        if success:
            user_data = db.get_user(user_id)
            return jsonify({
                'user': user_data,
                'status': 'success'
            })
        else:
            return jsonify({'error': 'User not found', 'status': 'error'}), 404
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/search', methods=['POST'])
def global_search():
    """Global search across conversations, documents, templates"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        filters = data.get('filters', {})
        user_id = data.get('user_id')
        
        if not query:
            return jsonify({'error': 'Query required', 'status': 'error'}), 400
        
        results = []
        
        # Search conversations
        if filters.get('conversations', True):
            if DB_AVAILABLE:
                db = get_database()
                conversations = db.get_conversations(user_id)
                
                for conv in conversations:
                    messages = db.get_conversation_messages(conv['id'])
                    for i, message in enumerate(messages):
                        if query.lower() in message['content'].lower():
                            results.append({
                                'id': f"conversation_{conv['id']}_{i}",
                                'type': 'conversation',
                                'title': f"Message in {conv['title']}",
                                'content': message['content'],
                                'conversationId': conv['id'],
                                'messageIndex': i,
                                'timestamp': message['timestamp'],
                                'score': message['content'].lower().count(query.lower())
                            })
        
        # Search documents
        if filters.get('documents', True) and DB_AVAILABLE:
            db = get_database()
            documents = db.get_documents(user_id)
            
            for doc in documents:
                if query.lower() in doc['content'].lower() or query.lower() in doc['title'].lower():
                    results.append({
                        'id': f"document_{doc['id']}",
                        'type': 'document',
                        'title': doc['title'],
                        'content': doc['content'],
                        'timestamp': doc['created_at'],
                        'score': (doc['title'].lower().count(query.lower()) * 2 + 
                                doc['content'].lower().count(query.lower()))
                    })
        
        # Search templates
        if filters.get('templates', True):
            for template in templates_db:
                if (query.lower() in template['content'].lower() or 
                    query.lower() in template['title'].lower()):
                    results.append({
                        'id': f"template_{template['id']}",
                        'type': 'template',
                        'title': template['title'],
                        'content': template['content'],
                        'timestamp': template['created'],
                        'score': (template['title'].lower().count(query.lower()) * 2 + 
                                template['content'].lower().count(query.lower()))
                    })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Save search if database available
        if DB_AVAILABLE and user_id:
            db = get_database()
            db.save_search(user_id, query, len(results))
        
        return jsonify({
            'results': results[:20],  # Limit to 20 results
            'total': len(results),
            'query': query,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/search/history/<user_id>', methods=['GET'])
def get_search_history(user_id):
    """Get search history for user"""
    try:
        if not DB_AVAILABLE:
            return jsonify({'history': [], 'status': 'success'})
        
        db = get_database()
        history = db.get_search_history(user_id)
        
        return jsonify({
            'history': history,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/analytics/<user_id>', methods=['GET'])
def get_user_analytics(user_id):
    """Get analytics for user"""
    try:
        if not DB_AVAILABLE:
            # Return mock data if database not available
            return jsonify({
                'analytics': {
                    'total_messages': 0,
                    'total_conversations': 0,
                    'avg_response_time': 0,
                    'popular_models': {},
                    'events_by_type': {}
                },
                'status': 'success'
            })
        
        db = get_database()
        days = request.args.get('days', 30, type=int)
        analytics = db.get_analytics(user_id, days)
        
        return jsonify({
            'analytics': analytics,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/analytics/log', methods=['POST'])
def log_analytics_event():
    """Log analytics event"""
    try:
        if not DB_AVAILABLE:
            return jsonify({'status': 'success'})  # Silently ignore if DB not available
        
        data = request.get_json()
        db = get_database()
        db.log_analytics(data)
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/export/<user_id>', methods=['GET'])
def export_user_data(user_id):
    """Export all user data"""
    try:
        export_data = {
            'user_id': user_id,
            'export_date': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        if DB_AVAILABLE:
            db = get_database()
            
            # Export user profile
            user_data = db.get_user(user_id)
            if user_data:
                export_data['profile'] = user_data
            
            # Export conversations
            conversations = db.get_conversations(user_id)
            export_data['conversations'] = []
            
            for conv in conversations:
                messages = db.get_conversation_messages(conv['id'])
                export_data['conversations'].append({
                    **conv,
                    'messages': messages
                })
            
            # Export documents
            documents = db.get_documents(user_id)
            export_data['documents'] = documents
            
            # Export search history
            search_history = db.get_search_history(user_id)
            export_data['search_history'] = search_history
            
            # Export analytics
            analytics = db.get_analytics(user_id, 365)  # Last year
            export_data['analytics'] = analytics
        
        return jsonify({
            'data': export_data,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/system/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics"""
    try:
        stats = {
            'timestamp': datetime.now().isoformat(),
            'features': {
                'rag_available': RAG_AVAILABLE,
                'lora_available': LORA_AVAILABLE,
                'database_available': DB_AVAILABLE
            }
        }
        
        if DB_AVAILABLE:
            db = get_database()
            db_stats = db.get_database_stats()
            stats['database'] = db_stats
        
        # Add RAG stats
        if RAG_AVAILABLE and rag_system:
            try:
                rag_stats = rag_system.get_stats()
                stats['rag'] = rag_stats
            except:
                pass
        
        # Add LoRA stats
        if LORA_AVAILABLE and lora_system:
            try:
                lora_stats = lora_system.get_stats()
                stats['lora'] = lora_stats
            except:
                pass
        
        return jsonify({
            'stats': stats,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/share', methods=['POST'])
def handle_share():
    """Handle PWA share target"""
    try:
        # Handle shared content from PWA
        title = request.form.get('title', '')
        text = request.form.get('text', '')
        url = request.form.get('url', '')
        
        # Process shared files
        files = request.files.getlist('files')
        
        shared_content = []
        
        if title:
            shared_content.append(f"Title: {title}")
        if text:
            shared_content.append(f"Text: {text}")
        if url:
            shared_content.append(f"URL: {url}")
        
        for file in files:
            if file.filename:
                # Process shared file
                content = file.read().decode('utf-8', errors='ignore')
                shared_content.append(f"File ({file.filename}): {content[:500]}...")
        
        # Create a new conversation with shared content
        shared_message = "Shared content:\n\n" + "\n\n".join(shared_content)
        
        # Redirect to main app with shared content
        return f'''
        <script>
            window.opener.postMessage({{
                type: 'shared_content',
                content: {json.dumps(shared_message)}
            }}, '*');
            window.close();
        </script>
        '''
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

# Enhanced chat functionality now handled by modular system