export interface Candidate {
  id: string;
  name: string;
  skills: string[];
  experience: string;
  score: number;
  rank: number;
  percentage?: number;
  matched_skills?: string[];
  mcqScore?: number;
  resumeText?: string;
}

export interface SearchQuery {
  query: string;
  filters?: {
    skills?: string[];
    minExperience?: number;
    maxExperience?: number;
  };
}

export interface SearchResponse {
  candidates: Candidate[];
  total: number;
  timestamp: string;
}
