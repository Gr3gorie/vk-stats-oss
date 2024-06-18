from datetime import datetime
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    Pending = "PENDING"
    Running = "RUNNING"
    Cancelled = "CANCELLED"
    Succeeded = "SUCCEEDED"
    Failed = "FAILED"

    def is_completed(self) -> bool:
        match self:
            case JobStatus.Pending | JobStatus.Running:
                return False

            case JobStatus.Cancelled | JobStatus.Succeeded | JobStatus.Failed:
                return True


class PendingJobInfo(BaseModel):
    type: Literal[JobStatus.Pending]


class RunningJobInfo(BaseModel):
    class Progress(BaseModel):
        num_updated: int
        num_total: int

    type: Literal[JobStatus.Running]
    progress: Progress | None = None


class CancelledJobInfo(BaseModel):
    type: Literal[JobStatus.Cancelled]


class SucceededJobInfo(BaseModel):
    type: Literal[JobStatus.Succeeded]
    completed_at: datetime


class FailedJobInfo(BaseModel):
    type: Literal[JobStatus.Failed]
    error: str
    completed_at: datetime


JobInfo = Annotated[
    PendingJobInfo
    | RunningJobInfo
    | CancelledJobInfo
    | SucceededJobInfo
    | FailedJobInfo,
    Field(..., discriminator="type"),
]
