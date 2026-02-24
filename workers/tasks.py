import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workers.celery_app import celery_app
from core.automation_engine.engine import get_nornir_engine, filter_inventory
from core.tasks.backup import backup_device
from db.models import SessionLocal, Job, JobResult
from datetime import datetime

@celery_app.task(bind=True)
def trigger_backup_job(self, job_id: str, filters: dict = None):
    """Celery task executing backup across devices via Nornir."""
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        db.close()
        return "Job not found in DB"
        
    job.status = "RUNNING"
    db.commit()
    
    try:
        nr = get_nornir_engine()
        target_hosts = filter_inventory(nr, filters)
        
        # Execute nornir task
        results = target_hosts.run(task=backup_device)
        
        # Process results and store to DB
        all_success = True
        for host, result in results.items():
            run_status = "SUCCESS" if not result.failed else "FAILED"
            if result.failed:
                all_success = False
                
            log_output = result[0].result.get("config") if not result.failed else str(result.exception)
                
            job_result = JobResult(
                job_id=job_id,
                device_name=host,
                status=run_status,
                log_output=log_output
            )
            db.add(job_result)
            
        job.status = "SUCCESS" if all_success else "PARTIAL_SUCCESS"
        job.completed_at = datetime.utcnow()
        
    except Exception as e:
        job.status = "FAILED"
        job.completed_at = datetime.utcnow()
        db.add(JobResult(job_id=job_id, device_name="system", status="FAILED", log_output=str(e)))
        
    db.commit()
    db.close()
    
    return {"job_id": job_id, "status": job.status}
