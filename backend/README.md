# AI-Powered Candidate Search Bot - Backend

Python-based backend (Flask) for the candidate search system with resume parsing and semantic search.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

### 3. Setup Database

#### MongoDB (Recommended for initial setup)
```bash
# Install MongoDB locally or use MongoDB Atlas
# Update MONGODB_URI in .env
```

#### PostgreSQL (Alternative)
```bash
# Install PostgreSQL
# Update POSTGRESQL_URI in .env
# Change DATABASE_TYPE to 'postgresql' in .env
```

### 4. Run the Application

```bash
python run.py
```

Backend will be available at `http://localhost:5000`

## Project Structure

```
backend/
├── app/
│   ├── routes/
│   │   └── candidate_routes.py     # API endpoints
│   ├── services/
│   │   └── candidate_service.py    # Business logic
│   ├── utils/
│   │   ├── resume_parser.py        # Resume extraction
│   │   └── embedding_utils.py      # Embedding generation
│   └── __init__.py
├── config.py                        # Configuration
├── database.py                      # Database initialization
├── models.py                        # Data models
├── app_factory.py                   # Flask app factory
├── run.py                           # Entry point
├── requirements.txt                 # Dependencies
├── .env.example                     # Environment template
└── uploads/                         # Resume uploads (temporary)
```

## API Endpoints

### Health Check
- `GET /api/health` - Check backend status

### Candidates
- `GET /api/candidates` - Get all candidates
- `GET /api/candidates/<id>` - Get specific candidate
- `POST /api/candidates/upload` - Upload resumes
- `POST /api/candidates/search` - Search candidates
- `DELETE /api/candidates` - Delete all candidates
- `PUT /api/candidates/<id>/status` - Update candidate status

## Features

- 📤 Resume upload (PDF/DOCX)
- 🔍 Text extraction from resumes
- 📊 Candidate data extraction (Name, Skills, Experience)
- 🧠 Vector embeddings (placeholder for Sentence-BERT)
- 🎯 Semantic search with ranking
- 🗄️ MongoDB/PostgreSQL support
- 🔐 CORS-enabled for Angular frontend

## Notes

- Embeddings are currently placeholders (all-zero vectors)
- Models will be integrated when ready
- Database connection must be active before starting the app
