from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class TaskType(str, Enum):
    MEANING = "MEANING"
    SENTENCE = "SENTENCE"
    MCQ = "MCQ"
    PARAGRAPH = "PARAGRAPH"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"

class TaskResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"

# Task Item Model
class TaskItem(BaseModel):
    taskId: str
    type: TaskType
    wordIds: List[str]
    status: TaskStatus
    result: Optional[TaskResult] = None

# Response Models
class DailyTaskResponse(BaseModel):
    id: str
    userId: str
    date: str  # YYYY-MM-DD
    tasks: List[TaskItem]
    createdAt: datetime
    
    class Config:
        from_attributes = True

# Request Models
class CompleteTaskRequest(BaseModel):
    result: TaskResult
