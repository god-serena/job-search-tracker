import uuid
from datetime import datetime, date

from sqlalchemy import Column, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    url = Column(String(1024), nullable=True)
    status = Column(String(32), nullable=False, default="wishlist")
    date_applied = Column(Date, nullable=True)
    follow_up_date = Column(Date, nullable=True)
    contact_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TailoredResume(Base):
    __tablename__ = "tailored_resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

