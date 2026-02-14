# Resonance AI – API Usage Guide

Base URL: `http://localhost:8000` (or your deployed URL)  
API prefix: `/api/v1`

Interactive docs: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

---

## Quick Start

```bash
# Health check
curl http://localhost:8000/health
# {"status":"ok","app":"Resonance AI - Call Monitoring"}
```

---

## 1. Upload Audio for Transcription & Analysis

Upload an audio file to transcribe it with Whisper and run AI analysis via Gemini.

**Endpoint:** `POST /api/v1/upload`

**Supported formats:** `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.webm`, `.mp4`

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@/path/to/call-recording.mp3"
```

**Example (JavaScript fetch):**
```javascript
const formData = new FormData();
formData.append('file', audioFile);

const response = await fetch('http://localhost:8000/api/v1/upload', {
  method: 'POST',
  body: formData,
});
const data = await response.json();
console.log(data.call_id);  // UUID of the created call
```

**Response:**
```json
{
  "message": "Upload processed",
  "call_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "call-recording.mp3"
}
```

---

## 2. List Calls

**Endpoint:** `GET /api/v1/calls`

**Query parameters:**

| Parameter | Type   | Description                              |
|-----------|--------|------------------------------------------|
| `source`  | string | Filter: `upload`                         |
| `limit`   | int    | Max results (1–100, default 50)          |
| `offset`  | int    | Pagination offset (default 0)            |

**Example:**
```bash
# All calls
curl http://localhost:8000/api/v1/calls

# Filter by source
curl "http://localhost:8000/api/v1/calls?source=upload"

# Pagination
curl "http://localhost:8000/api/v1/calls?limit=10&offset=20"
```

**Response:**
```json
{
  "calls": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "source": "upload",
      "external_id": "call-recording.mp3",
      "started_at": null,
      "ended_at": null,
      "metadata": null,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

## 3. Get Call Details

Retrieve a single call with transcript segments and analyses.

**Endpoint:** `GET /api/v1/calls/{call_id}`

**Example:**
```bash
curl http://localhost:8000/api/v1/calls/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "source": "upload",
  "external_id": "call-recording.mp3",
  "started_at": null,
  "ended_at": null,
  "metadata": null,
  "created_at": "2024-01-15T10:30:00Z",
  "segments": [
    {
      "id": "...",
      "call_id": "...",
      "speaker": "unknown",
      "text": "Hello, how can I help you today?",
      "start_time_ms": 0,
      "end_time_ms": 2500
    }
  ],
  "analyses": [
    {
      "id": "...",
      "call_id": "...",
      "analysis_type": "post_call",
      "payload": {
        "customer_satisfaction_score": 4,
        "questions_answered_correctly": true,
        "unanswered_questions": [],
        "resolution_status": "resolved",
        "key_topics": ["billing", "refund"],
        "agent_performance_notes": "Agent was helpful and resolved the issue.",
        "summary": "Customer called about a billing discrepancy. Agent verified the issue and processed a refund."
      },
      "created_at": "2024-01-15T10:30:05Z"
    }
  ]
}
```

---

## 4. List Analyses

**Endpoint:** `GET /api/v1/analyses`

**Query parameters:**

| Parameter      | Type   | Description                          |
|----------------|--------|--------------------------------------|
| `call_id`      | UUID   | Filter by call ID                    |
| `analysis_type`| string | Filter: `post_call`                  |
| `limit`        | int    | Max results (1–100, default 50)      |
| `offset`       | int    | Pagination offset (default 0)        |

**Example:**
```bash
curl "http://localhost:8000/api/v1/analyses?call_id=550e8400-e29b-41d4-a716-446655440000"
curl "http://localhost:8000/api/v1/analyses?analysis_type=post_call"
```

**Response:**
```json
{
  "analyses": [
    {
      "id": "...",
      "call_id": "550e8400-e29b-41d4-a716-446655440000",
      "analysis_type": "post_call",
      "payload": { ... },
      "created_at": "2024-01-15T10:30:05Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

## Analysis Payload Types

### Post-call analysis (`analysis_type: "post_call"`)

```json
{
  "customer_satisfaction_score": 1-5,
  "questions_answered_correctly": true/false,
  "unanswered_questions": ["question 1", "question 2"],
  "resolution_status": "resolved|partial|unresolved",
  "key_topics": ["billing", "technical_issue", "refund"],
  "agent_performance_notes": "string",
  "summary": "2-3 sentence summary"
}
```

---

## Error Responses

| Status | Description                    |
|--------|--------------------------------|
| 404    | Call not found                 |
| 422    | Validation error (bad request)  |
| 500    | Server error                   |

Example 404:
```json
{
  "detail": "Call not found"
}
```

---

## Typical Workflows

### 1. Upload a recording file

1. `POST /api/v1/upload` with `file`
2. `GET /api/v1/calls/{call_id}` to view transcript and analysis

### 2. Query for reporting

1. `GET /api/v1/calls?source=upload&limit=100` – list calls
2. `GET /api/v1/analyses?analysis_type=post_call` – list all post-call analyses
3. For each call, `GET /api/v1/calls/{id}` for full details
