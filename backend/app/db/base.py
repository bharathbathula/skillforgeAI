# Import all models for Base so that Alembic and SQLAlchemy can see them.
from app.db.base_class import Base
from app.models.user import User
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.analysis import Analysis
from app.models.skill_match import SkillMatch
from app.models.ats_score import ATSScore
