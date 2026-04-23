"""Diagnostic test for MongoDB storage"""
import sys
sys.path.insert(0, '.')

from config import Config
from app.services.candidate_service import CandidateService
from database import HAS_PYMONGO

print(f"\n{'='*80}")
print(f"RESUME DATA STORAGE DIAGNOSTIC")
print(f"{'='*80}\n")

print("1️⃣  CONFIGURATION:")
print(f"   - DATABASE_TYPE: {Config.DATABASE_TYPE}")
print(f"   - MONGODB_URI: {Config.MONGODB_URI}")
print(f"   - PyMongo installed: {'✓ YES' if HAS_PYMONGO else '✗ NO'}")

print("\n2️⃣  STORAGE MECHANISM:")
print("   When you upload resumes, data is stored in:")

service = CandidateService()
if service.db:
    print("   ✓ MongoDB Database")
    print(f"     Database: {service.db.name}")
    print("     Status: Connected ✓")
    
    # Check existing data
    try:
        candidates_count = service.db['candidates'].count_documents({})
        print(f"     Candidates stored: {candidates_count}")
    except:
        print("     Could not query collection")
else:
    print("   ⚠️  In-Memory Storage (Fallback)")
    print("     Reason: MongoDB connection failed or not configured")
    print("     Status: Candidates are stored in Python memory")
    print(f"     Current count: {len(CandidateService._candidates_memory)}")
    
    if len(CandidateService._candidates_memory) > 0:
        print("\n   Stored candidates in memory:")
        for i, c in enumerate(CandidateService._candidates_memory[:3], 1):
            print(f"     [{i}] {c.get('name', 'Unknown')} - {len(c.get('skills', []))} skills")

print("\n3️⃣  POSSIBLE ISSUES:")
if service.db is None:
    print("   ❌ MongoDB Connection Failed")
    print("\n   Options to fix:")
    print("   A) Use Local MongoDB:")
    print("      1. Install MongoDB Community Edition")
    print("      2. Start MongoDB: mongod or net start MongoDB")
    print("      3. Create .env file with:")
    print("         DATABASE_TYPE=mongodb")
    print("         MONGODB_URI=mongodb://localhost:27017/candidate_search")
    print("")
    print("   B) Use MongoDB Atlas (Cloud):")
    print("      1. Create cluster at mongodb.com/cloud")
    print("      2. Get connection string")
    print("      3. Add to .env file")
    print("")
    print("   C) Disable MongoDB (use in-memory only):")
    print("      - Data will be lost when server restarts")
    print("      - Good for testing only")
else:
    print("   ✓ MongoDB is connected and working")

print(f"\n{'='*80}")
print("Summary: Resume data will be stored in MongoDB once connection is established")
print(f"{'='*80}\n")
