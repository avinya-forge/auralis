from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class V2Metadata(Base):
    __tablename__ = "v2_metadata"

    id = Column(Integer, primary_key=True)
    track_id = Column(String, nullable=False)
    gharana = Column(String)
    instrument = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
