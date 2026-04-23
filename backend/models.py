import os
import uuid
from typing import List, Dict, Any
from datetime import datetime

class Candidate:
    """Candidate model"""
    
    def __init__(
        self,
        name: str,
        skills: List[str],
        experience: str,
        resume_text: str,
        embedding: List[float] = None,
        mcq_score: float = 0.0,
        status: str = "Active",
        id: str = None
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.skills = skills
        self.experience = experience
        self.resume_text = resume_text
        self.embedding = embedding
        self.mcq_score = mcq_score
        self.status = status
        self.uploaded_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert candidate to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "skills": self.skills,
            "experience": self.experience,
            "resume_text": self.resume_text,
            "embedding": self.embedding,
            "mcq_score": self.mcq_score,
            "status": self.status,
            "uploaded_at": self.uploaded_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Candidate':
        """Create candidate from dictionary"""
        return Candidate(
            name=data.get('name'),
            skills=data.get('skills', []),
            experience=data.get('experience'),
            resume_text=data.get('resume_text'),
            embedding=data.get('embedding'),
            mcq_score=data.get('mcq_score', 0.0),
            status=data.get('status', 'Active'),
            id=data.get('id')
        )

class SearchQuery:
    """Search query model"""
    
    def __init__(
        self,
        query: str,
        filters: Dict[str, Any] = None
    ):
        self.query = query
        self.filters = filters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "filters": self.filters
        }

class SearchResult:
    """Search result model"""
    
    def __init__(
        self,
        candidates: List[Candidate],
        total: int,
        query: str
    ):
        self.candidates = candidates
        self.total = total
        self.query = query
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidates": [c.to_dict() for c in self.candidates],
            "total": self.total,
            "query": self.query,
            "timestamp": self.timestamp
        }
