from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    completed: bool | None = None


class TaskReorder(BaseModel):
    task_ids: list[int] = Field(min_length=1)


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    completed: bool
    position: int
    created_at: datetime
    updated_at: datetime
