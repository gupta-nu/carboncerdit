from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from models import Record, Event
from schemas import RecordCreate, RecordOut, EventOut
from database import get_db
from utils import canonicalize_record_input, generate_record_id
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func
from datetime import datetime

router = APIRouter()

@router.post("/records", response_model=RecordOut, status_code=201)
def create_record(record_in: RecordCreate, db: Session = Depends(get_db)):
    # Canonicalize and generate deterministic ID
    canonical = canonicalize_record_input(record_in)
    record_id = generate_record_id(canonical)
    # Check for existing record
    db_record = db.query(Record).filter(Record.id == record_id).first()
    if db_record:
        # Check if all fields match (idempotent)
        if (
            db_record.project_name == canonical["project_name"] and
            db_record.registry == canonical["registry"] and
            db_record.vintage == canonical["vintage"] and
            float(db_record.quantity) == float(canonical["quantity"]) and
            db_record.serial_number == canonical["serial_number"]
        ):
            # Return with events
            events = db.query(Event).filter(Event.record_id == record_id).order_by(Event.created_at).all()
            status = "RETIRED" if any(e.event_type == "RETIRED" for e in events) else "ACTIVE"
            return RecordOut(
                id=record_id,
                project_name=db_record.project_name,
                registry=db_record.registry,
                vintage=db_record.vintage,
                quantity=db_record.quantity,
                serial_number=db_record.serial_number,
                created_at=db_record.created_at,
                status=status,
                events=[EventOut(
                    id=e.id,
                    record_id=e.record_id,
                    event_type=e.event_type,
                    payload=e.payload,
                    created_at=e.created_at
                ) for e in events]
            )
        else:
            raise HTTPException(status_code=409, detail="Record exists with different data.")
    # Create new record and CREATED event
    new_record = Record(
        id=record_id,
        project_name=canonical["project_name"],
        registry=canonical["registry"],
        vintage=canonical["vintage"],
        quantity=canonical["quantity"],
        serial_number=canonical["serial_number"]
    )
    db.add(new_record)
    db.flush()  # To get created_at
    created_event = Event(
        record_id=record_id,
        event_type="CREATED",
        payload=None
    )
    db.add(created_event)
    db.commit()
    db.refresh(new_record)
    events = [created_event]
    return RecordOut(
        id=record_id,
        project_name=new_record.project_name,
        registry=new_record.registry,
        vintage=new_record.vintage,
        quantity=new_record.quantity,
        serial_number=new_record.serial_number,
        created_at=new_record.created_at,
        status="ACTIVE",
        events=[EventOut(
            id=e.id,
            record_id=e.record_id,
            event_type=e.event_type,
            payload=e.payload,
            created_at=e.created_at
        ) for e in events]
    )

@router.post("/records/{record_id}/retire", response_model=EventOut)
def retire_record(record_id: str, db: Session = Depends(get_db)):
    # Lock record row for update (SQLite: SERIALIZABLE isolation)
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")
    # Check for existing RETIRED event
    retired = db.query(Event).filter(Event.record_id == record_id, Event.event_type == "RETIRED").first()
    if retired:
        raise HTTPException(status_code=409, detail="Record already retired.")
    # Create RETIRED event
    event = Event(
        record_id=record_id,
        event_type="RETIRED",
        payload=None
    )
    db.add(event)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Concurrent retirement detected.")
    db.refresh(event)
    return EventOut(
        id=event.id,
        record_id=event.record_id,
        event_type=event.event_type,
        payload=event.payload,
        created_at=event.created_at
    )

@router.get("/records/{record_id}", response_model=RecordOut)
def get_record(record_id: str, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")
    events = db.query(Event).filter(Event.record_id == record_id).order_by(Event.created_at).all()
    status = "RETIRED" if any(e.event_type == "RETIRED" for e in events) else "ACTIVE"
    return RecordOut(
        id=record.id,
        project_name=record.project_name,
        registry=record.registry,
        vintage=record.vintage,
        quantity=record.quantity,
        serial_number=record.serial_number,
        created_at=record.created_at,
        status=status,
        events=[EventOut(
            id=e.id,
            record_id=e.record_id,
            event_type=e.event_type,
            payload=e.payload,
            created_at=e.created_at
        ) for e in events]
    )
