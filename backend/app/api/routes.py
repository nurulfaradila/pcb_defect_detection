from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app.models import get_db
from backend.app.services import get_history, get_task_status, create_task_entry
from backend.app.tasks import predict_defect
import shutil
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/predict")
async def predict_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    file_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1]
    filename = f"{file_id}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_task = create_task_entry(db, file_id, filename, file.filename)

    task = predict_defect.delay(file_path, file_id)
    
    return {"task_id": file_id, "status": "PENDING", "image_url": f"/uploads/{filename}"}

@router.get("/status/{task_id}")
def check_status(task_id: str, db: Session = Depends(get_db)):
    task = get_task_status(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    response = {
        "task_id": task.task_id,
        "status": task.status,
        "filename": task.filename,
        "original_filename": task.original_filename
    }
    
    if task.status == "SUCCESS":
        response["result"] = task.result
    
    return response

@router.get("/history")
def get_prediction_history(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    history = get_history(db, skip, limit)
    return history
