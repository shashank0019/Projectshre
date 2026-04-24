#!/usr/bin/env python
"""Minimal FastAPI app for demo purposes"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

def create_minimal_app():
    """Create a minimal FastAPI app"""
    app = FastAPI()
    
    # Initialize CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    
    # Basic health check endpoint
    @app.get('/api/health')
    def health():
        return {'status': 'ok', 'message': 'Backend is running'}
    
    # Dummy candidate endpoints
    @app.get('/api/candidates')
    def get_candidates():
        return {'candidates': [], 'message': 'Database not configured'}
    
    @app.post('/api/search')
    def search_candidates():
        return {'results': [], 'message': 'Search functionality not available'}
    
    return app

if __name__ == '__main__':
    app = create_minimal_app()
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=5000
    )
