from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import uuid
from workers.tasks import trigger_backup_job
from db.models import SessionLocal, Job

router = APIRouter()

class BackupRequest(BaseModel):
    filters: Optional[dict] = None

@router.post("/backup", status_code=202)
def start_backup_job(request: BackupRequest):
    """Trigger a fleet backup job asynchronously."""
    
    job_id = str(uuid.uuid4())
    
    # Store job in DB
    db = SessionLocal()
    new_job = Job(id=job_id, job_type="BACKUP", status="PENDING")
    db.add(new_job)
    db.commit()
    db.close()
    
    # Send to Celery worker
    trigger_backup_job.delay(job_id, request.filters)
    
    return {"job_id": job_id, "message": "Backup job submitted successfully"}

@router.get("/{job_id}")
def get_job_status(job_id: str):
    """Retrieve the status of a specific job."""
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "job_id": job.id,
        "type": job.job_type,
        "status": job.status,
        "started_at": job.started_at,
        "completed_at": job.completed_at
    }
