"""
Chat API Routes
==============
Chat-related API endpoints
"""

from flask import Blueprint, request, jsonify
from ..services.llm_service import get_llm_service
import logging

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat completion requests"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        model = data.get('model', 'llama-3.1-8b-instant')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Prepare messages for LLM
        messages = [{"role": "user", "content": message}]
        
        # Get LLM service and make request
        llm_service = get_llm_service()
        result = llm_service.chat_completion(model, messages)
        
        logger.info(f"✅ Chat completed - Model: {result['model_used']}, Time: {result['response_time']:.2f}s")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/api/models', methods=['GET'])
def get_models():
    """Get available models"""
    try:
        llm_service = get_llm_service()
        models = llm_service.get_available_models()
        return jsonify({"models": models})
    except Exception as e:
        logger.error(f"❌ Models fetch error: {e}")
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/api/models/refresh', methods=['POST'])
def refresh_models():
    """Refresh available models"""
    try:
        llm_service = get_llm_service()
        llm_service.initialize_providers()  # Re-initialize providers
        models = llm_service.get_available_models()
        return jsonify({"models": models, "message": "Models refreshed successfully"})
    except Exception as e:
        logger.error(f"❌ Models refresh error: {e}")
        return jsonify({"error": str(e)}), 500