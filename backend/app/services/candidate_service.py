"""Candidate service"""
import os
import uuid
from typing import List, Dict, Any
from config import Config
from models import Candidate
from app.utils.tfidf_resume_parser import extract_text_from_resume, extract_candidate_info, allowed_file
from app.utils.embedding_utils import generate_embedding, generate_query_embedding, rank_candidates, compute_similarity

class CandidateService:
    """Service for managing candidates"""
    
    # In-memory store for candidates (when database is not available)
    _candidates_memory = []
    
    def __init__(self):
        """Initialize candidate service"""
        self.db = self._get_database()
    
    def _get_database(self):
        """Get database connection"""
        if Config.DATABASE_TYPE == 'mongodb':
            from database import get_mongodb_db
            return get_mongodb_db()
        else:
            # PostgreSQL will be implemented similarly
            return None
    
    def upload_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Upload and process resume
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Candidate data dictionary
        """
        try:
            print(f"\n[UPLOAD] Processing: {file_path}")
            
            # Extract text from resume
            resume_text = extract_text_from_resume(file_path)
            
            # Extract candidate information
            candidate_info = extract_candidate_info(resume_text)
            
            print(f"[UPLOAD] Extracted - Name: {candidate_info['name']}, Skills: {len(candidate_info['skills'])}, Experience: {candidate_info['experience']}")
            
            # Generate embedding
            embedding = generate_embedding(resume_text)
            
            # Create candidate object with ID
            candidate_dict = {
                'id': str(uuid.uuid4()),
                'name': str(candidate_info['name']),
                'skills': [str(s) for s in candidate_info['skills']],  # Ensure all skills are strings
                'experience': int(candidate_info['experience']),  # Ensure experience is int
                'resume_text': resume_text,
                'embedding': embedding
            }
            
            # Save to database or memory
            if self.db is not None:
                self.db['candidates'].insert_one(candidate_dict)
            else:
                # Store in memory when database is not available
                CandidateService._candidates_memory.append(candidate_dict)
            
            # Return without embedding and resume_text for UI - ensure JSON serializable
            return_data = {
                'id': candidate_dict['id'],
                'name': candidate_dict['name'],
                'skills': candidate_dict['skills'],
                'experience': candidate_dict['experience']
            }
            print(f"[UPLOAD] Returning: {return_data}")
            return return_data
        
        except Exception as e:
            print(f"[ERROR] Error uploading resume: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error uploading resume: {str(e)}")
    
    def upload_multiple_resumes(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Upload multiple resumes"""
        results = []
        for file_path in file_paths:
            try:
                result = self.upload_resume(file_path)
                results.append(result)
            except Exception as e:
                print(f"Error uploading {file_path}: {str(e)}")
        
        return results
    
    def get_all_candidates(self) -> List[Dict[str, Any]]:
        """Get all candidates"""
        try:
            if self.db is not None:
                candidates = list(self.db['candidates'].find({}, {'embedding': 0, 'resume_text': 0}))
                for candidate in candidates:
                    candidate['_id'] = str(candidate.get('_id'))
                return candidates
            else:
                # Return from memory store
                return [{k: v for k, v in c.items() if k not in ['embedding', 'resume_text']} for c in CandidateService._candidates_memory]
        except Exception as e:
            print(f"Error fetching candidates: {str(e)}")
            # Fallback to memory if database fails
            return [{k: v for k, v in c.items() if k != 'embedding'} for c in CandidateService._candidates_memory]
    
    def get_candidate_by_id(self, candidate_id: str) -> Dict[str, Any]:
        """Get candidate by ID"""
        try:
            if self.db is not None:
                from bson import ObjectId
                candidate = self.db['candidates'].find_one({'id': candidate_id}, {'embedding': 0, 'resume_text': 0})
                if candidate:
                    candidate['_id'] = str(candidate.get('_id'))
                return candidate
            else:
                # Search memory store
                for c in CandidateService._candidates_memory:
                    if c.get('id') == candidate_id:
                        return {k: v for k, v in c.items() if k not in ['embedding', 'resume_text']}
                return None
        except Exception as e:
            print(f"Error fetching candidate: {str(e)}")
            # Fallback to memory search
            for c in CandidateService._candidates_memory:
                if c.get('id') == candidate_id:
                    return {k: v for k, v in c.items() if k != 'embedding'}
            return None
    
    def search_candidates(self, query_text: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search candidates using semantic similarity (embeddings) with experience filtering
        
        Uses all-MiniLM-L6-v2 model for semantic matching (60% weight)
        Combined with experience score (20% weight) and MCQ score (20% weight)
        
        Args:
            query_text: Search query (e.g., "Python developer with 5 years experience")
            filters: Optional filters {skills: [], minExperience: 5, maxExperience: 10}
            
        Returns:
            Ranked list of candidates with similarity scores
        """
        try:
            # Get all candidates with embeddings
            if self.db is not None:
                candidates = list(self.db['candidates'].find({}, {'_id': 0}))
            else:
                candidates = [c for c in CandidateService._candidates_memory]
            
            if not candidates:
                return []
            
            # Parse filters
            min_experience = 0
            max_experience = 999
            
            if filters:
                min_exp_key = 'minExperience' if 'minExperience' in filters else 'min_experience'
                if min_exp_key in filters and filters[min_exp_key] is not None:
                    min_experience = int(filters[min_exp_key])
                
                max_exp_key = 'maxExperience' if 'maxExperience' in filters else 'max_experience'
                if max_exp_key in filters and filters[max_exp_key] is not None:
                    max_experience = int(filters[max_exp_key])
            
            print(f"\n[SEARCH] Using semantic embedding search (all-MiniLM-L6-v2)")
            print(f"[SEARCH] Query: '{query_text}'")
            print(f"[SEARCH] Filters - Experience: {min_experience}-{max_experience} years")
            
            # Generate query embedding
            query_embedding = generate_query_embedding(query_text)
            
            # Rank all candidates by semantic similarity + experience + MCQ
            ranked_candidates = rank_candidates(query_embedding, candidates)
            
            # Filter by experience range
            filtered_results = []
            for candidate in ranked_candidates:
                exp = candidate.get('experience', 0)
                if min_experience <= exp <= max_experience:
                    # Remove large data before returning
                    if 'resume_text' in candidate:
                        del candidate['resume_text']
                    filtered_results.append(candidate)
            
            print(f"[SEARCH] Found {len(filtered_results)} candidates matching filters")
            for i, c in enumerate(filtered_results[:5], 1):
                print(f"  #{i}. {c['name']} - Score: {c.get('percentage', 0):.1f}% | " +
                      f"Semantic: {c.get('semantic_similarity', 0):.3f} | " +
                      f"Experience: {c.get('experience', 0)}y")
            
            return filtered_results
        
        except Exception as e:
            print(f"[ERROR] Error searching candidates: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def _apply_filters(self, candidates: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters to candidates"""
        filtered = candidates
        
        # Filter by skills
        if 'skills' in filters and filters['skills']:
            filtered = [
                c for c in filtered 
                if any(skill.lower() in [s.lower() for s in c.get('skills', [])] 
                       for skill in filters['skills'])
            ]
        
        # Filter by minimum experience (handle both minExperience and min_experience)
        min_exp_key = 'minExperience' if 'minExperience' in filters else 'min_experience'
        if min_exp_key in filters:
            min_exp = filters[min_exp_key]
            filtered = [
                c for c in filtered 
                if self._extract_experience_years(c.get('experience', '')) >= min_exp
            ]
        
        if 'max_experience' in filters:
            filtered = [
                c for c in filtered 
                if self._extract_experience_years(c.get('experience', '')) <= filters['max_experience']
            ]
        
        return filtered
    
    def _extract_experience_years(self, experience_str) -> int:
        """Extract years from experience string or int"""
        import re
        # Handle case where experience is already an integer
        if isinstance(experience_str, int):
            return experience_str
        # Handle string input
        if not isinstance(experience_str, str):
            return 0
        match = re.search(r'(\d+)', experience_str)
        return int(match.group(1)) if match else 0
    
    def delete_all_candidates(self) -> Dict[str, Any]:
        """Delete all candidates"""
        try:
            if self.db is not None:
                result = self.db['candidates'].delete_many({})
                deleted_count = result.deleted_count
            else:
                # Clear memory store
                deleted_count = len(CandidateService._candidates_memory)
                CandidateService._candidates_memory = []
            
            return {'deleted_count': deleted_count}
        except Exception as e:
            raise Exception(f"Error deleting candidates: {str(e)}")
    
    def update_candidate_status(self, candidate_id: str, status: str) -> Dict[str, Any]:
        """Update candidate status"""
        try:
            if self.db is not None:
                result = self.db['candidates'].update_one(
                    {'id': candidate_id},
                    {'$set': {'status': status}}
                )
                if result.modified_count > 0:
                    return {'message': 'Candidate updated', 'status': status}
            return {'error': 'Candidate not found'}
        except Exception as e:
            raise Exception(f"Error updating candidate: {str(e)}")
