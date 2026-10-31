from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SupportRequestCreate(BaseModel):
    subject: str = Field(..., min_length=2, max_length=255)
    message: str = Field(..., min_length=5)


class SupportRequestResponse(BaseModel):
    id: int
    user_id: int
    subject: str
    message: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
