from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, JSON, Float, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job_description import JobDescription
    from app.models.analysis import Analysis

class Resume(Base):


    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(512))
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    status: Mapped[str] = mapped_column(String(50), default="uploaded")

    # Clean extracted raw text
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Store AI/Parser extraction JSON
    parsed_content: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ats_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    skill_gap: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship("User", back_populates="resumes")

    job_descriptions: Mapped[List[JobDescription]] = relationship("JobDescription", back_populates="resume", cascade="all, delete-orphan")
    analyses: Mapped[List[Analysis]] = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")
