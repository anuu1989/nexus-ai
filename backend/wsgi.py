"""
WSGI Entry Point
Production-ready WSGI application
"""

import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app
from app import app

if __name__ == "__main__":
    app.run()