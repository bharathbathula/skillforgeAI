from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ATSReportResponse(BaseModel):
    id: int
    analysis_id: int
    resume_id: int
    job_description_id: int
    overall_score: float
    skill_score: float
    keyword_score: float
    project_score: float
    experience_score: float
    semantic_score: float
    education_score: float
    formatting_score: float
    score_details: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
