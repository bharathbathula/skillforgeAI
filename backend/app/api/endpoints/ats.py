from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.models.ats_score import ATSScore
from app.schemas.ats import ATSReportResponse

router = APIRouter()

@router.get("/{resume_id}", response_model=ATSReportResponse)
async def get_ats_score(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    analysis = db.query(Analysis).filter(Analysis.resume_id == resume_id, Analysis.user_id == current_user.id).order_by(Analysis.created_at.desc()).first()
    if not analysis or not analysis.ats_score:
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
        if resume:
            from app.api.endpoints.analysis import start_analysis_pipeline
            try:
                await start_analysis_pipeline(resume_id=resume_id, payload=None, db=db, current_user=current_user)
                analysis = db.query(Analysis).filter(Analysis.resume_id == resume_id, Analysis.user_id == current_user.id).order_by(Analysis.created_at.desc()).first()
            except Exception:
                pass

    if not analysis or not analysis.ats_score:
        raise HTTPException(status_code=404, detail="ATS score not found. Please run resume analysis first.")

    ats = analysis.ats_score
    return ATSReportResponse(
        id=ats.id,
        analysis_id=ats.analysis_id,
        resume_id=analysis.resume_id,
        job_description_id=analysis.job_description_id,
        overall_score=ats.overall_score,
        skill_score=ats.skill_score,
        keyword_score=ats.keyword_score,
        project_score=ats.project_score,
        experience_score=ats.experience_score,
        semantic_score=ats.semantic_score,
        education_score=ats.education_score,
        formatting_score=ats.formatting_score,
        score_details=ats.score_details,
        created_at=ats.created_at
    )

@router.get("/{resume_id}/report")
async def get_ats_full_report(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    analysis = db.query(Analysis).filter(Analysis.resume_id == resume_id, Analysis.user_id == current_user.id).order_by(Analysis.created_at.desc()).first()
    if not analysis or not analysis.ats_score:
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
        if resume:
            from app.api.endpoints.analysis import start_analysis_pipeline
            try:
                await start_analysis_pipeline(resume_id=resume_id, payload=None, db=db, current_user=current_user)
                analysis = db.query(Analysis).filter(Analysis.resume_id == resume_id, Analysis.user_id == current_user.id).order_by(Analysis.created_at.desc()).first()
            except Exception:
                pass

    if not analysis or not analysis.ats_score:
        raise HTTPException(status_code=404, detail="ATS report not found. Please run resume analysis first.")

    ats = analysis.ats_score
    return {
        "status": analysis.status,
        "resume_id": resume_id,
        "job_description_id": analysis.job_description_id,
        "overall_score": ats.overall_score,
        "score_breakdown": {
            "skill_score": ats.skill_score,
            "keyword_score": ats.keyword_score,
            "project_score": ats.project_score,
            "experience_score": ats.experience_score,
            "semantic_score": ats.semantic_score,
            "education_score": ats.education_score,
            "formatting_score": ats.formatting_score
        },
        "report_details": ats.score_details
    }
