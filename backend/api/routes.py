"""
API Routes Module
================
Contains all API route definitions for NexusAI
"""

from flask import Blueprint, request, jsonify
import os
import time
import json
from datetime import datetime

# Create blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

def init_routes(app, llm_manager=None, rag_system=None, lora_system=None):
    """Initialize all API routes with dependencies"""
    
    # Store dependencies for use in routes
    api_bp.llm_manager = llm_manager
    api_bp.rag_system = rag_system
    api_bp.lora_system = lora_system
    
    # Register the blueprint
    app.register_blueprint(api_bp)
    
    return api_bp

# We'll add the actual route definitions here in the next step