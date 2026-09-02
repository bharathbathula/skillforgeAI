from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.analysis import Analysis

class SkillMatch(Base):


    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    skill: Mapped[str] = mapped_column(String(255))
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # Technical, Soft, Tool, Framework, Database
    
    # match_type: Exact, Strong, Partial, Related, Missing
    match_type: Mapped[str] = mapped_column(String(50), default="Exact")
    similarity_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    # importance: Required, Preferred, Optional
    importance: Mapped[str] = mapped_column(String(50), default="Required")

    analysis_id: Mapped[int] = mapped_column(ForeignKey("analysis.id", ondelete="CASCADE"))
    analysis: Mapped[Analysis] = relationship("Analysis", back_populates="skill_matches")
