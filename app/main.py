from datetime import time
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GigSet", description="Collaboration tools for bands")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/bands", response_model=schemas.BandOut)
def create_band(band: schemas.BandCreate, db: Session = Depends(get_db)):
    db_band = models.Band(name=band.name, description=band.description)
    db.add(db_band)
    db.commit()
    db.refresh(db_band)
    return db_band


@app.post("/bands/{band_id}/members", response_model=schemas.BandOut)
def add_member(band_id: int, user_id: int, db: Session = Depends(get_db)):
    band = db.get(models.Band, band_id)
    user = db.get(models.User, user_id)
    if not band or not user:
        raise HTTPException(status_code=404, detail="Band or user not found")
    if user not in band.members:
        band.members.append(user)
        db.add(band)
        db.commit()
        db.refresh(band)
    return band


@app.post("/bands/{band_id}/availability", response_model=schemas.AvailabilityOut)
def add_availability(
    band_id: int,
    user_id: int,
    availability: schemas.AvailabilityCreate,
    db: Session = Depends(get_db),
):
    band = db.get(models.Band, band_id)
    user = db.get(models.User, user_id)
    if not band or not user:
        raise HTTPException(status_code=404, detail="Band or user not found")
    if user not in band.members:
        raise HTTPException(status_code=400, detail="User must be in the band")

    db_availability = models.Availability(
        user_id=user_id,
        band_id=band_id,
        day_of_week=availability.day_of_week,
        start_time=availability.start_time,
        end_time=availability.end_time,
    )
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability


@app.get("/bands/{band_id}/availability/matches", response_model=schemas.MatchResponse)
def get_match_windows(band_id: int, db: Session = Depends(get_db)):
    band = db.get(models.Band, band_id)
    if not band:
        raise HTTPException(status_code=404, detail="Band not found")
    members = band.members
    if not members:
        raise HTTPException(status_code=400, detail="No members in band")

    # Organize availability by user and day
    availability_by_user = {member.id: [] for member in members}
    availabilities = (
        db.query(models.Availability)
        .filter(models.Availability.band_id == band_id)
        .all()
    )
    for slot in availabilities:
        availability_by_user.setdefault(slot.user_id, []).append(slot)

    matches = []
    for day in range(7):
        intersections = _daily_intersection(
            [slots for slots in availability_by_user.values()], day
        )
        for start, end in intersections:
            matches.append(
                schemas.MatchWindow(
                    day_of_week=day,
                    start_time=start.strftime("%H:%M"),
                    end_time=end.strftime("%H:%M"),
                )
            )

    return schemas.MatchResponse(
        band_id=band_id, member_count=len(members), matches=matches
    )


def _daily_intersection(
    availability_lists: List[List[models.Availability]], day: int
) -> List[tuple[time, time]]:
    """Compute overlapping windows across members for a specific day."""

    if not availability_lists:
        return []

    # Start with a full-day window and intersect user-by-user.
    intersection_windows = [(time(0, 0), time(23, 59))]
    for member_slots in availability_lists:
        member_windows = [
            (slot.start_time, slot.end_time)
            for slot in member_slots
            if slot.day_of_week == day
        ]
        intersection_windows = _intersect_windows(intersection_windows, member_windows)
        if not intersection_windows:
            break
    return intersection_windows


def _intersect_windows(
    base: List[tuple[time, time]], updates: List[tuple[time, time]]
) -> List[tuple[time, time]]:
    intersections: List[tuple[time, time]] = []
    for base_start, base_end in base:
        for update_start, update_end in updates:
            start = max(base_start, update_start)
            end = min(base_end, update_end)
            if start < end:
                intersections.append((start, end))
    return intersections


@app.post("/bands/{band_id}/events", response_model=schemas.EventOut)
def create_event(
    band_id: int, event: schemas.EventCreate, db: Session = Depends(get_db)
):
    band = db.get(models.Band, band_id)
    if not band:
        raise HTTPException(status_code=404, detail="Band not found")
    db_event = models.Event(band_id=band_id, **event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.get("/bands/{band_id}/events", response_model=List[schemas.EventOut])
def list_events(band_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Event)
        .filter(models.Event.band_id == band_id)
        .order_by(models.Event.date)
        .all()
    )


@app.post("/bands/{band_id}/messages", response_model=schemas.MessageOut)
def post_message(
    band_id: int, message: schemas.MessageCreate, db: Session = Depends(get_db)
):
    band = db.get(models.Band, band_id)
    sender = db.get(models.User, message.sender_id)
    if not band or not sender:
        raise HTTPException(status_code=404, detail="Band or sender not found")
    if sender not in band.members:
        raise HTTPException(status_code=400, detail="Sender must be in the band")

    db_message = models.Message(
        band_id=band_id, sender_id=message.sender_id, content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@app.get("/bands/{band_id}/messages", response_model=List[schemas.MessageOut])
def list_messages(band_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Message)
        .filter(models.Message.band_id == band_id)
        .order_by(models.Message.created_at.desc())
        .all()
    )


@app.post("/bands/{band_id}/files", response_model=schemas.SharedFileOut)
def share_file(
    band_id: int, shared_file: schemas.SharedFileCreate, db: Session = Depends(get_db)
):
    band = db.get(models.Band, band_id)
    uploader = db.get(models.User, shared_file.uploader_id)
    if not band or not uploader:
        raise HTTPException(status_code=404, detail="Band or uploader not found")
    if uploader not in band.members:
        raise HTTPException(status_code=400, detail="Uploader must be in the band")

    db_file = models.SharedFile(band_id=band_id, **shared_file.dict())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


@app.get("/bands/{band_id}/files", response_model=List[schemas.SharedFileOut])
def list_files(band_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.SharedFile)
        .filter(models.SharedFile.band_id == band_id)
        .order_by(models.SharedFile.created_at.desc())
        .all()
    )
