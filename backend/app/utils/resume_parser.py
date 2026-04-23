"""Resume parsing utility module"""
import os
from typing import Dict, List, Any

# Try to import optional dependencies
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

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    if not HAS_PYPDF2:
        return "[PDF parsing not available - PyPDF2 not installed]"
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
        return "[DOCX parsing not available - python-docx not installed]"
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

def extract_candidate_info(resume_text: str, spacy_model=None) -> Dict[str, Any]:
    """Extract candidate information from resume text using spaCy"""
    
    # Basic information extraction (will be enhanced with spaCy)
    candidate_info = {
        'name': 'Unknown Candidate',
        'skills': [],
        'experience': 'Not specified',
        'email': None,
        'phone': None
    }
    
    try:
        # Try to extract name from first non-empty line (usually the name is at the top)
        lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
        
        if lines:
            # First non-empty line is usually the name
            potential_name = lines[0]
            # If it's too long or doesn't look like a name, try next line
            if len(potential_name) < 50 and not potential_name.startswith('['):
                candidate_info['name'] = potential_name
            elif len(lines) > 1:
                candidate_info['name'] = lines[1]
        
        # Extract skills (simplified - will improve with NLP model)
        common_skills = [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'PHP', 'Swift', 'Kotlin',
            'SQL', 'PostgreSQL', 'MongoDB', 'MySQL', 'Redis', 'Elasticsearch',
            'React', 'Angular', 'Vue', 'Django', 'Flask', 'FastAPI', 'Spring',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git',
            'Machine Learning', 'Data Science', 'NLP', 'Deep Learning', 'TensorFlow'
        ]
        
        for skill in common_skills:
            if skill.lower() in resume_text.lower():
                candidate_info['skills'].append(skill)
        
        # Extract experience years (improved - try multiple patterns)
        import re
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
        
        # Pattern 3: Look for years in typical formats like "2020-2024" (4 years)
        if experience_found is None:
            matches = re.findall(r'(201\d|202\d|19\d\d)[\s\-]+(?:to\s+)?(201\d|202\d|19\d\d|present|current)', resume_text, re.IGNORECASE)
            if matches:
                # Calculate years from most recent date range
                try:
                    for start, end in matches:
                        if 'present' not in end.lower() and 'current' not in end.lower():
                            years = int(end) - int(start)
                        else:
                            years = 2024 - int(start)
                        if experience_found is None or years > experience_found:
                            experience_found = years
                except:
                    pass
        
        # Set experience with default of 0 if not found
        candidate_info['experience'] = experience_found if experience_found is not None else 0
        
        return candidate_info
    
    except Exception as e:
        print(f"Error extracting candidate info: {str(e)}")
        return candidate_info

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
