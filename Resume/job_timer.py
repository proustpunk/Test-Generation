import threading
import time
from datetime import datetime, timedelta
from .models import Job

def delete_expired_jobs():
    while True:
        now = datetime.now()
        expired_jobs = Job.objects.filter(is_active=True)
        for job in expired_jobs:
            expiry_time = job.created_at + timedelta(days=job.deadline_days)
            if now >= expiry_time:
                print(f"Deleting job {job.id} - {job.job_title}")
                job.is_active = False
                job.delete()
        time.sleep(60)  
