"""
Helper Functions
===============
Utility functions for NexusAI application
"""

import re
import time
import hashlib
from flask import session


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
    limit = model_limits.get(model_name, 256)
    
    # Safety check: never exceed 512 tokens to avoid API errors
    return min(limit, 512)


def apply_ai_guardrails(message):
    """Apply AI guardrails to filter unsafe content"""
    
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


def select_best_model(message, has_image, preferred_model=None, client=None):
    """Intelligently select the best model based on input characteristics"""
    try:
        if client is None:
            return get_default_model(has_image)
            
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


def get_default_model(needs_vision=False, client=None):
    """Get the default model based on requirements"""
    try:
        if client is None:
            return 'meta-llama/llama-4-maverick-17b-128e-instruct' if needs_vision else 'llama-3.1-8b-instant'
            
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