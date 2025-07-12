from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from pydantic import BaseModel, Field


class ComplaintStatus(str, PyEnum):
    """Описание статуса жалобы для создания/обновления."""
    OPEN = "open"
    CLOSED = "closed"


class ComplaintCategory(str, PyEnum):
    """Описание категории жалобы для создания/обновления."""
    TECHNICAL = "техническая"
    PAYMENT = "оплата"
    OTHER = "другое"


class ComplaintSentiment(str, PyEnum):
    """Описание тональности жалобы для создания/обновления."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


class ComplaintCreate(BaseModel):
    """Описание жалобы для создания."""
    text: str = Field(min_length=10, max_length=1000)
    category: ComplaintCategory = Field(default=ComplaintCategory.OTHER)

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Не приходит SMS-сообщение с кодом подтверждения",
                "category": "техническая",
            }
        }


class ComplaintUpdate(BaseModel):
    """Описание жалобы для обновления."""
    text: Optional[str] = Field(None, min_length=10, max_length=1000)
    status: Optional[ComplaintStatus] = Field(None)

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Не приходит SMS-сообщение с кодом подтверждения",
                "category": "техническая",
            }
        }


class ComplaintResponse(BaseModel):
    """Описание жалобы для Response."""
    id: int
    text: str
    status: ComplaintStatus
    timestamp: datetime
    sentiment: ComplaintSentiment | None
    category: ComplaintCategory
    ip_address: str | None
    geo_country: str | None
    geo_city: str | None


    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 27,
                "text": "Не приходит SMS-сообщение с кодом подтверждения",
                "status": "open",
                "timestamp": "2025-07-09T15:58:05",
                "sentiment": "neutral",
                "category": "техническая",
                "ip_address": "178.252.97.31",
                "geo_country": "Россия",
                "geo_city": "Санкт-Петербург"
            }
        }
