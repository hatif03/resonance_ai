# Resonance AI

**How Resonant uses AI to extract structured data points from audio and turn them into long-term business intelligence.**

## What This Does

Customer calls are one of the richest — and most underused — sources of business insight. Every conversation contains signals about satisfaction, product gaps, recurring issues, and agent effectiveness, but those signals are locked inside raw audio that nobody has time to re-listen to.

Resonance AI solves this by building an automated pipeline that:

1. **Ingests** call recordings (upload any common audio format).
2. **Transcribes** them locally with Whisper, producing timestamped, speaker-attributed text.
3. **Analyzes** the transcript with an LLM (Gemini or Ollama) and extracts structured data points:
   - Customer satisfaction score (1-5)
   - Whether the customer's questions were answered correctly
   - Unanswered questions that fell through the cracks
   - Resolution status (resolved / partial / unresolved)
   - Key topics discussed (billing, refund, technical issue, etc.)
   - Agent performance notes
   - A concise call summary

Every data point is stored in a structured database, queryable via a REST API. Over time this creates a growing dataset that can power dashboards, trend analysis, agent coaching programs, product feedback loops, and any other long-term business goal that benefits from understanding what customers are actually saying.

## Architecture

```
Audio File ──> Whisper (local transcription)
                   │
                   v
             Transcript + Segments
                   │
                   v
             LLM Analysis (Gemini / Ollama)
                   │
                   v
           Structured Data Points ──> Database (SQLite / Supabase)
                                          │
                                          v
                                    REST API ──> Dashboards, Reports, BI tools
```

## Setup

1. Create and activate the virtual environment (from project root):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```powershell
   pip install -r backend\requirements.txt
   ```

3. Copy `backend/.env.example` to `backend/.env` and configure:
   - `DATABASE_URL` — works out of the box with local SQLite; switch to Supabase PostgreSQL for production
   - `GEMINI_API_KEY` — get a free key at https://aistudio.google.com/apikey (or set `LLM_PROVIDER=ollama` for local inference)

4. Start the server:
   ```powershell
   .\venv\Scripts\Activate.ps1
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

Tables are created automatically on first startup — no manual migration needed for development.

## API

- **Interactive docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health
- **API prefix:** `/api/v1`
- **Full usage guide:** [docs/API_GUIDE.md](../docs/API_GUIDE.md)

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload` | Upload audio — triggers transcription and analysis |
| `GET` | `/api/v1/calls` | List all processed calls |
| `GET` | `/api/v1/calls/{id}` | Get call detail with transcript and analysis |
| `GET` | `/api/v1/analyses` | Query extracted data points across all calls |

## Processing Later for Long-Term Goals

The structured data points extracted from each call are designed to be consumed downstream:

- **Trend dashboards** — track satisfaction scores, resolution rates, and hot topics over weeks and months.
- **Agent coaching** — surface performance notes and unanswered-question patterns to improve training.
- **Product feedback** — aggregate key topics to identify what customers care about most.
- **Compliance & QA** — searchable transcripts with timestamps for audit trails.
- **Custom analytics** — the REST API and database are open for any BI tool, notebook, or pipeline to query.
