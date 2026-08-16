# HireLens ATS Scanner

HireLens is an explainable resume-to-job matching platform. It combines a deterministic ATS-style scoring engine with optional Groq-generated coaching, so the application remains fully usable without an API key while still supporting richer AI feedback when credentials are configured.

## What it does

- scores resume/job alignment from 0–100
- reports keyword overlap and missing role terminology
- detects requested technical skills and skill gaps
- evaluates ATS-friendly section completeness
- rewards measurable achievement/impact signals
- computes a readability signal
- provides strengths, improvement actions, and ATS tips
- accepts pasted text through the web/API and PDF or text uploads through the file API
- optionally enriches coaching with Groq without allowing the model to fabricate credentials

## Architecture

```text
Browser / API client
        |
        v
FastAPI control layer (hirelens/api.py)
        |
        +--> deterministic scoring (hirelens/scoring.py)
        |       keyword / skill / section / impact / readability
        |
        +--> optional Groq enrichment (hirelens/ai.py)
        |
        +--> PDF text extraction (hirelens/parsing.py)
        |
        v
Structured AnalysisResponse
```

The deterministic score remains the source of truth. Groq can improve the prose coaching but does not replace or secretly alter the numeric score.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open:

- dashboard: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- health: `http://localhost:8000/health`

No API key is required for deterministic analysis.

## Optional Groq insights

```bash
cp .env.example .env
```

Add your key:

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Export the environment variables or use Docker Compose. If Groq is missing/unavailable, HireLens automatically falls back to deterministic mode.

## Docker

```bash
cp .env.example .env
docker compose up --build
```

The image runs as a non-root user and exposes a container health check.

## API

### JSON analysis

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "resume": "Summary ... Skills ... Experience ...",
    "job_description": "We are hiring a Python data engineer ...",
    "use_ai": false
  }'
```

### PDF/text upload

```bash
curl -X POST http://localhost:8000/api/v1/analyze-file \
  -F 'resume=@resume.pdf' \
  -F 'job_description=We need a Python SQL data engineer with Docker and AWS...' \
  -F 'use_ai=false'
```

Uploads are limited to 5 MB and currently support PDF and plain text.

## Scoring model

The final deterministic score is a weighted composite:

- keyword match: 35%
- explicit skill match: 30%
- ATS section quality: 15%
- quantified impact/achievement signals: 15%
- readability: 5%

The result also exposes the complete breakdown so users can see *why* the score moved instead of receiving a black-box percentage.

## Tests and quality checks

```bash
pytest -q
python -m compileall app.py hirelens
```

or:

```bash
make check
```

GitHub Actions runs tests, compiles the Python package, and builds the Docker image on pull requests and pushes to `main`.

## Project structure

```text
.
├── app.py
├── hirelens/
│   ├── api.py
│   ├── ai.py
│   ├── parsing.py
│   ├── schemas.py
│   ├── scoring.py
│   ├── service.py
│   └── static/index.html
├── tests/
│   ├── test_api.py
│   └── test_scoring.py
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── requirements.txt
└── .github/workflows/ci.yml
```

## Engineering boundaries

HireLens is an educational/portfolio ATS analysis system, not an official scoring implementation from a specific applicant-tracking vendor. Real ATS products use proprietary parsing, ranking, recruiter configuration, and workflow rules. The score should therefore be treated as an explainable resume-tailoring signal, not as a guarantee of interview selection.

For production deployment, add authentication, request rate limits, encrypted persistent storage if resumes are retained, secrets management, observability, and an explicit data-retention policy. HireLens does not need to store uploaded resume content to perform the current synchronous analysis.

## License

MIT.
