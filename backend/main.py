#!/usr/bin/env python3
"""
NexusAI Main Entry Point
========================
Modular Flask application for AI chat interface
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.core.app import run_app

if __name__ == '__main__':
    run_app()