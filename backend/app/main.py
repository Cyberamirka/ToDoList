from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import models
from .database import Base, engine, get_db
from .schemas import TaskCreate, TaskOut, TaskReorder, TaskUpdate

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

Base.metadata.create_all(bind=engine)

app = FastAPI(title="To-Do List API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/tasks", response_model=list[TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    return models.list_tasks(db)


@app.post("/api/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    return models.create_task(
        db,
        title=payload.title,
        description=payload.description,
    )


@app.patch("/api/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = models.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    data = payload.model_dump(exclude_unset=True)
    if "title" in data and data["title"] is not None and not data["title"].strip():
        raise HTTPException(status_code=422, detail="Title cannot be empty")

    return models.update_task(db, task, **data)


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = models.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    models.delete_task(db, task)
    return None


@app.put("/api/tasks/reorder", response_model=list[TaskOut])
def reorder_tasks(payload: TaskReorder, db: Session = Depends(get_db)):
    tasks = models.reorder_tasks(db, payload.task_ids)
    if tasks is None:
        raise HTTPException(status_code=400, detail="One or more tasks were not found")
    return tasks


@app.get("/api/health")
def health():
    return {"status": "ok"}


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
