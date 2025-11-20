from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Table, Text, Time
from sqlalchemy.orm import relationship

from .database import Base

band_members_table = Table(
    "band_members",
    Base.metadata,
    Column("band_id", ForeignKey("bands.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)

    bands = relationship("Band", secondary=band_members_table, back_populates="members")
    availability = relationship(
        "Availability", back_populates="user", cascade="all, delete-orphan"
    )
    messages = relationship("Message", back_populates="sender")
    files = relationship("SharedFile", back_populates="uploader")


class Band(Base):
    __tablename__ = "bands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    members = relationship("User", secondary=band_members_table, back_populates="bands")
    events = relationship("Event", back_populates="band", cascade="all, delete-orphan")
    messages = relationship(
        "Message", back_populates="band", cascade="all, delete-orphan"
    )
    files = relationship("SharedFile", back_populates="band", cascade="all, delete-orphan")


class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    band_id = Column(Integer, ForeignKey("bands.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0 = Monday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    user = relationship("User", back_populates="availability")
    band = relationship("Band")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    band_id = Column(Integer, ForeignKey("bands.id"), nullable=False)
    title = Column(String, nullable=False)
    event_type = Column(String, nullable=False)  # rehearsal, gig, etc.
    date = Column(Date, nullable=False)
    location = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    setlist = Column(Text, nullable=True)

    band = relationship("Band", back_populates="events")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    band_id = Column(Integer, ForeignKey("bands.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    band = relationship("Band", back_populates="messages")
    sender = relationship("User", back_populates="messages")


class SharedFile(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    band_id = Column(Integer, ForeignKey("bands.id"), nullable=False)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    band = relationship("Band", back_populates="files")
    uploader = relationship("User", back_populates="files")
