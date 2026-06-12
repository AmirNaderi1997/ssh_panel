from datetime import date, datetime
import uuid
from pydantic import BaseModel, ConfigDict


class TrafficRecordBase(BaseModel):
    user_id: uuid.UUID
    server_id: uuid.UUID
    date: date
    upload_bytes: int = 0
    download_bytes: int = 0


class TrafficRecordCreate(TrafficRecordBase):
    pass


class TrafficRecordResponse(TrafficRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class TrafficSummaryBase(BaseModel):
    server_id: uuid.UUID
    period: str  # DAILY, MONTHLY
    period_start: date
    total_upload: int = 0
    total_download: int = 0


class TrafficSummaryResponse(TrafficSummaryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
