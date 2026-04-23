import os
import json
from datetime import datetime
from config import Config

# Try to import optional database drivers
try:
    from pymongo import MongoClient
    HAS_PYMONGO = True
except ImportError:
    HAS_PYMONGO = False
    MongoClient = None

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    create_engine = None
    sessionmaker = None

# MongoDB Setup
def get_mongodb_client():
    """Get MongoDB client"""
    if not HAS_PYMONGO:
        print("Warning: pymongo not installed")
        return None
    try:
        client = MongoClient(Config.MONGODB_URI)
        client.admin.command('ping')
        print("MongoDB connection successful")
        return client
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None

def get_mongodb_db():
    """Get MongoDB database"""
    client = get_mongodb_client()
    if client:
        return client['WebApp']
    return None

# PostgreSQL Setup
def get_postgresql_engine():
    """Get PostgreSQL engine"""
    if not HAS_SQLALCHEMY:
        print("Warning: sqlalchemy not installed")
        return None
    try:
        engine = create_engine(Config.POSTGRESQL_URI)
        # Test connection
        with engine.connect() as conn:
            print("PostgreSQL connection successful")
        return engine
    except Exception as e:
        print(f"PostgreSQL connection error: {e}")
        return None

# Sample MongoDB Collections Schema
MONGODB_SCHEMA = {
    "candidates": {
        "id": "unique string",
        "name": "string",
        "skills": ["array of strings"],
        "experience": "string",
        "resume_text": "string",
        "embedding": "list of floats",
        "mcq_score": "float",
        "status": "string (Active/Selected/Rejected)",
        "uploaded_at": "timestamp",
        "updated_at": "timestamp"
    }
}

# PostgreSQL Tables Schema
POSTGRESQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS candidates (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    skills TEXT[],
    experience TEXT,
    resume_text TEXT,
    embedding FLOAT8[],
    mcq_score FLOAT DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'Active',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_name ON candidates(name);
CREATE INDEX IF NOT EXISTS idx_status ON candidates(status);
"""

def initialize_database():
    """Initialize database based on config"""
    if Config.DATABASE_TYPE == 'mongodb':
        db = get_mongodb_db()
        if db is not None:
            # Create collections if they don't exist
            if 'candidates' not in db.list_collection_names():
                db.create_collection('candidates')
                print("MongoDB collection 'candidates' created")
        return db
    elif Config.DATABASE_TYPE == 'postgresql':
        engine = get_postgresql_engine()
        if engine:
            with engine.connect() as conn:
                conn.execute(POSTGRESQL_SCHEMA)
                conn.commit()
                print("PostgreSQL tables created")
        return engine
    
    return None
