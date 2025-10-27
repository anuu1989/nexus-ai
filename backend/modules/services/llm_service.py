"""
LLM Service Module
=================
Simplified LLM provider management
"""

import time
import logging
from typing import Dict, List, Any, Optional
from ..core.config import get_ai_config

logger = logging.getLogger(__name__)

class LLMService:
    """Simplified LLM service"""
    
    def __init__(self):
        self.config = get_ai_config()
        self.providers = {}
        self.initialize_providers()
    
    def initialize_providers(self):
        """Initialize available LLM providers"""
        logger.info("🔄 Initializing LLM providers...")
        
        # Initialize Groq
        if self.config.GROQ_API_KEY:
            try:
                from groq import Groq
                self.providers['groq'] = Groq(api_key=self.config.GROQ_API_KEY)
                logger.info("✅ Groq provider initialized")
            except Exception as e:
                logger.error(f"❌ Groq initialization failed: {e}")
        
        # Initialize OpenAI
        if self.config.OPENAI_API_KEY:
            try:
                import openai
                self.providers['openai'] = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)
                logger.info("✅ OpenAI provider initialized")
            except Exception as e:
                logger.error(f"❌ OpenAI initialization failed: {e}")
        
        # Initialize Ollama
        try:
            import requests
            response = requests.get(f"{self.config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                self.providers['ollama'] = {"base_url": self.config.OLLAMA_BASE_URL}
                logger.info("✅ Ollama provider initialized")
        except Exception as e:
            logger.warning(f"⚠️ Ollama not available: {e}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available models from all providers"""
        models = []
        
        # Groq models
        if 'groq' in self.providers:
            try:
                groq_models = self.providers['groq'].models.list()
                for model in groq_models.data:
                    models.append({
                        "id": model.id,
                        "name": model.id,
                        "provider": "groq",
                        "provider_name": "Groq"
                    })
            except Exception as e:
                logger.error(f"Failed to fetch Groq models: {e}")
        
        # OpenAI models
        if 'openai' in self.providers:
            try:
                openai_models = self.providers['openai'].models.list()
                for model in openai_models.data:
                    if 'gpt' in model.id.lower():
                        models.append({
                            "id": model.id,
                            "name": model.id,
                            "provider": "openai",
                            "provider_name": "OpenAI"
                        })
            except Exception as e:
                logger.error(f"Failed to fetch OpenAI models: {e}")
        
        return models
    
    def chat_completion(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Send chat completion request"""
        start_time = time.time()
        
        # Determine provider from model
        provider = self._get_provider_for_model(model)
        if not provider:
            raise ValueError(f"No provider available for model: {model}")
        
        try:
            if provider == 'groq':
                response = self.providers['groq'].chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
                return {
                    "response": response.choices[0].message.content,
                    "model_used": model,
                    "provider_used": "groq",
                    "response_time": time.time() - start_time
                }
            
            elif provider == 'openai':
                response = self.providers['openai'].chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
                return {
                    "response": response.choices[0].message.content,
                    "model_used": model,
                    "provider_used": "openai",
                    "response_time": time.time() - start_time
                }
            
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise e
    
    def _get_provider_for_model(self, model: str) -> Optional[str]:
        """Determine provider for a given model"""
        if model.startswith('gpt'):
            return 'openai' if 'openai' in self.providers else None
        else:
            return 'groq' if 'groq' in self.providers else None

# Global LLM service instance
llm_service = LLMService()

def get_llm_service() -> LLMService:
    """Get LLM service instance"""
    return llm_service