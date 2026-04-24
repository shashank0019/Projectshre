"""Embedding generation utility module using Sentence-Transformers"""
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

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    SentenceTransformer = None

# Global embedding model - loaded once
embedding_model = None

def initialize_embedding_model():
    """Initialize Sentence-BERT model (all-MiniLM-L6-v2)"""
    global embedding_model
    if embedding_model is not None:
        return  # Already initialized
    
    try:
        if HAS_SENTENCE_TRANSFORMERS:
            print("Loading Sentence-Transformers model: all-MiniLM-L6-v2...")
            embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[OK] Model loaded successfully. Embedding dimension: 384")
        else:
            print("WARNING: sentence-transformers not installed, falling back to dummy embeddings")
    except Exception as e:
        print(f"Error loading embedding model: {str(e)}")

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using Sentence-BERT (all-MiniLM-L6-v2)
    
    Returns 384-dimensional vector as list for MongoDB storage
    """
    global embedding_model
    
    if embedding_model is None:
        initialize_embedding_model()
    
    try:
        if embedding_model is not None and HAS_SENTENCE_TRANSFORMERS:
            # Convert text to embedding
            embedding = embedding_model.encode(text, convert_to_tensor=False)
            # Return as list for JSON/MongoDB serialization
            return embedding.tolist()
        else:
            # Fallback dummy embedding
            return [0.0] * 384
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return [0.0] * 384

def generate_query_embedding(query: str) -> List[float]:
    """Generate embedding for search query using the same model"""
    return generate_embedding(query)

def compute_skill_scores(candidate_embedding: List[float], skills: List[str]) -> dict:
    """
    Compute per-skill relevance scores using all-MiniLM-L6-v2.

    Compares the CANDIDATE'S OWN RESUME EMBEDDING against each skill phrase,
    so candidates who have more content about a skill score higher than those
    who barely mention it — making scores unique per candidate.

    Returns a dict: { skill_name: percentage_float }
    """
    global embedding_model
    if embedding_model is None:
        initialize_embedding_model()

    skill_scores = {}
    if not skills or not candidate_embedding:
        return skill_scores

    for skill in skills:
        try:
            # Embed the skill as a phrase; compare against candidate's resume embedding
            skill_phrase = f"experience with {skill}"
            skill_embedding = generate_embedding(skill_phrase)
            raw_sim = compute_similarity(candidate_embedding, skill_embedding)
            # raw_sim is 0-1 (normalized cosine). Remap [0.5, 1.0] -> [0%, 100%]
            # so that truly unrelated text scores near 0 and strong matches near 100.
            pct = max(0.0, (raw_sim - 0.5) * 2.0) * 100.0
            skill_scores[skill] = round(pct, 1)
        except Exception as e:
            print(f"[WARN] Skill score error for '{skill}': {e}")
            skill_scores[skill] = 0.0

    return skill_scores

def compute_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Compute cosine similarity between two embeddings (0.0 to 1.0)"""
    try:
        if not embedding1 or not embedding2:
            return 0.0
        
        if len(embedding1) == 0 or len(embedding2) == 0:
            return 0.0

        if HAS_NUMPY_SKLEARN:
            emb1 = np.array(embedding1).reshape(1, -1)
            emb2 = np.array(embedding2).reshape(1, -1)
            similarity = cosine_similarity(emb1, emb2)[0][0]
            # Normalize to 0-1 range (cosine similarity returns -1 to 1)
            return float((similarity + 1) / 2)

        # Pure Python fallback cosine similarity
        dot = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = math.sqrt(sum(a * a for a in embedding1))
        norm2 = math.sqrt(sum(b * b for b in embedding2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        similarity = float(dot / (norm1 * norm2))
        # Normalize to 0-1 range
        return (similarity + 1) / 2
    except Exception as e:
        print(f"Error computing similarity: {str(e)}")
        return 0.0

def rank_candidates(query_embedding: List[float], candidates: List[dict], weights: dict = None) -> List[dict]:
    """
    Rank candidates using semantic similarity + experience + MCQ score
    
    Default weights:
    - semantic_similarity: 60% (most important - semantic match from embeddings)
    - experience_score: 20% (normalized experience comparison)
    - mcq_score: 20% (MCQ performance)
    """
    if weights is None:
        weights = {
            'semantic_similarity': 0.6,
            'experience_score': 0.2,
            'mcq_score': 0.2
        }
    
    scored_candidates = []
    
    # Find max experience for normalization
    max_experience = max([c.get('experience', 0) for c in candidates], default=10)
    if max_experience == 0:
        max_experience = 10
    
    for candidate in candidates:
        # 1. Compute semantic similarity (0.0 to 1.0)
        semantic_sim = compute_similarity(query_embedding, candidate.get('embedding', []))

        # 2. Normalize experience score (0.0 to 1.0)
        candidate_exp = candidate.get('experience', 0)
        experience_score = min(candidate_exp / max_experience, 1.0)

        # 3. Get MCQ score (normalize to 0.0-1.0)
        mcq_score = 0.0
        if 'mcq_score' in candidate and candidate['mcq_score'] is not None:
            mcq_score = min(candidate['mcq_score'] / 100.0, 1.0)

        # 4. Compute final weighted score
        final_score = (
            weights['semantic_similarity'] * semantic_sim +
            weights['experience_score'] * experience_score +
            weights['mcq_score'] * mcq_score
        )

        # Ensure score is in valid range
        final_score = max(0.0, min(1.0, final_score))

        # 5. Compute per-skill scores using the CANDIDATE'S resume embedding
        #    (not the query) — so each candidate gets unique scores per skill
        skills = candidate.get('skills', [])
        candidate_emb = candidate.get('embedding', [])
        skill_scores = compute_skill_scores(candidate_emb, skills)

        # Add scoring details to candidate
        candidate['score'] = final_score
        candidate['percentage'] = round(final_score * 100, 2)
        candidate['semantic_similarity'] = round(semantic_sim, 3)
        candidate['experience_score'] = round(experience_score, 3)
        candidate['mcq_score_normalized'] = round(mcq_score, 3)
        candidate['skill_scores'] = skill_scores  # { skill: pct } unique per skill

        scored_candidates.append(candidate)
    
    # Sort by score descending
    scored_candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # Add rank
    for idx, candidate in enumerate(scored_candidates, 1):
        candidate['rank'] = idx
    
    return scored_candidates
