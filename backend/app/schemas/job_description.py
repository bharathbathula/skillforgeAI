from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class JobDescriptionCreate(BaseModel):
    title: str
    description: str
    resume_id: Optional[int] = None

class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    description: str
    parsed_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    resume_id: Optional[int] = None

    class Config:
        from_attributes = True
