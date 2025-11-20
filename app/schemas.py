from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str
    email: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: Optional[str]

    class Config:
        orm_mode = True


class BandCreate(BaseModel):
    name: str
    description: Optional[str] = None


class BandOut(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


class AvailabilityCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: time
    end_time: time


class AvailabilityOut(BaseModel):
    id: int
    user_id: int
    band_id: int
    day_of_week: int
    start_time: time
    end_time: time

    class Config:
        orm_mode = True


class EventCreate(BaseModel):
    title: str
    event_type: str
    date: date
    location: Optional[str] = None
    notes: Optional[str] = None
    setlist: Optional[str] = None


class EventOut(BaseModel):
    id: int
    band_id: int
    title: str
    event_type: str
    date: date
    location: Optional[str]
    notes: Optional[str]
    setlist: Optional[str]

    class Config:
        orm_mode = True


class MessageCreate(BaseModel):
    sender_id: int
    content: str


class MessageOut(BaseModel):
    id: int
    band_id: int
    sender_id: int
    content: str
    created_at: str

    class Config:
        orm_mode = True


class SharedFileCreate(BaseModel):
    uploader_id: int
    title: str
    url: str
    notes: Optional[str] = None


class SharedFileOut(BaseModel):
    id: int
    band_id: int
    uploader_id: int
    title: str
    url: str
    notes: Optional[str]
    created_at: str

    class Config:
        orm_mode = True


class MatchWindow(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str


class MatchResponse(BaseModel):
    band_id: int
    member_count: int
    matches: List[MatchWindow]
