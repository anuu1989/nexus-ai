"""
Chat API Routes
==============
Handles chat and model-related API endpoints
"""

from flask import Blueprint, request, jsonify
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import (
    apply_ai_guardrails, 
    select_best_model, 
    get_default_model,
    get_max_tokens_for_model,
    format_model_name,
    get_model_category_from_capabilities,
    get_model_speed_from_cost,
    get_model_description,
    get_model_category,
    get_model_speed,
    get_model_capabilities,
    get_fastest_model,
    get_smartest_model,
    get_coding_model,
    get_creative_model,
    get_fallback_models
)

def register_chat_routes(app, llm_manager=None, client=None, rag_system=None, lora_system=None):
    """Register chat-related routes"""
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        """Main chat endpoint with intelligent model selection and AI guardrails"""
        try:
            if client is None and llm_manager is None:
                return jsonify({
                    'error': 'No AI providers available. Please check your API keys.',
                    'status': 'error'
                }), 500
                
            data = request.get_json()
            user_message = data.get('message', '')
            image_data = data.get('image', None)
            selected_model = data.get('model', None)
            auto_select = data.get('auto_select', True)
            use_rag = data.get('use_rag', False)
            use_lora = data.get('use_lora', False)
            lora_adapter_id = data.get('lora_adapter_id', None)
            
            if not user_message and not image_data:
                return jsonify({
                    'error': 'No message or image provided',
                    'status': 'error'
                }), 400
            
            # Apply AI Guardrails to user message
            guardrails_result = apply_ai_guardrails(user_message)
            if guardrails_result['blocked']:
                return jsonify({
                    'response': f"⚠️ Message blocked by AI Guardrails: {guardrails_result['reason']}",
                    'blocked': True,
                    'guardrails': guardrails_result,
                    'status': 'blocked'
                }), 200
            
            # Record start time
            start_time = time.time()
            
            # Intelligent model selection
            if auto_select:
                model = select_best_model(user_message, image_data, selected_model)
                print(f"🤖 Auto-selected model: {model} (preferred: {selected_model})")
            else:
                model = selected_model or get_default_model(image_data is not None)
                print(f"🎯 Using user-selected model: {model}")
            
            # Check if selected model supports vision
            llama4_vision_models = ['meta-llama/llama-4-maverick-17b-128e-instruct', 'meta-llama/llama-4-scout-17b-16e-instruct']
            vision_keywords = ['vision', 'llava', 'multimodal', 'visual']
            supports_vision = (any(keyword in model.lower() for keyword in vision_keywords) or 
                              model in llama4_vision_models)
            
            # RAG Enhancement
            rag_context = ""
            relevant_chunks = []
            if use_rag and rag_system and user_message:
                try:
                    relevant_chunks = rag_system.retrieve_relevant_chunks(user_message, top_k=3)
                    if relevant_chunks:
                        rag_context = "\n\nRelevant context from knowledge base:\n"
                        for i, chunk in enumerate(relevant_chunks, 1):
                            rag_context += f"{i}. {chunk['content'][:500]}...\n"
                        print(f"✅ Retrieved {len(relevant_chunks)} relevant chunks for RAG")
                except Exception as e:
                    print(f"❌ RAG retrieval error: {e}")
            
            # LoRA Enhancement
            if use_lora and lora_system and lora_adapter_id:
                try:
                    # Generate response using LoRA adapter
                    lora_response = lora_system.generate_with_adapter(
                        user_message, 
                        lora_adapter_id, 
                        max_length=512
                    )
                    if lora_response:
                        return jsonify({
                            'response': lora_response,
                            'model_used': f'LoRA-{lora_adapter_id}',
                            'response_time': round(time.time() - start_time, 2),
                            'status': 'success',
                            'enhanced_with': 'lora'
                        })
                except Exception as e:
                    print(f"❌ LoRA generation error: {e}")
            
            # Build messages for API
            messages = []
            
            # Add system message with RAG context
            system_content = "You are a helpful AI assistant. Provide clear, accurate, and well-formatted responses."
            if rag_context:
                system_content += rag_context + "\n\nUse the provided context to enhance your responses when relevant."
            
            messages.append({
                "role": "system",
                "content": system_content
            })
            
            # Add user message - check if model supports vision
            if image_data and supports_vision:
                # For vision models, use the multimodal format
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_message or "What do you see in this image?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                })
            elif image_data:
                # If image provided but model doesn't support vision, return error
                return jsonify({
                    'error': f'Model {model} does not support image analysis. Please use a vision-capable model like meta-llama/llama-4-maverick-17b-128e-instruct.',
                    'status': 'error'
                }), 400
            else:
                # Text-only message
                messages.append({"role": "user", "content": user_message})
            
            # Create chat completion using multi-provider system
            if llm_manager is not None:
                try:
                    completion_result = llm_manager.chat_completion(
                        model=model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=get_max_tokens_for_model(model)
                    )
                    response = completion_result['content']
                    provider_used = completion_result['provider']
                    model_used = completion_result['model']
                    usage_info = completion_result.get('usage', {})
                    response_time = time.time() - start_time
                    
                    print(f"✅ Response generated using {provider_used} provider")
                    
                except Exception as e:
                    print(f"❌ Multi-provider error: {e}")
                    # Fallback to legacy Groq client
                    if client is not None:
                        chat_completion = client.chat.completions.create(
                            messages=messages,
                            model=model,
                            temperature=0.7,
                            max_tokens=get_max_tokens_for_model(model),
                            top_p=0.9
                        )
                        response = chat_completion.choices[0].message.content
                        provider_used = "groq"
                        model_used = model
                        usage_info = {
                            "prompt_tokens": chat_completion.usage.prompt_tokens,
                            "completion_tokens": chat_completion.usage.completion_tokens,
                            "total_tokens": chat_completion.usage.total_tokens
                        }
                        response_time = time.time() - start_time
                    else:
                        raise e
            else:
                # Fallback to legacy Groq client
                if client is None:
                    return jsonify({
                        'error': 'No AI providers available. Please check your API keys.',
                        'status': 'error'
                    }), 500
                
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=model,
                    temperature=0.7,
                    max_tokens=get_max_tokens_for_model(model),
                    top_p=0.9
                )
                response = chat_completion.choices[0].message.content
                provider_used = "groq"
                model_used = model
                usage_info = {
                    "prompt_tokens": chat_completion.usage.prompt_tokens,
                    "completion_tokens": chat_completion.usage.completion_tokens,
                    "total_tokens": chat_completion.usage.total_tokens
                }
                response_time = time.time() - start_time
            
            # Apply AI Guardrails to AI response as well
            response_guardrails_result = apply_ai_guardrails(response)
            if response_guardrails_result['blocked']:
                return jsonify({
                    'response': f"⚠️ AI response blocked by guardrails: {response_guardrails_result['reason']}",
                    'blocked': True,
                    'guardrails': response_guardrails_result,
                    'model_used': model,
                    'response_time': round(response_time, 2),
                    'status': 'blocked'
                }), 200
            
            # Prepare enhanced response
            enhanced_info = []
            if use_rag and rag_context:
                enhanced_info.append('rag')
            
            print(f"✅ Chat completed - Model used: {model}, Response time: {round(response_time, 2)}s")
            
            return jsonify({
                'response': response,
                'model_used': model_used,
                'provider_used': provider_used,
                'response_time': round(response_time, 2),
                'status': 'success',
                'enhanced_with': enhanced_info,
                'rag_chunks_used': len(relevant_chunks),
                'guardrails': {'status': 'passed', 'checked': True},
                'usage': usage_info
            })
            
        except Exception as e:
            print(f"❌ Error in chat: {e}")
            return jsonify({
                'error': str(e),
                'status': 'error'
            }), 500

    @app.route('/api/models', methods=['GET'])
    def get_models():
        """Get available models from all providers"""
        try:
            # Use multi-provider system if available
            if llm_manager is not None:
                available_models = llm_manager.get_available_models()
                
                # Categorize models
                text_models = []
                vision_models = []
                
                for model in available_models:
                    # Enhance model info
                    enhanced_model = {
                        'id': model['id'],
                        'name': format_model_name(model['name']),
                        'description': model['description'],
                        'provider': model['provider'],
                        'provider_name': model['provider_name'],
                        'supportsVision': 'vision' in model['capabilities'],
                        'category': get_model_category_from_capabilities(model['capabilities']),
                        'speed': get_model_speed_from_cost(model['cost_per_1k_tokens']),
                        'capabilities': model['capabilities'],
                        'context_length': model['context_length'],
                        'cost_per_1k_tokens': model['cost_per_1k_tokens']
                    }
                    
                    if enhanced_model['supportsVision']:
                        vision_models.append(enhanced_model)
                    else:
                        text_models.append(enhanced_model)
                
                # Sort models by provider priority and speed
                text_models.sort(key=lambda x: (x.get('cost_per_1k_tokens', 0), -x['speed']))
                vision_models.sort(key=lambda x: (x.get('cost_per_1k_tokens', 0), -x['speed']))
                
                # Determine best default models
                default_text = text_models[0]['id'] if text_models else None
                default_vision = vision_models[0]['id'] if vision_models else None
                
                return jsonify({
                    'models': available_models,
                    'textModels': text_models,
                    'visionModels': vision_models,
                    'defaultText': default_text,
                    'defaultVision': default_vision,
                    'providers': llm_manager.get_provider_status(),
                    'multi_provider_enabled': True,
                    'status': 'success'
                })
            
            # Fallback to legacy Groq-only system
            elif client is not None:
                # Fetch models from Groq API
                models_response = client.models.list()
                available_models = []
                text_models = []
                vision_models = []
                
                # Categorize models and enhance with metadata
                for model in models_response.data:
                    # Determine if model supports vision
                    vision_keywords = ['vision', 'llava', 'multimodal', 'visual']
                    # Add Llama 4 models that support vision
                    llama4_vision_models = ['meta-llama/llama-4-maverick-17b-128e-instruct', 'meta-llama/llama-4-scout-17b-16e-instruct']
                    
                    supports_vision = (any(keyword in model.id.lower() for keyword in vision_keywords) or 
                                     model.id in llama4_vision_models)
                    
                    # Create enhanced model info
                    model_info = {
                        'id': model.id,
                        'name': format_model_name(model.id),
                        'description': get_model_description(model.id),
                        'provider': 'groq',
                        'provider_name': 'Groq',
                        'supportsVision': supports_vision,
                        'category': get_model_category(model.id),
                        'speed': get_model_speed(model.id),
                        'capabilities': get_model_capabilities(model.id)
                    }
                    
                    available_models.append(model_info)
                    
                    if supports_vision:
                        vision_models.append(model_info)
                    else:
                        text_models.append(model_info)
                
                # Sort models by preference
                text_models.sort(key=lambda x: x['speed'], reverse=True)
                vision_models.sort(key=lambda x: x['speed'], reverse=True)
                
                # Determine best default models
                default_text = text_models[0]['id'] if text_models else None
                default_vision = vision_models[0]['id'] if vision_models else None
                
                return jsonify({
                    'models': {
                        'available': available_models,
                        'text_models': text_models,
                        'vision_models': vision_models,
                        'default': default_text,
                        'default_vision': default_vision,
                        'recommendations': {
                            'fast': get_fastest_model(text_models),
                            'smart': get_smartest_model(text_models),
                            'vision': default_vision,
                            'coding': get_coding_model(text_models),
                            'creative': get_creative_model(text_models)
                        }
                    },
                    'status': 'success'
                })
            else:
                # No providers available
                return jsonify({
                    'models': {
                        'available': get_fallback_models(),
                        'default': 'llama-3.1-8b-instant',
                        'error': 'No providers available'
                    },
                    'status': 'fallback'
                }), 200
                
        except Exception as e:
            print(f"❌ Error fetching models: {e}")
            # Return fallback models on error
            return jsonify({
                'models': {
                    'available': get_fallback_models(),
                    'default': 'llama-3.1-8b-instant',
                    'error': 'Using fallback models'
                },
                'status': 'fallback'
            }), 200