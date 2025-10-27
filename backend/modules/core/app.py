"""
Main Application Module
======================
Flask application factory and configuration
"""

from flask import Flask
from flask_cors import CORS
import logging
from .config import get_app_config
from ..api.chat_routes import chat_bp
from ..api.static_routes import static_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    """Create and configure Flask application"""
    config = get_app_config()
    
    # Create Flask app with correct paths
    app = Flask(__name__, 
                static_folder='../../../frontend/static',
                static_url_path='/static',
                template_folder='../../../frontend')
    
    # Configure app
    app.secret_key = config.SECRET_KEY
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(static_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {"status": "healthy", "service": "NexusAI"}
    
    return app

def run_app():
    """Run the Flask application"""
    config = get_app_config()
    app = create_app()
    
    print("🚀 Starting NexusAI Server")
    print(f"🔧 Debug mode: {config.DEBUG}")
    print(f"🌐 Access at: http://localhost:{config.PORT}")
    
    app.run(
        host='0.0.0.0',
        port=config.PORT,
        debug=config.DEBUG
    )