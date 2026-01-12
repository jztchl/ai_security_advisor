from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict
from db.models.tasks import TaskStatus

class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    file_type: str
    filepath: str
    status: TaskStatus
    result: Optional[Any] = None
    created_at: datetime
    updated_at: datetime