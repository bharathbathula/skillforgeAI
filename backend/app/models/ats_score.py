from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.analysis import Analysis

class ATSScore(Base):


    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    skill_score: Mapped[float] = mapped_column(Float, default=0.0)
    keyword_score: Mapped[float] = mapped_column(Float, default=0.0)
    project_score: Mapped[float] = mapped_column(Float, default=0.0)
    experience_score: Mapped[float] = mapped_column(Float, default=0.0)
    semantic_score: Mapped[float] = mapped_column(Float, default=0.0)
    education_score: Mapped[float] = mapped_column(Float, default=0.0)
    formatting_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Detailed report data JSON (breakdown analysis, recommendations, strengths, weaknesses, project matches)
    score_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    analysis_id: Mapped[int] = mapped_column(ForeignKey("analysis.id", ondelete="CASCADE"), unique=True)
    analysis: Mapped[Analysis] = relationship("Analysis", back_populates="ats_score")
