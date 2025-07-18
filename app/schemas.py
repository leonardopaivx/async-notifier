from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import List
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"


class NotificationRequest(BaseModel):
    message_id: UUID = Field(default_factory=uuid4)
    message_content: str
    notification_type: NotificationType


class StatusEntry(BaseModel):
    status: str
    timestamp: datetime


class StatusResponse(BaseModel):
    trace_id: UUID
    message_id: UUID
    message_content: str
    notification_type: NotificationType
    status: str
    history: List[StatusEntry]
