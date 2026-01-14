from datetime import datetime
import asyncio
from typing import Dict, Any
from core.ai import analyze_code_security
from core.semgrep import run_semgrep
import logging
from db.models.tasks import Task
from db.database import SessionLocal
from celery_app import celery_client
logger = logging.getLogger(__name__)
import json
from db.models.tasks import TaskStatus

@celery_client.task
def process_uploaded_file(task_id: str) -> dict:
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return {"error": "Task not found"}
        
        filepath = task.filepath
        original_filename = task.filename
        language = task.file_type

        with open(filepath, 'r', encoding='utf-8') as f:
            code_content = f.read()
 
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)

        try:
            semgrep_result = run_semgrep(filepath)
            analysis_result = analyze_code_security(code_content, language,task_id,filepath,semgrep_result)
            if analysis_result:
                task.result = analysis_result
                task.status = TaskStatus.COMPLETED
                
                logger.info(f"Task {task_id} completed successfully")
            else:
                logger.error(f"Analysis result is empty for task {task_id}")
                task.status = TaskStatus.FAILED
                task.result = {}
                
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            task.status = TaskStatus.FAILED
            task.result = {}
            
        finally:
            db.commit()

        return {
            "status": "completed",
            "filename": original_filename,
            "filepath": filepath,
            "language": language,
            "analysis": analysis_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        if 'task' in locals():
            task.status = TaskStatus.FAILED
            task.result = {"error": str(e)}
            db.commit()
        return {
            "status": "error",
            "filename": original_filename if 'original_filename' in locals() else "unknown",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    finally:
        db.close()