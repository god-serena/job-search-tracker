import uuid
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class StatusEnum(str, Enum):
    wishlist = "wishlist"
    applied = "applied"
    interviewing = "interviewing"
    offer = "offer"
    rejected = "rejected"
    cancelled = "cancelled"


class ApplicationBase(BaseModel):
    company: str
    role: str
    url: Optional[str] = None
    status: StatusEnum = StatusEnum.wishlist
    date_applied: Optional[date] = None
    follow_up_date: Optional[date] = None
    contact_name: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    url: Optional[str] = None
    status: Optional[StatusEnum] = None
    date_applied: Optional[date] = None
    follow_up_date: Optional[date] = None
    contact_name: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class ApplicationOut(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class ResumeBase(BaseModel):
    content: str = ""


class ResumeUpdate(BaseModel):
    content: str


class ResumeOut(ResumeBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    updated_at: datetime


class TailorPromptOut(BaseModel):
    prompt: str


class TailoredResumeCreate(BaseModel):
    content: str
    source: str


class TailoredResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    content: str
    source: str
    created_at: datetime

class GenerateLocalRequest(BaseModel):
    model: Optional[str] = None


class GenerateDocumentRequest(BaseModel):
    model: Optional[str] = None
    template_type: Optional[str] = "cold_outreach"


class DocumentOut(BaseModel):
    content: str
    document_type: str



class StatsOut(BaseModel):
    total_applications: int
    by_status: dict[str, int]
    interview_rate: float
    offer_rate: float
    active_pipeline: int
    follow_ups_due: int
