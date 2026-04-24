from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import config
import os

def create_app(config_name='development'):
    """Application factory"""
    app = FastAPI()
    
    # Load config
    cfg = config[config_name]
    app.config = cfg
    
    # Create upload folder if it doesn't exist
    os.makedirs(cfg.UPLOAD_FOLDER, exist_ok=True)
    
    # Initialize CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.CORS_ORIGINS if isinstance(cfg.CORS_ORIGINS, list) else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize database (optional - graceful degradation)
    try:
        from database import initialize_database
        initialize_database()
    except ImportError as e:
        print(f"Warning: Database initialization skipped - {e}")
    
    # Register health check
    @app.get('/api/health')
    def health_check():
        return {'status': 'healthy', 'service': 'candidate-search-backend'}
    
    # Register routers
    from app.routes.candidate_routes import candidate_bp
    app.include_router(candidate_bp, prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
