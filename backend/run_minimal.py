#!/usr/bin/env python
"""Minimal Flask app for demo purposes"""
from flask import Flask, jsonify
from flask_cors import CORS
import os

def create_minimal_app():
    """Create a minimal Flask app"""
    app = Flask(__name__)
    
    # Initialize CORS
    CORS(app, origins=['*'])
    
    # Basic health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok', 'message': 'Backend is running'})
    
    # Dummy candidate endpoints
    @app.route('/api/candidates', methods=['GET'])
    def get_candidates():
        return jsonify({'candidates': [], 'message': 'Database not configured'})
    
    @app.route('/api/search', methods=['POST'])
    def search_candidates():
        return jsonify({'results': [], 'message': 'Search functionality not available'})
    
    return app

if __name__ == '__main__':
    app = create_minimal_app()
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
