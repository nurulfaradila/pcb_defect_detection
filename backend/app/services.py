from sqlalchemy.orm import Session
from .models import PredictionHistory, SessionLocal
from ultralytics import YOLO
import cv2
import json
import os
import logging

logger = logging.getLogger(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", "/app/ml/yolov8_model/best.pt")

def get_history(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PredictionHistory).order_by(PredictionHistory.created_at.desc()).offset(skip).limit(limit).all()

def get_task_status(db: Session, task_id: str):
    return db.query(PredictionHistory).filter(PredictionHistory.task_id == task_id).first()

def create_task_entry(db: Session, task_id: str, filename: str, original_filename: str):
    db_item = PredictionHistory(task_id=task_id, filename=filename, original_filename=original_filename, status="PENDING")
    db.add(db_item)
    db.commit()
    return db_item

def update_task_result(task_id: str, result: dict, status: str):
    db = SessionLocal()
    try:
        task = db.query(PredictionHistory).filter(PredictionHistory.task_id == task_id).first()
        if task:
            task.result = result
            task.status = status
            db.commit()
    except Exception as e:
        logger.error(f"Error updating task result: {e}")
    finally:
        db.close()

def run_inference(image_path: str):
    try:
        if os.path.exists(MODEL_PATH):
             model = YOLO(MODEL_PATH)
        else:
             logger.warning(f"Model not found at {MODEL_PATH}, using yolov8n.pt")
             model = YOLO("yolov8n.pt") 

        results = model(image_path)
        
        defects = []
        for r in results:
            for box in r.boxes:
                b = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = model.names[cls]
                defects.append({
                    "type": label,
                    "confidence": conf,
                    "bbox": b
                })
        return {"defects": defects}
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        raise e
