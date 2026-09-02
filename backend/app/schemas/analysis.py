from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class AnalysisCreate(BaseModel):
    resume_id: Optional[int] = None
    job_description_id: Optional[int] = None
    job_title: Optional[str] = None
    job_description_text: Optional[str] = None

class AnalysisStatusResponse(BaseModel):
    id: int
    resume_id: int
    job_description_id: int
    status: str # PENDING, PROCESSING, COMPLETED, FAILED
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AnalysisResponse(AnalysisStatusResponse):
    overall_score: Optional[float] = None
    report_details: Optional[Dict[str, Any]] = None
