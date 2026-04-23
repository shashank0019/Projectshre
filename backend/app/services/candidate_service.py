"""Candidate service"""
import os
import uuid
from typing import List, Dict, Any
from config import Config
from models import Candidate
from app.utils.tfidf_resume_parser import extract_text_from_resume, extract_candidate_info, allowed_file
from app.utils.embedding_utils import generate_embedding, rank_candidates

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
        Search candidates using skill matching and experience filtering
        
        Args:
            query_text: Search query (skills and experience)
            filters: Optional filters (skills, minExperience, etc.)
            
        Returns:
            Ranked list of candidates
        """
        try:
            # Get all candidates
            if self.db is not None:
                candidates = list(self.db['candidates'].find({}, {'_id': 0}))
            else:
                candidates = [{k: v for k, v in c.items() if k != 'embedding'} for c in CandidateService._candidates_memory]
            
            if not candidates:
                return []
            
            # Extract search terms from query
            query_skills = []
            min_experience = 0
            
            # Parse query for skills and experience
            if filters:
                if 'skills' in filters and filters['skills']:
                    query_skills = filters['skills']
                
                min_exp_key = 'minExperience' if 'minExperience' in filters else 'min_experience'
                if min_exp_key in filters and filters[min_exp_key]:
                    min_experience = filters[min_exp_key]
            
            print(f"\n[SEARCH] Query skills: {query_skills}, Min experience: {min_experience} years")
            
            # Score each candidate
            scored_candidates = []
            for candidate in candidates:
                # Get candidate skills and experience
                candidate_skills = [s.lower() for s in candidate.get('skills', [])]
                candidate_experience = self._extract_experience_years(candidate.get('experience', ''))
                
                # Count exact matching skills
                matching_skills = 0
                matched_skill_names = []
                if query_skills:
                    for query_skill in query_skills:
                        for cskill in candidate_skills:
                            if query_skill.lower() in cskill:
                                matching_skills += 1
                                matched_skill_names.append(query_skill)
                                break
                
                # Check experience match
                experience_match = candidate_experience >= min_experience
                
                # Calculate skill score - IMPROVED DIFFERENTIATION
                max_skills = len(query_skills) if query_skills else 1
                skill_score = (matching_skills / max_skills) * 0.8 if max_skills > 0 else 0.3
                
                # Calculate experience score - IMPROVED DIFFERENTIATION
                if min_experience == 0:
                    # Scale 0-10 years to 0.3-1.0
                    experience_score = 0.3 + (min(candidate_experience, 10) / 10.0) * 0.7
                elif experience_match:
                    # Bonus for exceeding minimum - more differentiation
                    experience_bonus = min((candidate_experience - min_experience) / 2.0, 1.0)
                    experience_score = 0.5 + experience_bonus
                else:
                    experience_score = 0.1
                
                # Add skill diversity bonus (more total skills = bonus)
                skill_diversity_bonus = min(len(candidate_skills) / 15.0, 0.15)
                
                # Calculate FINAL score with better differentiation
                final_score = (skill_score * 0.5 + experience_score * 0.35 + skill_diversity_bonus * 0.15)
                
                # Ensure scores range from 0.0 to 1.0
                final_score = max(0.0, min(1.0, final_score))
                
                # Convert to percentage
                final_percentage = round(final_score * 100, 2)
                
                print(f"  [{candidate['name']}] Skills matched: {matching_skills}/{len(query_skills)} | " +
                      f"Experience: {candidate_experience}y | Score: {final_percentage}% | " +
                      f"(skill:{skill_score:.2f}, exp:{experience_score:.2f}, div:{skill_diversity_bonus:.2f})")
                
                # Only include candidates that match filters
                if query_skills or min_experience > 0:
                    if (query_skills and matching_skills > 0) or (min_experience > 0 and experience_match):
                        candidate['score'] = final_score
                        candidate['percentage'] = final_percentage
                        candidate['matched_skills'] = matched_skill_names
                        scored_candidates.append(candidate)
                else:
                    candidate['score'] = final_score
                    candidate['percentage'] = final_percentage
                    candidate['matched_skills'] = matched_skill_names
                    scored_candidates.append(candidate)
            
            # Sort by score descending
            scored_candidates.sort(key=lambda x: x['score'], reverse=True)
            
            # Add rank
            for idx, candidate in enumerate(scored_candidates, 1):
                candidate['rank'] = idx
            
            print(f"[SEARCH] Total results: {len(scored_candidates)}\n")
            
            return scored_candidates
        
        except Exception as e:
            print(f"Error searching candidates: {str(e)}")
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
    
    def _extract_experience_years(self, experience_str: str) -> int:
        """Extract years from experience string"""
        import re
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
