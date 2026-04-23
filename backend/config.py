import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # Database
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'mongodb')  # mongodb or postgresql
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/candidate_search')
    POSTGRESQL_URI = os.getenv('POSTGRESQL_URI', 'postgresql://user:password@localhost/candidate_search')
    
    # CORS - allow all localhost origins in development
    _is_dev = os.getenv('DEBUG', 'True') == 'True' or os.getenv('FLASK_ENV') == 'development'
    CORS_ORIGINS = ['*'] if _is_dev else os.getenv('CORS_ORIGINS', 'http://localhost:4200').split(',')
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    
    # AI/ML
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
    SIMILARITY_THRESHOLD = 0.5

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_TYPE = 'sqlite'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
