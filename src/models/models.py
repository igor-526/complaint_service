from models.schemas import (ComplaintCategory,
                            ComplaintSentiment,
                            ComplaintStatus)

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class ComplaintDB(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(String(1000), nullable=False)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.OPEN)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    sentiment = Column(Enum(ComplaintSentiment),
                       default=ComplaintSentiment.UNKNOWN)
    category = Column(Enum(ComplaintCategory), default=ComplaintCategory.OTHER)
    ip_address = Column(String(15), nullable=True)
    geo_country = Column(String(50), nullable=True)
    geo_city = Column(String(50), nullable=True)
