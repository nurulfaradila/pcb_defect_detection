from celery import Celery
import os
import time
from .services import run_inference, update_task_result

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@broker:5672//")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "db+postgresql://user:password@db:5432/pcb_defects")

celery_app = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery_app.task(name="predict_defect", bind=True)
def predict_defect(self, image_path: str, task_id_db: str):
    try:
        time.sleep(1) 
        result = run_inference(image_path)
        update_task_result(task_id_db, result, "SUCCESS")
        return result
    except Exception as e:
        update_task_result(task_id_db, {"error": str(e)}, "FAILURE")
        raise e
