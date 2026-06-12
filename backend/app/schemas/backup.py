import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BackupBase(BaseModel):
    type: str = "DATABASE"  # DATABASE, CONFIG, SSL, FULL
    filename: str
    file_size: int = 0
    status: str = "PENDING"
    notes: str | None = None
    schedule_id: str | None = None


class BackupCreate(BackupBase):
    pass


class BackupResponse(BackupBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_by_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
