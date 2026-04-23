"""Embedding generation utility module"""
import math
from typing import List

try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_NUMPY_SKLEARN = True
except ImportError:
    HAS_NUMPY_SKLEARN = False
    np = None
    cosine_similarity = None

# Placeholder for Sentence-BERT model initialization
# Will be implemented when models are added
embedding_model = None

def initialize_embedding_model():
    """Initialize Sentence-BERT model"""
    global embedding_model
    # Placeholder - will implement with sentence-transformers
    print("Embedding model initialization placeholder")

def generate_embedding(text: str) -> List[float]:
    """Generate embedding for text using Sentence-BERT"""
    # Placeholder - will implement with sentence-transformers
    # For now, return a dummy embedding
    return [0.0] * 384  # all-MiniLM-L6-v2 outputs 384-dimensional vectors

def generate_query_embedding(query: str) -> List[float]:
    """Generate embedding for search query"""
    # Placeholder - will implement with sentence-transformers
    return generate_embedding(query)

def compute_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Compute cosine similarity between two embeddings"""
    try:
        if not embedding1 or not embedding2:
            return 0.0

        if HAS_NUMPY_SKLEARN:
            emb1 = np.array(embedding1).reshape(1, -1)
            emb2 = np.array(embedding2).reshape(1, -1)
            similarity = cosine_similarity(emb1, emb2)[0][0]
            return float(similarity)

        # Pure Python fallback cosine similarity
        dot = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = math.sqrt(sum(a * a for a in embedding1))
        norm2 = math.sqrt(sum(b * b for b in embedding2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot / (norm1 * norm2))
    except Exception as e:
        print(f"Error computing similarity: {str(e)}")
        return 0.0

def rank_candidates(query_embedding: List[float], candidates: List[dict], weights: dict = None) -> List[dict]:
    """
    Rank candidates using weighted scoring system
    
    weights: {
        'semantic_similarity': 0.6,
        'experience_match': 0.2,
        'mcq_score': 0.2
    }
    """
    if weights is None:
        weights = {
            'semantic_similarity': 0.6,
            'experience_match': 0.2,
            'mcq_score': 0.2
        }
    
    scored_candidates = []
    
    for candidate in candidates:
        # Compute semantic similarity
        semantic_sim = compute_similarity(query_embedding, candidate.get('embedding', []))
        
        # Compute experience match (simplified)
        experience_match = 0.5  # Placeholder
        
        # Get MCQ score
        mcq_score = candidate.get('mcq_score', 0.0) / 100.0 if candidate.get('mcq_score') else 0.0
        
        # Compute final score
        final_score = (
            weights['semantic_similarity'] * semantic_sim +
            weights['experience_match'] * experience_match +
            weights['mcq_score'] * mcq_score
        )
        
        candidate['final_score'] = final_score
        scored_candidates.append(candidate)
    
    # Sort by score descending
    scored_candidates.sort(key=lambda x: x['final_score'], reverse=True)
    
    # Add rank
    for idx, candidate in enumerate(scored_candidates, 1):
        candidate['rank'] = idx
        candidate['score'] = candidate['final_score']
    
    return scored_candidates
