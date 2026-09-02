from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.resume import Resume
    from app.models.analysis import Analysis

class JobDescription(Base):

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    parsed_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship("User", back_populates="job_descriptions")

    resume_id: Mapped[Optional[int]] = mapped_column(ForeignKey("resume.id", ondelete="CASCADE"), nullable=True)
    resume: Mapped[Optional[Resume]] = relationship("Resume", back_populates="job_descriptions")

    analyses: Mapped[List[Analysis]] = relationship("Analysis", back_populates="job_description", cascade="all, delete-orphan")
