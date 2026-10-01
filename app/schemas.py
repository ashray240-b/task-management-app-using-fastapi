from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, use_enum_values=True)

    title: str = Field(..., min_length=1, max_length=255, examples=["Write DR runbook"])
    description: str | None = Field(default=None, examples=["Document failover steps"])
    status: TaskStatus = TaskStatus.pending


class TaskUpdate(BaseModel):
    """All fields optional: only the fields you send are updated."""

    model_config = ConfigDict(str_strip_whitespace=True, use_enum_values=True)

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None

    @field_validator("title", "status")
    @classmethod
    def not_null_if_provided(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
