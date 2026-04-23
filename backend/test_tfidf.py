"""Test script to verify TF-IDF is working and scoring is differentiated"""

import sys
sys.path.insert(0, '.')

from app.utils.tfidf_resume_parser import extract_skills_tfidf, extract_candidate_info, HAS_TFIDF
from app.services.candidate_service import CandidateService

print(f"\n{'='*80}")
print(f"TF-IDF STATUS: {'✓ ACTIVE' if HAS_TFIDF else '✗ FALLBACK TO REGEX'}")
print(f"{'='*80}\n")

# Test Case 1: Python Developer
resume1 = """
John Smith
Python Developer
john.smith@email.com

Experience:
- 5 years of Python development
- Django and Flask frameworks
- PostgreSQL and MongoDB
- AWS and Docker

Skills: Python, Django, Flask, PostgreSQL, MongoDB, AWS, Docker, Linux, Git
"""

# Test Case 2: Java Developer
resume2 = """
Jane Doe
Senior Java Engineer
jane.doe@email.com

Experience:
- 8 years of Java programming
- Spring and Spring Boot
- MySQL and Oracle
- AWS and Kubernetes

Skills: Java, Spring, Spring Boot, MySQL, Oracle, AWS, Kubernetes, Git, Docker, CI/CD
"""

# Test Case 3: React Developer
resume3 = """
Bob Johnson
Frontend Developer
bob.johnson@email.com

Experience:
- 3 years of experience with React
- Angular and Vue.js
- TypeScript and JavaScript
- Node.js and Express

Skills: React, Angular, Vue, TypeScript, JavaScript, Node.js, Express, CSS, HTML, Webpack
"""

print("\n[TEST 1] Extracting skills from Python Developer resume:")
print("-" * 60)
skills1 = extract_skills_tfidf(resume1)
print(f"Skills extracted: {skills1}\n")

print("[TEST 2] Extracting skills from Java Developer resume:")
print("-" * 60)
skills2 = extract_skills_tfidf(resume2)
print(f"Skills extracted: {skills2}\n")

print("[TEST 3] Extracting skills from React Developer resume:")
print("-" * 60)
skills3 = extract_skills_tfidf(resume3)
print(f"Skills extracted: {skills3}\n")

# Now test scoring differentiation
print("\n" + "="*80)
print("SCORING DIFFERENTIATION TEST")
print("="*80)

service = CandidateService()

# Store test candidates
class FakeCandidate:
    def get(self, key, default=None):
        data = {
            'name': self.name,
            'skills': self.skills,
            'experience': self.experience
        }
        return data.get(key, default)

# Create mock candidates in memory
CandidateService._candidates_memory = []

test_candidates = [
    {'id': '1', 'name': 'John (Python)', 'skills': skills1, 'experience': '5 years', 'embedding': None},
    {'id': '2', 'name': 'Jane (Java)', 'skills': skills2, 'experience': '8 years', 'embedding': None},
    {'id': '3', 'name': 'Bob (React)', 'skills': skills3, 'experience': '3 years', 'embedding': None},
]

for candidate in test_candidates:
    CandidateService._candidates_memory.append(candidate)

# Test Search 1: Looking for Python developers
print("\n[SEARCH 1] Searching for: Python developers with 2+ years experience")
print("-" * 60)
results1 = service.search_candidates("Python", {'skills': ['Python'], 'minExperience': 2})
for r in results1:
    print(f"  Rank {r['rank']}: {r['name']:20} -> {r.get('percentage', 'N/A')}% (matched: {r.get('matched_skills', [])})")

# Test Search 2: Looking for Java developers
print("\n[SEARCH 2] Searching for: Java developers with 5+ years experience")
print("-" * 60)
results2 = service.search_candidates("Java", {'skills': ['Java'], 'minExperience': 5})
for r in results2:
    print(f"  Rank {r['rank']}: {r['name']:20} -> {r.get('percentage', 'N/A')}% (matched: {r.get('matched_skills', [])})")

# Test Search 3: Looking for React developers
print("\n[SEARCH 3] Searching for: React developers with 1+ years experience")
print("-" * 60)
results3 = service.search_candidates("React", {'skills': ['React'], 'minExperience': 1})
for r in results3:
    print(f"  Rank {r['rank']}: {r['name']:20} -> {r.get('percentage', 'N/A')}% (matched: {r.get('matched_skills', [])})")

# Test Search 4: Multiple skills
print("\n[SEARCH 4] Searching for: Python + Django + Docker developers with 3+ years experience")
print("-" * 60)
results4 = service.search_candidates("Python Django Docker", 
                                    {'skills': ['Python', 'Django', 'Docker'], 'minExperience': 3})
for r in results4:
    print(f"  Rank {r['rank']}: {r['name']:20} -> {r.get('percentage', 'N/A')}% (matched: {r.get('matched_skills', [])})")

print("\n" + "="*80)
print(f"✓ TEST COMPLETED - TF-IDF is {'ACTIVE' if HAS_TFIDF else 'USING REGEX FALLBACK'}")
print("="*80 + "\n")

print("✓ If you see different percentages for different searches, TF-IDF scoring is working!")
print("✓ If all scores are the same, check the console logs for '[USING TF-IDF METHOD' or '[USING REGEX METHOD'\n")
