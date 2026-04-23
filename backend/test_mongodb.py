"""Test MongoDB connection and data storage"""
import sys
sys.path.insert(0, '.')

from database import get_mongodb_client, get_mongodb_db, HAS_PYMONGO
from config import Config

print(f"\n{'='*80}")
print(f"MONGODB TEST")
print(f"{'='*80}\n")

# Check if pymongo is installed
print(f"1. PyMongo installed: {'✓ YES' if HAS_PYMONGO else '✗ NO'}")

if not HAS_PYMONGO:
    print("\n❌ PyMongo is not installed. Install it with: pip install pymongo")
    sys.exit(1)

# Check MongoDB URI configuration
print(f"2. MongoDB URI: {Config.MONGODB_URI}")

# Try to connect to MongoDB
print(f"\n3. Attempting to connect to MongoDB...")
client = get_mongodb_client()

if not client:
    print("❌ MongoDB connection FAILED!")
    print("\nPossible reasons:")
    print("  - MongoDB server is not running")
    print("  - Connection string is incorrect")
    print("  - Firewall is blocking the connection")
    print("\nTo start MongoDB:")
    print("  - Windows: mongod.exe or 'net start MongoDB'")
    print("  - Linux: sudo systemctl start mongod")
    print("  - macOS: brew services start mongodb-community")
    sys.exit(1)

print("✓ MongoDB connection SUCCESSFUL!")

# Get database
db = get_mongodb_db()
if not db:
    print("❌ Could not get database")
    sys.exit(1)

print(f"✓ Connected to database: {db.name}")

# Check collections
print(f"\n4. Collections in database:")
collections = db.list_collection_names()
if collections:
    for col in collections:
        print(f"   - {col}")
else:
    print("   (No collections yet)")

# Check candidates collection
print(f"\n5. Checking 'candidates' collection:")
candidates_collection = db['candidates']
candidate_count = candidates_collection.count_documents({})
print(f"   Total candidates: {candidate_count}")

if candidate_count > 0:
    print(f"\n   Sample candidates:")
    # Show first 3 candidates
    for i, candidate in enumerate(candidates_collection.find().limit(3), 1):
        print(f"\n   [{i}] {candidate.get('name', 'N/A')}")
        print(f"       Skills: {', '.join(candidate.get('skills', []))}")
        print(f"       Experience: {candidate.get('experience', 'N/A')}")
        print(f"       ID: {candidate.get('id', 'N/A')}")
else:
    print("   ℹ No candidates uploaded yet")

print(f"\n{'='*80}")
print(f"✓ MONGODB STATUS: OPERATIONAL")
print(f"{'='*80}\n")
