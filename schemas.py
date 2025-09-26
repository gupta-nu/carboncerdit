from pydantic import BaseModel, Field
from typing import Optional, List, Any
from decimal import Decimal
from datetime import datetime

class RecordBase(BaseModel):
    project_name: str
    registry: str
    vintage: int
    quantity: Decimal
    serial_number: str

class RecordCreate(RecordBase):
    pass

class RecordOut(RecordBase):
    id: str
    created_at: datetime
    status: str
    events: List[Any] = []

class EventBase(BaseModel):
    event_type: str
    payload: Optional[Any] = None

class EventOut(EventBase):
    id: str
    record_id: str
    created_at: datetime
