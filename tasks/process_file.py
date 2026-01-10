from datetime import datetime
import asyncio
from typing import Dict, Any
from core.ai import analyze_code_security
import logging
from db.models.tasks import Task
from fastapi import HTTPException
from pathlib import Path
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
 
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            analysis_result = loop.run_until_complete(
                analyze_code_security(code_content, language)
            )
            

            result_text = analysis_result.text
            print(f"Raw response: {result_text}")
            
            if result_text:
                if '```json' in result_text:
                    json_start = result_text.find('```json') + 7
                    json_end = result_text.find('```', json_start)
                    json_text = result_text[json_start:json_end].strip()
                elif '```' in result_text:
                    json_start = result_text.find('```') + 3
                    json_end = result_text.find('```', json_start)
                    json_text = result_text[json_start:json_end].strip()
                else:
                    json_text = result_text.strip()
                
                try:
                    parsed_result = json.loads(json_text)
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    print(f"Attempted to parse: {json_text}")
                    parsed_result = {
                        "error": f"JSON parsing error: {str(e)}",
                        "status": "analysis_error",
                        "raw_response": result_text
                    }
            else:
                parsed_result = {
                    "error": "No analysis result",
                    "status": "analysis_error"
                }
            

            task.result = parsed_result
            task.status = TaskStatus.COMPLETED
            db.commit()
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            task.status = TaskStatus.FAILED
            task.result = {"error": str(e)}
            db.commit()
        finally:
            loop.close()
            

        return {
            "status": "completed",
            "filename": original_filename,
            "filepath": filepath,
            "language": language,
            "analysis": parsed_result,
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