from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import Base, engine
from routes import router
import models
import os
import json
from sqlalchemy.orm import Session
from database import SessionLocal
from utils import canonicalize_record_input, generate_record_id
from models import Record, Event
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    preload_sample_data()
    yield
    # Shutdown (if needed)

app = FastAPI(lifespan=lifespan)
app.include_router(router)

def preload_sample_data():
    sample_path = os.path.join(os.path.dirname(__file__), 'sample-registry.json')
    if not os.path.exists(sample_path):
        return
    with open(sample_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    db: Session = SessionLocal()
    for item in data:
        canonical = canonicalize_record_input(item)
        record_id = generate_record_id(canonical)
        exists = db.query(Record).filter(Record.id == record_id).first()
        if not exists:
            record = Record(
                id=record_id,
                project_name=canonical['project_name'],
                registry=canonical['registry'],
                vintage=canonical['vintage'],
                quantity=canonical['quantity'],
                serial_number=canonical['serial_number'],
                created_at=datetime.utcnow()
            )
            db.add(record)
            db.flush()
            event = Event(
                record_id=record_id,
                event_type="CREATED",
                payload=None
            )
            db.add(event)
    db.commit()
    db.close()
