"""
Static Routes Module
===================
Static file serving and frontend routes
"""

from flask import Blueprint, send_from_directory, jsonify
import os
import json

static_bp = Blueprint('static', __name__)

@static_bp.route('/')
def home():
    """Serve the main HTML file"""
    try:
        # Get the correct path relative to the backend/modules/api directory
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(current_dir, '../../../frontend/index.html')
        with open(html_path, 'r') as f:
            return f.read()
    except FileNotFoundError as e:
        return f"Frontend not found: {e}", 404

@static_bp.route('/css/<path:filename>')
def css_files(filename):
    """Serve CSS files"""
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_dir = os.path.join(current_dir, '../../../frontend/css')
    return send_from_directory(css_dir, filename)

@static_bp.route('/js/<path:filename>')
def js_files(filename):
    """Serve JS files"""
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    js_dir = os.path.join(current_dir, '../../../frontend/js')
    return send_from_directory(js_dir, filename)

@static_bp.route('/manifest.json')
def manifest():
    """Serve PWA manifest"""
    try:
        with open('../frontend/public/manifest.json', 'r') as f:
            return f.read(), 200, {'Content-Type': 'application/json'}
    except FileNotFoundError:
        # Return a default manifest
        default_manifest = {
            "name": "NexusAI",
            "short_name": "NexusAI",
            "description": "Advanced AI Chat Interface",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#0f172a",
            "theme_color": "#6366f1",
            "icons": []
        }
        return jsonify(default_manifest)