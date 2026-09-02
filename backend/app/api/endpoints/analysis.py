from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.analysis import Analysis
from app.models.skill_match import SkillMatch
from app.models.ats_score import ATSScore

from app.schemas.analysis import AnalysisCreate, AnalysisStatusResponse, AnalysisResponse
from app.services.parsing.pdf_extractor import PDFExtractor
from app.services.parsing.resume_parser import ResumeParser
from app.services.parsing.job_parser import JobParser
from app.services.embeddings.embedding_service import EmbeddingService
from app.services.vector.chroma_service import ChromaService
from app.services.ats.ats_scoring_service import ATSScoringService

router = APIRouter()

@router.post("/{resume_id}", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def start_analysis_pipeline(
    resume_id: int,
    payload: Optional[AnalysisCreate] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # 1. User Isolation & Resume Verification
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # 2. Handle / Get Job Description
    job_desc = None
    if payload and payload.job_description_id:
        job_desc = db.query(JobDescription).filter(JobDescription.id == payload.job_description_id, JobDescription.user_id == current_user.id).first()
    
    if not job_desc and payload and payload.job_description_text:
        title = payload.job_title or "Target Role"
        parsed_jd = JobParser.parse(title, payload.job_description_text)
        job_desc = JobDescription(
            title=title,
            description=payload.job_description_text,
            parsed_data=parsed_jd,
            user_id=current_user.id,
            resume_id=resume.id
        )
        db.add(job_desc)
        db.commit()
        db.refresh(job_desc)

    # Fallback to recent job description associated with resume
    if not job_desc:
        job_desc = db.query(JobDescription).filter(JobDescription.resume_id == resume.id, JobDescription.user_id == current_user.id).order_by(JobDescription.created_at.desc()).first()

    if not job_desc:
        raise HTTPException(status_code=400, detail="Job description text or ID must be provided to run analysis")

    # 3. Create Analysis Record with status PENDING -> PROCESSING
    analysis = Analysis(
        status="PROCESSING",
        user_id=current_user.id,
        resume_id=resume.id,
        job_description_id=job_desc.id
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    try:
        # Step A: Extract Raw Text from Resume if missing
        raw_resume_text = resume.extracted_text
        if not raw_resume_text or not raw_resume_text.strip():
            raw_resume_text = PDFExtractor.extract_text(resume.file_path)
            resume.extracted_text = raw_resume_text

        # Step B: Parse Resume into Structured JSON
        parsed_content = resume.parsed_content
        if isinstance(parsed_content, str):
            import json
            try:
                parsed_content = json.loads(parsed_content)
            except Exception:
                parsed_content = None

        # Re-parse if missing, not a dict, or in legacy format
        if (
            not isinstance(parsed_content, dict)
            or "personal_info" not in parsed_content
            or not isinstance(parsed_content.get("skills"), dict)
        ):
            parsed_resume: dict[str, Any] = ResumeParser.parse(raw_resume_text)
            resume.parsed_content = parsed_resume
            resume.status = "parsed"
        else:
            parsed_resume: dict[str, Any] = parsed_content

        # Step C: Parse Job Description if missing
        parsed_job_data = job_desc.parsed_data
        if isinstance(parsed_job_data, str):
            import json
            try:
                parsed_job_data = json.loads(parsed_job_data)
            except Exception:
                parsed_job_data = None

        if not isinstance(parsed_job_data, dict):
            parsed_job: dict[str, Any] = JobParser.parse(job_desc.title, job_desc.description)
            job_desc.parsed_data = parsed_job
        else:
            parsed_job: dict[str, Any] = parsed_job_data

        # Step D: Section Chunking & Vector Indexing
        resume_chunks = EmbeddingService.chunk_resume(parsed_resume, raw_resume_text)
        job_chunks = EmbeddingService.chunk_job(parsed_job, job_desc.description)

        ChromaService.index_resume_sections(resume.id, resume_chunks)
        ChromaService.index_job_sections(job_desc.id, job_chunks)

        # Step E: Complete ATS Report & Matching Pipeline
        ats_report = await ATSScoringService.compute_full_ats_report_async(
            parsed_resume,
            parsed_job,
            raw_resume_text,
            job_desc.description,
            resume_chunks,
            job_chunks
        )

        # Step F: Store Individual SkillMatches (clear previous if any for this analysis)
        db.query(SkillMatch).filter(SkillMatch.analysis_id == analysis.id).delete()
        skill_analysis = ats_report.get("skill_analysis", {})
        for match_item in skill_analysis.get("skill_matches", []):
            sm = SkillMatch(
                skill=match_item["skill"],
                category="Technical",
                match_type=match_item["match_type"],
                similarity_score=match_item["similarity_score"],
                importance=match_item["importance"],
                analysis_id=analysis.id
            )
            db.add(sm)

        # Step G: Store or Update ATSScore Record
        breakdown = ats_report.get("score_breakdown", {})
        existing_ats = db.query(ATSScore).filter(ATSScore.analysis_id == analysis.id).first()
        if existing_ats:
            existing_ats.overall_score = ats_report["overall_score"]
            existing_ats.skill_score = breakdown.get("skill_score", 0.0)
            existing_ats.keyword_score = breakdown.get("keyword_score", 0.0)
            existing_ats.project_score = breakdown.get("project_score", 0.0)
            existing_ats.experience_score = breakdown.get("experience_score", 0.0)
            existing_ats.semantic_score = breakdown.get("semantic_score", 0.0)
            existing_ats.education_score = breakdown.get("education_score", 0.0)
            existing_ats.formatting_score = breakdown.get("formatting_score", 0.0)
            existing_ats.score_details = ats_report
        else:
            db_ats = ATSScore(
                overall_score=ats_report["overall_score"],
                skill_score=breakdown.get("skill_score", 0.0),
                keyword_score=breakdown.get("keyword_score", 0.0),
                project_score=breakdown.get("project_score", 0.0),
                experience_score=breakdown.get("experience_score", 0.0),
                semantic_score=breakdown.get("semantic_score", 0.0),
                education_score=breakdown.get("education_score", 0.0),
                formatting_score=breakdown.get("formatting_score", 0.0),
                score_details=ats_report,
                analysis_id=analysis.id
            )
            db.add(db_ats)

        # Update Resume summary metrics
        resume.ats_score = ats_report["overall_score"]
        resume.skill_gap = {
            "matched_skills": skill_analysis.get("matched_skills", []),
            "missing_skills": skill_analysis.get("missing_skills", []),
            "partial_skills": skill_analysis.get("partial_skills", [])
        }

        # Step H: Finalize Analysis record status to COMPLETED
        analysis.status = "COMPLETED"
        analysis.completed_at = datetime.now()

        db.commit()
        db.refresh(analysis)

        return AnalysisResponse(
            id=analysis.id,
            resume_id=analysis.resume_id,
            job_description_id=analysis.job_description_id,
            status=analysis.status,
            created_at=analysis.created_at,
            completed_at=analysis.completed_at,
            overall_score=ats_report["overall_score"],
            report_details=ats_report
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        analysis.status = "FAILED"
        analysis.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")

@router.get("/{resume_id}", response_model=AnalysisResponse)
def get_latest_analysis(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    analysis = db.query(Analysis).filter(Analysis.resume_id == resume_id, Analysis.user_id == current_user.id).order_by(Analysis.created_at.desc()).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis report not found for this resume")

    overall_score = analysis.ats_score.overall_score if analysis.ats_score else 0.0
    report_details = analysis.ats_score.score_details if analysis.ats_score else None

    return AnalysisResponse(
        id=analysis.id,
        resume_id=analysis.resume_id,
        job_description_id=analysis.job_description_id,
        status=analysis.status,
        error_message=analysis.error_message,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
        overall_score=overall_score,
        report_details=report_details
    )

@router.get("/{resume_id}/status", response_model=AnalysisStatusResponse)
def get_analysis_status(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    analysis = db.query(Analysis).filter(Analysis.resume_id == resume_id, Analysis.user_id == current_user.id).order_by(Analysis.created_at.desc()).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis task not found")
    return analysis
