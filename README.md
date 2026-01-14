
---

# ai_security_advisor

AI-powered code security analyzer.

This service exposes a FastAPI endpoint that accepts a source code file upload, stores a “task” record in a SQLAlchemy-backed database, and processes the file asynchronously.
The code is **first analyzed using Semgrep (static analysis)** and the findings are then **passed to Google Gemini for higher-level reasoning, prioritization, and recommendations**.

The system also supports **Server-Sent Events (SSE)** to notify clients in real time when analysis tasks are **completed or failed**.

---

## Features

* File upload API for security analysis (`POST /analyze/`)
* Static analysis using **Semgrep**
* AI-based enrichment using **Google Gemini**
* Async/background processing using **Celery + Redis**
* Task tracking stored in a SQL database (SQLite supported via `DATABASE_URL`)
* Results retrieval by `task_id`
* Real-time **SSE notifications** for task status updates
* Structured JSON output (severity, vulnerabilities, recommendations, score)

---

## Architecture / Data Flow

### High-level flow

1. Client uploads a source code file via `POST /analyze/`
2. API stores the file and creates a `Task` record with status `pending`
3. Background worker processes the task:

   * Runs **Semgrep** on the uploaded file
   * Passes Semgrep findings + source context to **Gemini**
   * Gemini generates risk assessment, severity, and recommendations
4. Task status is updated to `completed` or `failed`
5. Clients can:

   * Fetch results via REST
   * Subscribe to **SSE** for real-time updates

---

### Detailed flow

* **API layer**
  `app.py`
  `apis/analyze_apis.py`

* **Persistence**
  `db/database.py`
  `db/models/tasks.py`

* **Background processing**
  `celery_app.py`
  `tasks/process_file.py`

* **Static analysis**
  `semgrep` (invoked from the worker)

* **AI integration**
  `core/ai.py`
  `core/gemini.py`

* **Notifications**
  SSE endpoint for task status updates

---

## Analysis Pipeline

### 1. Semgrep (Static Analysis)

* Runs first on the uploaded source file
* Detects:

  * Common vulnerabilities
  * Insecure patterns
  * Language-specific security issues
* Produces structured findings (rules, locations, severity)

### 2. Gemini (AI Enrichment)

* Receives:

  * Original source code
  * Semgrep findings
* Performs:

  * Contextual reasoning
  * Risk prioritization
  * False-positive reduction
  * Actionable security recommendations
* Produces a final JSON report

This hybrid approach combines **deterministic static analysis** with **LLM-based reasoning**.

---

## API Endpoints

### Upload & start analysis

```
POST /analyze/
```

* Multipart file upload
* Creates a new task with status `pending`
* Enqueues background processing

---

### Get analysis result

```
GET /analyze/results/{task_id}
```

Returns:

* `pending` → analysis in progress
* `completed` → full analysis result
* `failed` → task failed (no result payload)

---

### List analysis tasks

```
GET /analyze/tasks
```

Returns paginated task metadata (id, filename, status, timestamps).

---

### SSE: Task status notifications

```
GET /analyze/events
```

* Server-Sent Events stream
* Emits events when tasks are:

  * completed
  * failed

Useful for:

* Live dashboards
* Auto-refreshing UIs
* Removing polling on the frontend

---

## Example Result Structure

```json
{
  "analysis_id": "uuid",
  "overall_severity": "Low",
  "score": 90,
  "vulnerabilities": [],
  "recommendations": [
    "Validate and sanitize all user inputs.",
    "Avoid logging sensitive data."
  ]
}
```

---

## Requirements

* Python 3.10+ recommended
* Redis (required for Celery background processing)
* Semgrep (CLI must be available)
* Google Gemini API key

Key Python dependencies (see `requirements.txt`):

* `fastapi`, `uvicorn`
* `celery`, `redis`
* `sqlalchemy`
* `google-genai`
* `pydantic-settings`
* `aiofiles`
* `semgrep`

---

## Configuration (.env)

This project uses `pydantic-settings` and reads environment variables from `.env`.

Create a `.env` file in the repo root:

```env
DATABASE_URL=sqlite:///./security_advisor.db
GEMINI_API_KEY=your_gemini_api_key_here
REDIS_URL=redis://localhost:6379/0
REDIS_CELERY_BROKER=redis://localhost:6379/0
```

---

## Why This Design

* **Semgrep** provides fast, deterministic static analysis
* **Gemini** adds context-aware reasoning and prioritization
* **Celery + Redis** decouple API responsiveness from heavy analysis
* **SSE** enables real-time UX without polling
* Clean separation between API, analysis, and storage layers

---

