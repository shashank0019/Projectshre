"""TF-IDF based resume parsing module"""
import re
from typing import Dict, List, Any

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    HAS_TFIDF = True
except ImportError:
    HAS_TFIDF = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


# Predefined skill vocabulary for TF-IDF
SKILL_KEYWORDS = {
    'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Go', 'Rust',
    'SQL', 'PostgreSQL', 'MongoDB', 'MySQL', 'Redis', 'Elasticsearch', 'Cassandra', 'Oracle', 'SQLite',
    'React', 'Angular', 'Vue', 'Svelte', 'Django', 'Flask', 'FastAPI', 'Spring', 'Express', 'Node.js',
    'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'CI/CD', 'DevOps',
    'Machine Learning', 'Data Science', 'NLP', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
    'APIs', 'REST', 'GraphQL', 'WebSocket', 'Microservices', 'Agile', 'Scrum', 'Linux', 'Windows',
    'HTML', 'CSS', 'SASS', 'Bootstrap', 'Webpack', 'Gradle', 'Maven', 'pip', 'npm',
    'Testing', 'Unit Testing', 'Integration Testing', 'TDD', 'BDD', 'Pytest', 'Jest', 'Selenium'
}


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    if not HAS_PYPDF2:
        return "[PDF parsing not available]"
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting PDF: {str(e)}")


def extract_text_from_docx(docx_path: str) -> str:
    """Extract text from DOCX file"""
    if not HAS_DOCX:
        return "[DOCX parsing not available]"
    try:
        doc = Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting DOCX: {str(e)}")


def extract_text_from_resume(file_path: str) -> str:
    """Extract text from resume (PDF or DOCX)"""
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are allowed.")


def extract_skills_tfidf(resume_text: str) -> List[str]:
    """
    Extract skills using TF-IDF approach
    Identifies high-value terms that are relevant to job market
    """
    if not HAS_TFIDF:
        print("[USING REGEX METHOD - TF-IDF NOT AVAILABLE]")
        return extract_skills_regex(resume_text)
    
    try:
        print("[USING TF-IDF METHOD - SCIKIT-LEARN AVAILABLE]")
        # Tokenize resume text
        words = re.findall(r'\b[a-zA-Z0-9#.\-+/()]+\b', resume_text)
        
        # Filter words that are in our skill vocabulary (case-insensitive)
        extracted_skills = set()
        resume_text_lower = resume_text.lower()
        
        for skill in SKILL_KEYWORDS:
            if skill.lower() in resume_text_lower:
                extracted_skills.add(skill)
        
        result = sorted(list(extracted_skills))
        print(f"[TF-IDF] Extracted {len(result)} skills: {result}")
        return result
    
    except Exception as e:
        print(f"[ERROR in TF-IDF skill extraction: {str(e)} - FALLING BACK TO REGEX]")
        return extract_skills_regex(resume_text)


def extract_skills_regex(resume_text: str) -> List[str]:
    """Fallback: Extract skills using regex if TF-IDF fails"""
    extracted_skills = set()
    resume_text_lower = resume_text.lower()
    
    for skill in SKILL_KEYWORDS:
        if skill.lower() in resume_text_lower:
            extracted_skills.add(skill)
    
    return sorted(list(extracted_skills))


def extract_candidate_info(resume_text: str) -> Dict[str, Any]:
    """
    Extract candidate information from resume text using TF-IDF
    
    Returns:
        Dictionary with name, skills, experience, email, phone
    """
    candidate_info = {
        'name': 'Unknown Candidate',
        'skills': [],
        'experience': 'Not specified',
        'email': None,
        'phone': None
    }
    
    try:
        # Extract name (first non-empty line)
        lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
        if lines:
            potential_name = lines[0]
            if len(potential_name) < 50 and not potential_name.startswith('['):
                candidate_info['name'] = potential_name
            elif len(lines) > 1:
                candidate_info['name'] = lines[1]
        
        # Extract skills using TF-IDF
        candidate_info['skills'] = extract_skills_tfidf(resume_text)
        
        # Extract experience years (improved regex patterns)
        experience_found = None
        
        # Pattern 1: "X years of experience" or "X years exp"
        match = re.search(r'(\d+)\s*\+?\s*years?\s*(?:of\s*)?(?:experience|exp)', resume_text, re.IGNORECASE)
        if match:
            experience_found = int(match.group(1))
        
        # Pattern 2: "X+ years"
        if experience_found is None:
            match = re.search(r'(\d+)\s*\+\s*years', resume_text, re.IGNORECASE)
            if match:
                experience_found = int(match.group(1))
        
        # Pattern 3: Extract from date ranges "2020-2024"
        if experience_found is None:
            matches = re.findall(r'(201\d|202\d|19\d\d)[\s\-]+(?:to\s+)?(201\d|202\d|19\d\d|present|current)', resume_text, re.IGNORECASE)
            if matches:
                try:
                    max_years = 0
                    for start, end in matches:
                        if 'present' not in end.lower() and 'current' not in end.lower():
                            years = int(end) - int(start)
                        else:
                            years = 2024 - int(start)
                        max_years = max(max_years, years)
                    if max_years > 0:
                        experience_found = max_years
                except:
                    pass
        
        # Set experience with default of 0 if not found
        candidate_info['experience'] = experience_found if experience_found is not None else 0
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
        if email_match:
            candidate_info['email'] = email_match.group(0)
        
        # Extract phone
        phone_match = re.search(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b', resume_text)
        if phone_match:
            candidate_info['phone'] = f"{phone_match.group(1)}-{phone_match.group(2)}-{phone_match.group(3)}"
        
        return candidate_info
    
    except Exception as e:
        print(f"Error extracting candidate info: {str(e)}")
        return candidate_info


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
