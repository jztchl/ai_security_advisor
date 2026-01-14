from fastapi.responses import StreamingResponse
from fastapi import APIRouter
import time
import redis
from config import settings
r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

router = APIRouter(prefix="/notification")

@router.get("/tasks/{task_id}")
def task_events(task_id: str):

    def stream():
        while True:
            status = r.get(f"task:{task_id}:status")
            if status == "completed":
                yield f"event: completed\ndata: {{\"task_id\": \"{task_id}\"}}\n\n"
                break
            
            if status == "failed":
                yield f"event: failed\ndata: {{\"task_id\": \"{task_id}\"}}\n\n"
                break
            time.sleep(1)

    return StreamingResponse(stream(), media_type="text/event-stream")
