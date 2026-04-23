#!/usr/bin/env python
"""Main entry point for the backend application"""
import os
from app_factory import create_app

if __name__ == '__main__':
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    
    # Run the application
    app.run(
        debug=os.getenv('DEBUG', 'True') == 'True',
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000))
    )
