# Resonance AI - Call Monitoring Backend

Standalone REST API for transcribing and analyzing customer support calls.

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
   - `DATABASE_URL` - Supabase or PostgreSQL connection string
   - `AWS_REGION`, `BEDROCK_MODEL_ID` - For Bedrock (or use `LLM_PROVIDER=ollama`)

4. Run migrations:
   ```powershell
   cd backend
   alembic upgrade head
   ```

5. Start the server (from project root):
   ```powershell
   .\run.ps1
   ```
   Or manually:
   ```powershell
   .\venv\Scripts\Activate.ps1
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API

- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- API prefix: `/api/v1`
