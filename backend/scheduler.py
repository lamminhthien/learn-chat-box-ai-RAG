from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

scheduler = BackgroundScheduler()
scheduler.start()

_reminder_jobs = {}

def schedule_reminder(event_id, title, dt, callback):
    # dt: datetime object
    job_id = f"reminder_{event_id}"
    remove_reminder(event_id)
    if dt > datetime.now():
        job = scheduler.add_job(callback, 'date', run_date=dt, args=[event_id, title, dt], id=job_id)
        _reminder_jobs[event_id] = job

def remove_reminder(event_id):
    job_id = f"reminder_{event_id}"
    job = _reminder_jobs.pop(event_id, None)
    if job:
        try:
            job.remove()
        except Exception:
            pass 