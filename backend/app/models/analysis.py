from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.resume import Resume
    from app.models.job_description import JobDescription
    from app.models.skill_match import SkillMatch
    from app.models.ats_score import ATSScore

class Analysis(Base):

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Status: PENDING, PROCESSING, COMPLETED, FAILED
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship("User", back_populates="analyses")

    resume_id: Mapped[int] = mapped_column(ForeignKey("resume.id", ondelete="CASCADE"))
    resume: Mapped[Resume] = relationship("Resume", back_populates="analyses")

    job_description_id: Mapped[int] = mapped_column(ForeignKey("jobdescription.id", ondelete="CASCADE"))
    job_description: Mapped[JobDescription] = relationship("JobDescription", back_populates="analyses")

    skill_matches: Mapped[List[SkillMatch]] = relationship("SkillMatch", back_populates="analysis", cascade="all, delete-orphan")
    ats_score: Mapped[Optional[ATSScore]] = relationship("ATSScore", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
