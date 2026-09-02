from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, computed_field
from app.schemas.job_description import JobDescriptionResponse

class ResumeBase(BaseModel):
    filename: str
    status: str = "uploaded"

class ResumeCreate(ResumeBase):
    file_path: str
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None

class ResumeResponse(ResumeBase):
    id: int
    file_path: str
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    upload_date: datetime
    status: str
    parsed_content: Optional[Dict[str, Any]] = None
    ats_score: Optional[float] = None
    skill_gap: Optional[Dict[str, Any]] = None
    learning_roadmap: Optional[Dict[str, Any]] = None
    interview_questions: Optional[Dict[str, Any]] = None
    user_id: int
    job_descriptions: Optional[List[JobDescriptionResponse]] = []

    @computed_field
    @property
    def uploaded_at(self) -> datetime:
        return self.upload_date

    @computed_field
    @property
    def filepath(self) -> str:
        return self.file_path

    model_config = ConfigDict(from_attributes=True)

