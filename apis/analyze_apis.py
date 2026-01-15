from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from datetime import datetime
import os
from pathlib import Path
from tasks.process_file import process_uploaded_file
import uuid
import logging
from sqlalchemy.orm import Session
from db.models.tasks import Task, TaskStatus
from db.database import get_db
import aiofiles
from utils.response_models import TaskOut
from utils.pagination import Page, paginate
router = APIRouter(prefix="/analyze")
logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(exist_ok=True)

@router.post("/")
async def analyze_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.go': 'go',
            '.rs': 'rust',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.php': 'php',
            '.rb': 'ruby'
        }
        file_extension = Path(file.filename).suffix.lower()
        actual_file_name = Path(file.filename).name
        language = language_map.get(file_extension, 'text')
        
        # if file_extension not in allowed_extensions:
        #     raise HTTPException(
        #         status_code=400,
        #         detail=f"File type {file_extension} not supported. Supported types: 

       
        filename=uuid.uuid4().hex + file_extension
        filepath = os.path.join(UPLOAD_DIR, filename)
        async with aiofiles.open(filepath, mode='wb') as f:
            await f.write(await file.read())

        task = Task(
            filename=actual_file_name,
            filepath=filepath,
            file_type=language
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        try:
            process_uploaded_file.delay(str(task.id))
        except Exception as e:
            logger.warning(f"Could not queue task (Redis not available): {e}")
            
        return {
            "status": "processing",
            "task_id": task.id,
            "filename": file.filename,
            "message": "File uploaded and analysis started"
        }
        
    except Exception as e:
        # Update task status if it was created
        if 'task' in locals():
            task.status = TaskStatus.FAILED
            task.result = {"error": str(e)}
            db.commit()
            
        logger.error(f"Error processing file upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/results/{task_id}")
async def get_analysis_results(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the results of a file analysis
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task.id,
        "status": task.status,
        "filename": task.filename,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "result": task.result
    }




@router.get("/tasks", response_model=Page[TaskOut])
async def list_tasks(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    q = db.query(Task)
    return paginate(q, page, per_page, out_model=TaskOut)
