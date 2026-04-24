#!/usr/bin/env python
"""Test backend - simplified FastAPI app"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/api/health')
def health_check():
    return {'status': 'healthy', 'service': 'candidate-search-backend'}

@app.get('/api/candidates')
def get_candidates():
    return {'candidates': [], 'message': 'Database not configured'}

if __name__ == '__main__':
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=5000,
        reload=True
    )
