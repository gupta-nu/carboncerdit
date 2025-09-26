
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, JSON, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from database import Base
import uuid
from datetime import datetime


class Record(Base):
    __tablename__ = 'records'
    id = Column(String, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    registry = Column(String, nullable=False)
    vintage = Column(Integer, nullable=False)
    quantity = Column(Numeric(18, 4), nullable=False)
    serial_number = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    events = relationship('Event', back_populates='record', cascade='all, delete-orphan')

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    record_id = Column(String, ForeignKey('records.id'), nullable=False, index=True)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    record = relationship('Record', back_populates='events')
    
    # Prevent double retirement: only one RETIRED event per record
    __table_args__ = (
        Index('idx_record_event_type', 'record_id', 'event_type'),
        UniqueConstraint('record_id', 'event_type', name='uq_record_retired'),
    )