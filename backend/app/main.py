from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .api import routes
from .models import Base, engine
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PCB Defect Detection API")

origins = [
    "http://localhost:8501",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to PCB Defect Detection API"}
