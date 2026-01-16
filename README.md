
---

# ai_security_advisor

AI-powered code security analyzer.

This service exposes a FastAPI endpoint that accepts a source code file upload, stores a “task” record in a SQLAlchemy-backed database, and processes the file asynchronously.
The code is **first analyzed using Semgrep (static analysis)** and the findings are then **passed to Mistral AI for higher-level reasoning, prioritization, and recommendations** (with Gemini as fallback).

The system also supports **Server-Sent Events (SSE)** to notify clients in real time when analysis tasks are **completed or failed**.

---

## Features

* File upload API for security analysis (`POST /analyze/`)
* Static analysis using **Semgrep**
* AI-based enrichment using **Mistral AI** (with Gemini fallback)
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
   * Passes Semgrep findings + source context to **Mistral AI**
   * Mistral generates risk assessment, severity, and recommendations (falls back to Gemini if needed)
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
  `core/mistral.py`
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

### 2. Mistral AI (Primary AI Enrichment)
* Receives:

  * Original source code
  * Semgrep findings
* Falls back to Gemini if Mistral is unavailable
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
* `mistralai`
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
MISTRAL_API_KEY=your_mistral_api_key_here
REDIS_URL=redis://localhost:6379/0
REDIS_CELERY_BROKER=redis://localhost:6379/0
```

---

## Why This Design

* **Semgrep** provides fast, deterministic static analysis
* **Mistral AI** adds context-aware reasoning and prioritization (with Gemini fallback)
* **Celery + Redis** decouple API responsiveness from heavy analysis
* **SSE** enables real-time UX without polling
* Clean separation between API, analysis, and storage layers

---


## Adding New AI Providers

Feel free to modify the system to use any LLM that has mastered coding and vulnerability analysis! The architecture is designed for easy extension:

### To add a new AI provider:

1. **Create a new provider file** in `core/` (e.g., `core/openai.py`, `core/claude.py`)

2. **Implement the required function** with this signature:
   ```python
   def generate_content_{provider}(instruction: str, context: str) -> dict:
       # Your LLM API call logic here
       # Return parsed JSON result or None on failure
   ```

3. **Add the provider to the model dictionary** in [core/ai.py]
   ```python
   model_providers = {
       "mistral": generate_content_mistral,
       "gemini": gemini_generate_content,
       "your_provider": generate_content_your_provider,  # Add this
   }
   ```

4. **Add API key to config**:
   ```python
   # config.py
   YOUR_PROVIDER_API_KEY: str
   ```

5. **Update requirements.txt** with the necessary SDK

### Example provider structure:
```python
# core/openai.py
from openai import OpenAI
from config import settings
from utils.to_json import to_json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_content_openai(instruction: str, context: str) -> dict:
    try:
        content = instruction + "\n\n" + context
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": content}]
        )
        return to_json(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return None
```

The system will automatically try all available providers in order and use the first one that succeeds, providing built-in redundancy and fallback support.

---


