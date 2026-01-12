# ai_security_advisor

AI-powered code security analyzer.

This service exposes a FastAPI endpoint that accepts a source code file upload, stores a “task” record in a SQLAlchemy-backed database, and (optionally) processes the file asynchronously via Celery + Redis. The analysis is performed using Google Gemini and stored back into the task record.

## Features

- File upload API for security analysis (`/analyze/`)
- Async/background processing using Celery + Redis
- Task tracking stored in a SQL database (SQLite supported via `DATABASE_URL`)
- Results retrieval by `task_id`
- Gemini-based analysis that returns a JSON structure (vulnerabilities, severity, recommendations, score)

## Architecture / Data Flow

- **API layer**: `app.py` + [apis/analyze_apis.py](cci:7://file://wsl.localhost/Ubuntu/home/vishnu/SideQuest/ai_security_advisor/apis/analyze_apis.py:0:0-0:0)
- **Persistence**: `db/database.py` + `db/models/tasks.py`
- **Background processing**: `celery_app.py` + `tasks/process_file.py`
- **AI integration**: `core/ai.py` + [core/gemini.py](cci:7://file://wsl.localhost/Ubuntu/home/vishnu/SideQuest/ai_security_advisor/core/gemini.py:0:0-0:0)

Flow:
1. `POST /analyze/` uploads a file into `uploads/` and creates a `Task` row with status `pending`.
2. The API tries to enqueue Celery job `process_uploaded_file(task_id)`.
3. Worker loads the file from disk, calls `core.ai.analyze_code_security(...)`, and stores the JSON result into `Task.result`.
4. `GET /analyze/results/{task_id}` returns status + stored analysis.

## Requirements

- Python 3.10+ recommended
- Redis (required if you want background processing via Celery)
- A Gemini API key

Key Python dependencies (see [requirements.txt](cci:7://file://wsl.localhost/Ubuntu/home/vishnu/SideQuest/ai_security_advisor/requirements.txt:0:0-0:0)):
- `fastapi`, `uvicorn`
- `celery`, `redis`
- `sqlalchemy`
- `google-genai`
- `pydantic-settings`
- `aiofiles`

## Configuration (.env)

This project uses `pydantic-settings` and reads environment variables from `.env` (see `config.py`).

Create a `.env` file in the repo root:

```env
DATABASE_URL=sqlite:///./security_advisor.db
GEMINI_API_KEY=your_gemini_api_key_here
REDIS_URL=redis://localhost:6379/0
REDIS_CELERY_BROKER=redis://localhost:6379/0
```