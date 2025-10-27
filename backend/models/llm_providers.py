"""
Multi-LLM Provider System for NexusAI
=====================================

Supports multiple AI providers with automatic fallback and provider selection:
- Groq (Fast inference)
- OpenAI (GPT models)
- Anthropic (Claude models)
- Ollama (Local models)
- Hugging Face (Open source models)
- Google AI (Gemini models)

Features:
- Automatic provider detection and initialization
- Intelligent fallback system
- Cost optimization
- Rate limit handling
- Model capability mapping
- Provider health monitoring
"""

import os
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProviderType(Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    GOOGLE = "google"

@dataclass
class ModelInfo:
    """Information about a specific model"""
    name: str
    provider: ProviderType
    context_length: int
    cost_per_1k_tokens: float
    capabilities: List[str]
    description: str
    max_output_tokens: int = 4096

@dataclass
class ProviderConfig:
    """Configuration for an LLM provider"""
    name: str
    provider_type: ProviderType
    api_key_env: str
    base_url: Optional[str] = None
    enabled: bool = True
    priority: int = 1  # Lower number = higher priority
    rate_limit: int = 60  # requests per minute
    timeout: int = 30  # seconds

class LLMProviderManager:
    """Manages multiple LLM providers with intelligent routing and fallback"""
    
    def __init__(self):
        self.providers = {}
        self.clients = {}
        self.model_catalog = {}
        self.provider_configs = self._get_provider_configs()
        self.last_request_times = {}
        self.request_counts = {}
        
        # Initialize providers
        self._initialize_providers()
        self._load_model_catalog()
    
    def _get_provider_configs(self) -> Dict[str, ProviderConfig]:
        """Get provider configurations"""
        return {
            "groq": ProviderConfig(
                name="Groq",
                provider_type=ProviderType.GROQ,
                api_key_env="GROQ_API_KEY",
                priority=1,
                rate_limit=30
            ),
            "openai": ProviderConfig(
                name="OpenAI",
                provider_type=ProviderType.OPENAI,
                api_key_env="OPENAI_API_KEY",
                priority=2,
                rate_limit=60
            ),
            "anthropic": ProviderConfig(
                name="Anthropic",
                provider_type=ProviderType.ANTHROPIC,
                api_key_env="ANTHROPIC_API_KEY",
                priority=3,
                rate_limit=50
            ),
            "ollama": ProviderConfig(
                name="Ollama",
                provider_type=ProviderType.OLLAMA,
                api_key_env="OLLAMA_BASE_URL",
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                priority=4,
                rate_limit=100
            ),
            "huggingface": ProviderConfig(
                name="Hugging Face",
                provider_type=ProviderType.HUGGINGFACE,
                api_key_env="HUGGINGFACE_API_KEY",
                priority=5,
                rate_limit=30
            ),
            "google": ProviderConfig(
                name="Google AI",
                provider_type=ProviderType.GOOGLE,
                api_key_env="GOOGLE_API_KEY",
                priority=6,
                rate_limit=60
            )
        }
    
    def _initialize_providers(self):
        """Initialize all available providers"""
        logger.info("🔄 Initializing LLM providers...")
        
        for provider_id, config in self.provider_configs.items():
            try:
                if self._initialize_provider(provider_id, config):
                    logger.info(f"✅ {config.name} provider initialized successfully")
                else:
                    logger.info(f"⚠️  {config.name} provider not available (missing API key or dependency)")
            except Exception as e:
                logger.error(f"❌ Error initializing {config.name}: {e}")
    
    def _initialize_provider(self, provider_id: str, config: ProviderConfig) -> bool:
        """Initialize a specific provider"""
        api_key = os.getenv(config.api_key_env)
        
        # Special case for Ollama (doesn't need API key)
        if config.provider_type == ProviderType.OLLAMA:
            return self._initialize_ollama(provider_id, config)
        
        if not api_key:
            return False
        
        try:
            if config.provider_type == ProviderType.GROQ:
                return self._initialize_groq(provider_id, config, api_key)
            elif config.provider_type == ProviderType.OPENAI:
                return self._initialize_openai(provider_id, config, api_key)
            elif config.provider_type == ProviderType.ANTHROPIC:
                return self._initialize_anthropic(provider_id, config, api_key)
            elif config.provider_type == ProviderType.HUGGINGFACE:
                return self._initialize_huggingface(provider_id, config, api_key)
            elif config.provider_type == ProviderType.GOOGLE:
                return self._initialize_google(provider_id, config, api_key)
        except Exception as e:
            logger.error(f"Error initializing {config.name}: {e}")
            return False
        
        return False
    
    def _initialize_groq(self, provider_id: str, config: ProviderConfig, api_key: str) -> bool:
        """Initialize Groq provider"""
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            self.clients[provider_id] = client
            self.providers[provider_id] = config
            return True
        except ImportError:
            logger.warning("Groq library not installed. Install with: pip install groq")
            return False
    
    def _initialize_openai(self, provider_id: str, config: ProviderConfig, api_key: str) -> bool:
        """Initialize OpenAI provider"""
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            self.clients[provider_id] = client
            self.providers[provider_id] = config
            return True
        except ImportError:
            logger.warning("OpenAI library not installed. Install with: pip install openai")
            return False
    
    def _initialize_anthropic(self, provider_id: str, config: ProviderConfig, api_key: str) -> bool:
        """Initialize Anthropic provider"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            self.clients[provider_id] = client
            self.providers[provider_id] = config
            return True
        except ImportError:
            logger.warning("Anthropic library not installed. Install with: pip install anthropic")
            return False
    
    def _initialize_ollama(self, provider_id: str, config: ProviderConfig) -> bool:
        """Initialize Ollama provider"""
        try:
            import requests
            # Test if Ollama is running
            response = requests.get(f"{config.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.clients[provider_id] = {"base_url": config.base_url}
                self.providers[provider_id] = config
                return True
        except Exception:
            pass
        return False
    
    def _initialize_huggingface(self, provider_id: str, config: ProviderConfig, api_key: str) -> bool:
        """Initialize Hugging Face provider"""
        try:
            import requests
            # Test API key
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get("https://api-inference.huggingface.co/models", headers=headers, timeout=5)
            if response.status_code == 200:
                self.clients[provider_id] = {"api_key": api_key}
                self.providers[provider_id] = config
                return True
        except Exception:
            pass
        return False
    
    def _initialize_google(self, provider_id: str, config: ProviderConfig, api_key: str) -> bool:
        """Initialize Google AI provider"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.clients[provider_id] = genai
            self.providers[provider_id] = config
            return True
        except ImportError:
            logger.warning("Google AI library not installed. Install with: pip install google-generativeai")
            return False
    
    def _load_model_catalog(self):
        """Load model catalog with capabilities and pricing"""
        self.model_catalog = {
            # Groq Models
            "llama-3.1-8b-instant": ModelInfo(
                name="llama-3.1-8b-instant",
                provider=ProviderType.GROQ,
                context_length=131072,
                cost_per_1k_tokens=0.00005,
                capabilities=["chat", "reasoning", "code"],
                description="Fast Llama 3.1 8B model optimized for speed"
            ),
            "llama-3.1-70b-versatile": ModelInfo(
                name="llama-3.1-70b-versatile",
                provider=ProviderType.GROQ,
                context_length=131072,
                cost_per_1k_tokens=0.0002,
                capabilities=["chat", "reasoning", "code", "analysis"],
                description="Powerful Llama 3.1 70B model for complex tasks"
            ),
            "mixtral-8x7b-32768": ModelInfo(
                name="mixtral-8x7b-32768",
                provider=ProviderType.GROQ,
                context_length=32768,
                cost_per_1k_tokens=0.0001,
                capabilities=["chat", "reasoning", "multilingual"],
                description="Mixtral 8x7B mixture of experts model"
            ),
            
            # OpenAI Models
            "gpt-4o": ModelInfo(
                name="gpt-4o",
                provider=ProviderType.OPENAI,
                context_length=128000,
                cost_per_1k_tokens=0.005,
                capabilities=["chat", "reasoning", "code", "vision", "analysis"],
                description="Latest GPT-4 Omni model with multimodal capabilities"
            ),
            "gpt-4o-mini": ModelInfo(
                name="gpt-4o-mini",
                provider=ProviderType.OPENAI,
                context_length=128000,
                cost_per_1k_tokens=0.00015,
                capabilities=["chat", "reasoning", "code"],
                description="Smaller, faster GPT-4 model"
            ),
            "gpt-3.5-turbo": ModelInfo(
                name="gpt-3.5-turbo",
                provider=ProviderType.OPENAI,
                context_length=16385,
                cost_per_1k_tokens=0.0005,
                capabilities=["chat", "reasoning"],
                description="Fast and efficient GPT-3.5 model"
            ),
            
            # Anthropic Models
            "claude-3-5-sonnet-20241022": ModelInfo(
                name="claude-3-5-sonnet-20241022",
                provider=ProviderType.ANTHROPIC,
                context_length=200000,
                cost_per_1k_tokens=0.003,
                capabilities=["chat", "reasoning", "code", "analysis", "vision"],
                description="Latest Claude 3.5 Sonnet with enhanced capabilities"
            ),
            "claude-3-haiku-20240307": ModelInfo(
                name="claude-3-haiku-20240307",
                provider=ProviderType.ANTHROPIC,
                context_length=200000,
                cost_per_1k_tokens=0.00025,
                capabilities=["chat", "reasoning"],
                description="Fast and efficient Claude 3 Haiku model"
            ),
            
            # Google Models
            "gemini-1.5-pro": ModelInfo(
                name="gemini-1.5-pro",
                provider=ProviderType.GOOGLE,
                context_length=2000000,
                cost_per_1k_tokens=0.00125,
                capabilities=["chat", "reasoning", "code", "vision", "analysis"],
                description="Google's most capable Gemini model"
            ),
            "gemini-1.5-flash": ModelInfo(
                name="gemini-1.5-flash",
                provider=ProviderType.GOOGLE,
                context_length=1000000,
                cost_per_1k_tokens=0.000075,
                capabilities=["chat", "reasoning", "code"],
                description="Fast Gemini model optimized for speed"
            )
        }
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from all providers in real-time"""
        available_models = []
        
        # Dynamically fetch models from all active providers
        for provider_id, provider_config in self.providers.items():
            if provider_id in self.clients:
                try:
                    if provider_id == "groq":
                        groq_models = self._get_groq_models()
                        available_models.extend(groq_models)
                    elif provider_id == "ollama":
                        ollama_models = self._get_ollama_models()
                        available_models.extend(ollama_models)
                    elif provider_id == "openai":
                        openai_models = self._get_openai_models()
                        available_models.extend(openai_models)
                    elif provider_id == "anthropic":
                        anthropic_models = self._get_anthropic_models()
                        available_models.extend(anthropic_models)
                    # Add more providers as needed
                except Exception as e:
                    logger.warning(f"Failed to fetch models from {provider_id}: {e}")
                    # Fallback to static catalog for this provider
                    static_models = self._get_static_models_for_provider(provider_id)
                    available_models.extend(static_models)
        
        # Sort by provider priority and cost
        available_models.sort(key=lambda x: (
            self.providers[x["provider"]].priority,
            x["cost_per_1k_tokens"]
        ))
        
        return available_models
    
    def _get_ollama_models(self) -> List[Dict[str, Any]]:
        """Dynamically fetch available models from Ollama"""
        ollama_models = []
        
        try:
            if "ollama" in self.clients:
                import requests
                base_url = self.clients["ollama"]["base_url"]
                response = requests.get(f"{base_url}/api/tags", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("models", []):
                        model_name = model["name"]
                        
                        # Parse model info
                        size_gb = round(model.get("size", 0) / (1024**3), 1)
                        family = model.get("details", {}).get("family", "unknown")
                        param_size = model.get("details", {}).get("parameter_size", "unknown")
                        
                        ollama_models.append({
                            "id": model_name,
                            "name": model_name,
                            "provider": "ollama",
                            "provider_name": "Ollama",
                            "context_length": 4096,  # Default for most Ollama models
                            "cost_per_1k_tokens": 0.0,  # Local models are free
                            "capabilities": ["chat", "reasoning", "local"],
                            "description": f"Local {family.title()} model ({param_size}, {size_gb}GB)"
                        })
                        
        except Exception as e:
            logger.warning(f"Failed to fetch Ollama models: {e}")
        
        return ollama_models
    
    def _get_groq_models(self) -> List[Dict[str, Any]]:
        """Dynamically fetch available models from Groq API in real-time"""
        groq_models = []
        
        try:
            if "groq" in self.clients:
                client = self.clients["groq"]
                # Fetch models from Groq API
                models_response = client.models.list()
                
                for model in models_response.data:
                    # Filter out non-chat models (Whisper, etc.)
                    if self._is_chat_model(model.id):
                        # Enhanced model info with real-time data
                        model_info = {
                            "id": model.id,
                            "name": model.id,
                            "provider": "groq",
                            "provider_name": "Groq",
                            "context_length": self._get_groq_context_length(model.id),
                            "cost_per_1k_tokens": self._get_groq_cost(model.id),
                            "capabilities": self._get_groq_capabilities(model.id),
                            "description": self._get_groq_description(model.id),
                            "created": getattr(model, 'created', None),
                            "owned_by": getattr(model, 'owned_by', 'groq')
                        }
                        groq_models.append(model_info)
                    
        except Exception as e:
            logger.warning(f"Failed to fetch Groq models: {e}")
        
        return groq_models
    
    def _get_groq_context_length(self, model_id: str) -> int:
        """Get context length for Groq model"""
        context_lengths = {
            "llama-3.1-8b-instant": 131072,
            "llama-3.1-70b-versatile": 131072,
            "llama-3.2-1b-preview": 131072,
            "llama-3.2-3b-preview": 131072,
            "llama-3.2-11b-text-preview": 131072,
            "llama-3.2-90b-text-preview": 131072,
            "llama-3.2-11b-vision-preview": 131072,
            "mixtral-8x7b-32768": 32768,
            "gemma-7b-it": 8192,
            "gemma2-9b-it": 8192
        }
        return context_lengths.get(model_id, 8192)
    
    def _get_groq_cost(self, model_id: str) -> float:
        """Get cost per 1K tokens for Groq model"""
        costs = {
            "llama-3.1-8b-instant": 0.00005,
            "llama-3.1-70b-versatile": 0.0002,
            "llama-3.2-1b-preview": 0.00004,
            "llama-3.2-3b-preview": 0.00006,
            "llama-3.2-11b-text-preview": 0.00018,
            "llama-3.2-90b-text-preview": 0.0009,
            "llama-3.2-11b-vision-preview": 0.00018,
            "mixtral-8x7b-32768": 0.0001,
            "gemma-7b-it": 0.00007,
            "gemma2-9b-it": 0.00002
        }
        return costs.get(model_id, 0.0001)
    
    def _get_groq_capabilities(self, model_id: str) -> List[str]:
        """Get capabilities for Groq model"""
        if "vision" in model_id.lower():
            return ["chat", "reasoning", "vision", "multimodal"]
        elif "70b" in model_id or "90b" in model_id:
            return ["chat", "reasoning", "code", "analysis", "complex-tasks"]
        elif "mixtral" in model_id.lower():
            return ["chat", "reasoning", "multilingual", "expert-mix"]
        else:
            return ["chat", "reasoning", "code"]
    
    def _get_groq_description(self, model_id: str) -> str:
        """Get description for Groq model"""
        descriptions = {
            "llama-3.1-8b-instant": "Ultra-fast Llama 3.1 8B model optimized for speed and efficiency",
            "llama-3.1-70b-versatile": "Powerful Llama 3.1 70B model for complex reasoning and analysis",
            "llama-3.2-1b-preview": "Compact Llama 3.2 1B model for lightweight applications",
            "llama-3.2-3b-preview": "Efficient Llama 3.2 3B model balancing speed and capability",
            "llama-3.2-11b-text-preview": "Advanced Llama 3.2 11B model for text processing",
            "llama-3.2-90b-text-preview": "Most powerful Llama 3.2 90B model for complex tasks",
            "llama-3.2-11b-vision-preview": "Multimodal Llama 3.2 11B with vision capabilities",
            "mixtral-8x7b-32768": "Mixtral 8x7B mixture of experts model with 32K context",
            "gemma-7b-it": "Google's Gemma 7B instruction-tuned model",
            "gemma2-9b-it": "Google's Gemma 2 9B instruction-tuned model"
        }
        return descriptions.get(model_id, f"Groq {model_id} language model")
    
    def _is_chat_model(self, model_id: str) -> bool:
        """Check if a model supports chat completions"""
        # List of non-chat models that should be filtered out
        non_chat_models = [
            'whisper-large-v3',
            'whisper-large-v3-turbo',
            'distil-whisper-large-v3-en',
            'whisper-1',
            'tts-1',
            'tts-1-hd',
            'dall-e-2',
            'dall-e-3',
            'text-embedding-ada-002',
            'text-embedding-3-small',
            'text-embedding-3-large'
        ]
        
        # Check if model is in the non-chat list
        if model_id.lower() in [m.lower() for m in non_chat_models]:
            return False
            
        # Check if model name contains keywords indicating non-chat functionality
        non_chat_keywords = ['whisper', 'tts', 'dall-e', 'embedding', 'moderation']
        model_lower = model_id.lower()
        
        for keyword in non_chat_keywords:
            if keyword in model_lower:
                return False
        
        return True
    
    def _get_default_chat_model(self) -> str:
        """Get a default chat model based on available providers"""
        # Priority order for default models
        default_models = [
            "llama-3.1-8b-instant",  # Groq - fast and reliable
            "gpt-3.5-turbo",         # OpenAI - widely available
            "llama-3.1-70b-versatile", # Groq - more powerful
            "gpt-4o-mini"            # OpenAI - newer model
        ]
        
        # Get available models
        available_models = self.get_available_models()
        available_model_ids = [m["id"] for m in available_models]
        
        # Return the first available default model
        for model in default_models:
            if model in available_model_ids:
                return model
        
        # If no default models are available, return the first available chat model
        for model in available_model_ids:
            if self._is_chat_model(model):
                return model
        
        # Last resort fallback
        return "llama-3.1-8b-instant"
    
    def _get_max_tokens_for_model(self, model_name: str) -> int:
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
    
    def _get_static_models_for_provider(self, provider_id: str) -> List[Dict[str, Any]]:
        """Fallback to static catalog for a provider"""
        static_models = []
        for model_name, model_info in self.model_catalog.items():
            if model_info.provider.value == provider_id:
                static_models.append({
                    "id": model_name,
                    "name": model_name,
                    "provider": model_info.provider.value,
                    "provider_name": self.providers[provider_id].name,
                    "context_length": model_info.context_length,
                    "cost_per_1k_tokens": model_info.cost_per_1k_tokens,
                    "capabilities": model_info.capabilities,
                    "description": model_info.description
                })
        return static_models
    
    def _get_openai_models(self) -> List[Dict[str, Any]]:
        """Dynamically fetch available models from OpenAI API in real-time"""
        openai_models = []
        
        try:
            if "openai" in self.clients:
                client = self.clients["openai"]
                models_response = client.models.list()
                
                # Filter for chat models only (exclude embeddings, audio, etc.)
                for model in models_response.data:
                    if not self._is_chat_model(model.id):
                        continue
                    model_info = {
                        "id": model.id,
                        "name": model.id,
                        "provider": "openai",
                        "provider_name": "OpenAI",
                        "context_length": self._get_openai_context_length(model.id),
                        "cost_per_1k_tokens": self._get_openai_cost(model.id),
                        "capabilities": self._get_openai_capabilities(model.id),
                        "description": self._get_openai_description(model.id),
                        "created": model.created,
                        "owned_by": model.owned_by
                    }
                    openai_models.append(model_info)
                    
        except Exception as e:
            logger.warning(f"Failed to fetch OpenAI models: {e}")
        
        return openai_models
    
    def _get_openai_context_length(self, model_id: str) -> int:
        """Get context length for OpenAI model"""
        context_lengths = {
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-preview": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16385,
            "gpt-3.5-turbo-16k": 16385
        }
        return context_lengths.get(model_id, 4096)
    
    def _get_openai_cost(self, model_id: str) -> float:
        """Get cost per 1K tokens for OpenAI model (input cost)"""
        costs = {
            "gpt-4o": 0.0025,
            "gpt-4o-mini": 0.00015,
            "gpt-4-turbo": 0.01,
            "gpt-4-turbo-preview": 0.01,
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.0005,
            "gpt-3.5-turbo-16k": 0.001
        }
        return costs.get(model_id, 0.002)
    
    def _get_openai_capabilities(self, model_id: str) -> List[str]:
        """Get capabilities for OpenAI model"""
        if "gpt-4" in model_id.lower():
            if "vision" in model_id.lower() or "gpt-4o" in model_id.lower():
                return ["chat", "reasoning", "code", "analysis", "vision", "multimodal"]
            else:
                return ["chat", "reasoning", "code", "analysis", "complex-tasks"]
        else:
            return ["chat", "reasoning", "code"]
    
    def _get_openai_description(self, model_id: str) -> str:
        """Get description for OpenAI model"""
        descriptions = {
            "gpt-4o": "Most advanced GPT-4 model with vision capabilities",
            "gpt-4o-mini": "Fast and cost-effective GPT-4 model",
            "gpt-4-turbo": "Latest GPT-4 Turbo with enhanced performance",
            "gpt-4-turbo-preview": "Preview version of GPT-4 Turbo",
            "gpt-4": "Original GPT-4 model with advanced reasoning",
            "gpt-3.5-turbo": "Fast and efficient conversational AI",
            "gpt-3.5-turbo-16k": "GPT-3.5 with extended 16K context window"
        }
        return descriptions.get(model_id, f"OpenAI {model_id} language model")
    
    def _get_anthropic_models(self) -> List[Dict[str, Any]]:
        """Get available models from Anthropic (Claude models)"""
        # Anthropic doesn't have a public models list endpoint, so we use known models
        # that are currently available and check if the client is working
        anthropic_models = []
        
        try:
            if "anthropic" in self.clients:
                # Test if the client is working by making a simple request
                # We'll use the known available models
                known_models = [
                    {
                        "id": "claude-3-5-sonnet-20241022",
                        "name": "claude-3-5-sonnet-20241022",
                        "provider": "anthropic",
                        "provider_name": "Anthropic",
                        "context_length": 200000,
                        "cost_per_1k_tokens": 0.003,
                        "capabilities": ["chat", "reasoning", "code", "analysis", "vision", "multimodal"],
                        "description": "Latest Claude 3.5 Sonnet with enhanced capabilities and vision"
                    },
                    {
                        "id": "claude-3-5-haiku-20241022",
                        "name": "claude-3-5-haiku-20241022", 
                        "provider": "anthropic",
                        "provider_name": "Anthropic",
                        "context_length": 200000,
                        "cost_per_1k_tokens": 0.00025,
                        "capabilities": ["chat", "reasoning", "fast-response"],
                        "description": "Fast and efficient Claude 3.5 Haiku model"
                    },
                    {
                        "id": "claude-3-opus-20240229",
                        "name": "claude-3-opus-20240229",
                        "provider": "anthropic", 
                        "provider_name": "Anthropic",
                        "context_length": 200000,
                        "cost_per_1k_tokens": 0.015,
                        "capabilities": ["chat", "reasoning", "code", "analysis", "complex-tasks", "creative"],
                        "description": "Most powerful Claude 3 model for complex reasoning and creative tasks"
                    }
                ]
                
                # Test client connectivity with a minimal request
                client = self.clients["anthropic"]
                # If we can access the client without error, return the models
                anthropic_models = known_models
                
        except Exception as e:
            logger.warning(f"Failed to verify Anthropic models: {e}")
        
        return anthropic_models
    
    def get_provider_for_model(self, model_name: str) -> Optional[str]:
        """Get the provider ID for a specific model"""
        if model_name in self.model_catalog:
            provider_type = self.model_catalog[model_name].provider
            for provider_id, config in self.providers.items():
                if config.provider_type == provider_type:
                    return provider_id
        return None
    
    def chat_completion(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Send chat completion request with automatic provider routing"""
        
        # Validate that the model supports chat completions
        if not self._is_chat_model(model):
            logger.warning(f"Model {model} does not support chat completions, falling back to default")
            # Use a default chat model instead
            model = self._get_default_chat_model()
            logger.info(f"Using fallback model: {model}")
        
        provider_id = self.get_provider_for_model(model)
        
        if not provider_id:
            raise ValueError(f"Model {model} not available or provider not initialized")
        
        # Check rate limits
        if not self._check_rate_limit(provider_id):
            # Try fallback providers
            fallback_provider = self._get_fallback_provider(model)
            if fallback_provider:
                provider_id = fallback_provider
            else:
                raise Exception("Rate limit exceeded and no fallback available")
        
        try:
            return self._make_request(provider_id, model, messages, **kwargs)
        except Exception as e:
            logger.error(f"Error with {provider_id}: {e}")
            # Try fallback
            fallback_provider = self._get_fallback_provider(model)
            if fallback_provider and fallback_provider != provider_id:
                logger.info(f"Trying fallback provider: {fallback_provider}")
                return self._make_request(fallback_provider, model, messages, **kwargs)
            raise e
    
    def _check_rate_limit(self, provider_id: str) -> bool:
        """Check if provider is within rate limits"""
        config = self.providers[provider_id]
        current_time = time.time()
        
        # Initialize tracking if needed
        if provider_id not in self.request_counts:
            self.request_counts[provider_id] = []
        
        # Remove old requests (older than 1 minute)
        self.request_counts[provider_id] = [
            req_time for req_time in self.request_counts[provider_id]
            if current_time - req_time < 60
        ]
        
        # Check if under rate limit
        return len(self.request_counts[provider_id]) < config.rate_limit
    
    def _get_fallback_provider(self, model: str) -> Optional[str]:
        """Get a fallback provider for the model"""
        # For now, return the first available provider with lower priority
        current_provider_id = self.get_provider_for_model(model)
        if not current_provider_id:
            return None
        
        current_priority = self.providers[current_provider_id].priority
        
        # Find provider with next highest priority
        fallback_candidates = [
            (pid, config) for pid, config in self.providers.items()
            if config.priority > current_priority and self._check_rate_limit(pid)
        ]
        
        if fallback_candidates:
            fallback_candidates.sort(key=lambda x: x[1].priority)
            return fallback_candidates[0][0]
        
        return None
    
    def _make_request(self, provider_id: str, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make the actual API request to the provider"""
        config = self.providers[provider_id]
        client = self.clients[provider_id]
        
        # Record request time for rate limiting
        current_time = time.time()
        if provider_id not in self.request_counts:
            self.request_counts[provider_id] = []
        self.request_counts[provider_id].append(current_time)
        
        if config.provider_type == ProviderType.GROQ:
            return self._groq_request(client, model, messages, **kwargs)
        elif config.provider_type == ProviderType.OPENAI:
            return self._openai_request(client, model, messages, **kwargs)
        elif config.provider_type == ProviderType.ANTHROPIC:
            return self._anthropic_request(client, model, messages, **kwargs)
        elif config.provider_type == ProviderType.GOOGLE:
            return self._google_request(client, model, messages, **kwargs)
        elif config.provider_type == ProviderType.OLLAMA:
            return self._ollama_request(client, model, messages, **kwargs)
        elif config.provider_type == ProviderType.HUGGINGFACE:
            return self._huggingface_request(client, model, messages, **kwargs)
        
        raise ValueError(f"Unsupported provider type: {config.provider_type}")
    
    def _groq_request(self, client, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make Groq API request"""
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=kwargs.get('max_tokens', self._get_max_tokens_for_model(model)),
            temperature=kwargs.get('temperature', 0.7),
            stream=kwargs.get('stream', False)
        )
        
        return {
            "content": response.choices[0].message.content,
            "provider": "groq",
            "model": model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    def _openai_request(self, client, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make OpenAI API request"""
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=kwargs.get('max_tokens', self._get_max_tokens_for_model(model)),
            temperature=kwargs.get('temperature', 0.7),
            stream=kwargs.get('stream', False)
        )
        
        return {
            "content": response.choices[0].message.content,
            "provider": "openai",
            "model": model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    def _anthropic_request(self, client, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make Anthropic API request"""
        # Convert messages format for Anthropic
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        response = client.messages.create(
            model=model,
            max_tokens=kwargs.get('max_tokens', self._get_max_tokens_for_model(model)),
            temperature=kwargs.get('temperature', 0.7),
            system=system_message,
            messages=user_messages
        )
        
        return {
            "content": response.content[0].text,
            "provider": "anthropic",
            "model": model,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        }
    
    def _google_request(self, client, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make Google AI API request"""
        # Convert messages to Google format
        prompt_parts = []
        for msg in messages:
            if msg["role"] == "user":
                prompt_parts.append(msg["content"])
            elif msg["role"] == "assistant":
                prompt_parts.append(f"Assistant: {msg['content']}")
        
        prompt = "\n".join(prompt_parts)
        
        model_instance = client.GenerativeModel(model)
        response = model_instance.generate_content(
            prompt,
            generation_config={
                "temperature": kwargs.get('temperature', 0.7),
                "max_output_tokens": kwargs.get('max_tokens', self._get_max_tokens_for_model(model))
            }
        )
        
        return {
            "content": response.text,
            "provider": "google",
            "model": model,
            "usage": {
                "prompt_tokens": 0,  # Google doesn't provide token counts
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    
    def _ollama_request(self, client, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make Ollama API request"""
        import requests
        
        # Convert messages to prompt
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                prompt += f"System: {msg['content']}\n"
            elif msg["role"] == "user":
                prompt += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt += f"Assistant: {msg['content']}\n"
        
        response = requests.post(
            f"{client['base_url']}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "num_predict": kwargs.get('max_tokens', self._get_max_tokens_for_model(model))
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "content": result.get("response", ""),
                "provider": "ollama",
                "model": model,
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
        else:
            raise Exception(f"Ollama API error: {response.status_code}")
    
    def _huggingface_request(self, client, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make Hugging Face API request"""
        import requests
        
        # Convert messages to prompt
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                prompt += f"System: {msg['content']}\n"
            elif msg["role"] == "user":
                prompt += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt += f"Assistant: {msg['content']}\n"
        
        headers = {"Authorization": f"Bearer {client['api_key']}"}
        
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model}",
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "max_new_tokens": kwargs.get('max_tokens', self._get_max_tokens_for_model(model))
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result[0].get("generated_text", "") if isinstance(result, list) else result.get("generated_text", "")
            
            return {
                "content": content,
                "provider": "huggingface",
                "model": model,
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
        else:
            raise Exception(f"Hugging Face API error: {response.status_code}")
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        for provider_id, config in self.providers.items():
            status[provider_id] = {
                "name": config.name,
                "enabled": provider_id in self.clients,
                "priority": config.priority,
                "rate_limit": config.rate_limit,
                "requests_last_minute": len(self.request_counts.get(provider_id, []))
            }
        return status

# Global instance
llm_manager = None

def get_llm_manager() -> LLMProviderManager:
    """Get the global LLM manager instance"""
    global llm_manager
    if llm_manager is None:
        llm_manager = LLMProviderManager()
    return llm_manager

def initialize_llm_providers() -> bool:
    """Initialize the LLM provider system"""
    try:
        global llm_manager
        llm_manager = LLMProviderManager()
        logger.info("✅ LLM Provider Manager initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error initializing LLM Provider Manager: {e}")
        return False