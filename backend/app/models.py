from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, Session, mapped_column

from .database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


def list_tasks(db: Session) -> list[Task]:
    return db.query(Task).order_by(Task.position.asc(), Task.id.asc()).all()


def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)


def create_task(db: Session, *, title: str, description: str = "") -> Task:
    max_position = db.query(func.max(Task.position)).scalar()
    next_position = 0 if max_position is None else max_position + 1

    task = Task(
        title=title.strip(),
        description=description.strip(),
        position=next_position,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(
    db: Session,
    task: Task,
    *,
    title: str | None = None,
    description: str | None = None,
    completed: bool | None = None,
) -> Task:
    if title is not None:
        task.title = title.strip()
    if description is not None:
        task.description = description.strip()
    if completed is not None:
        task.completed = completed

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def reorder_tasks(db: Session, task_ids: list[int]) -> list[Task] | None:
    tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
    by_id = {task.id: task for task in tasks}

    if len(by_id) != len(set(task_ids)):
        return None

    for index, task_id in enumerate(task_ids):
        by_id[task_id].position = index

    db.commit()
    return list_tasks(db)
