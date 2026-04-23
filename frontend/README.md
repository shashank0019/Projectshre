# AI-Powered Candidate Search Bot - Frontend

Angular-based frontend for the candidate search system with resume upload and semantic search capabilities.

## Quick Start

```bash
npm install
npm start
```

The application will be available at `http://localhost:4200`

## Project Structure

```
src/
├── app/
│   ├── components/
│   │   ├── dashboard/          # Main upload & stats dashboard
│   │   └── candidate-search/   # Search interface
│   ├── models/
│   │   └── candidate.model.ts  # Data models
│   ├── services/
│   │   └── candidate.service.ts # API communication
│   └── app.component.ts        # Root component
├── environments/               # Environment configs
├── styles.css                  # Global styles
└── index.html                  # Main HTML
```

## Features

- 📤 Resume upload (PDF/DOCX)
- 🔍 Semantic search
- 📊 Candidate statistics
- 🎯 Ranked results with scoring

## Environment Configuration

Update `src/environments/environment.ts` to match your backend URL.
