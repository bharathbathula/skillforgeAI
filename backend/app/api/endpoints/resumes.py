import os
import hashlib
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse
from app.services.parser import ResumeParser

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # Validate extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".pdf", ".docx", ".doc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF and DOCX files are allowed."
        )

    # Read content to check size and hash
    content = await file.read()
    file_size = len(content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed limit of 10MB."
        )

    # SHA-256 for duplicate detection
    file_hash = hashlib.sha256(content).hexdigest()

    # Check for duplicates for this user
    existing_duplicate = db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.file_hash == file_hash
    ).first()

    if existing_duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate resume detected! You uploaded an identical file on {existing_duplicate.upload_date.strftime('%Y-%m-%d %H:%M')} (ID: {existing_duplicate.id})."
        )

    # Ensure user upload directory exists
    user_upload_dir = os.path.join(UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_upload_dir, exist_ok=True)

    # Sanitize filename and make unique on disk to prevent overwrites
    safe_filename = file.filename.replace(" ", "_")
    unique_disk_filename = f"{int(datetime.now().timestamp())}_{safe_filename}"
    file_path = os.path.join(user_upload_dir, unique_disk_filename)

    with open(file_path, "wb") as f:
        f.write(content)


    # Extract raw text & parse resume content using unified services
    raw_text = None
    parsed_data = None
    parse_status = "uploaded"
    try:
        from app.services.parsing.pdf_extractor import PDFExtractor
        from app.services.parsing.resume_parser import ResumeParser as ParsingService
        raw_text = PDFExtractor.extract_text(file_path)
        parsed_data = ParsingService.parse(raw_text)
        parse_status = "parsed"
    except Exception as e:
        parse_status = "parse_failed"

    # Create DB record
    db_resume = Resume(
        filename=file.filename,
        file_path=file_path,
        file_hash=file_hash,
        file_size=file_size,
        file_type=file_ext,
        status=parse_status,
        extracted_text=raw_text,
        parsed_content=parsed_data,
        user_id=current_user.id
    )

    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)

    return db_resume

@router.get("/", response_model=List[ResumeResponse])
def list_resumes(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    return db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.upload_date.desc()).all()

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

@router.post("/{resume_id}/parse", response_model=ResumeResponse)
def parse_resume(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if not os.path.exists(resume.file_path):
        raise HTTPException(status_code=404, detail="Resume file not found on disk")

    try:
        from app.services.parsing.pdf_extractor import PDFExtractor
        from app.services.parsing.resume_parser import ResumeParser as ParsingService
        raw_text = PDFExtractor.extract_text(resume.file_path)
        parsed_data = ParsingService.parse(raw_text)
        resume.extracted_text = raw_text
        resume.parsed_content = parsed_data
        resume.status = "parsed"
        db.commit()
        db.refresh(resume)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

    return resume

@router.get("/{resume_id}/download")
def download_resume(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if not os.path.exists(resume.file_path):
        raise HTTPException(status_code=404, detail="Resume file not found on disk")

    return FileResponse(
        path=resume.file_path,
        filename=resume.filename,
        media_type="application/octet-stream"
    )

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Remove file from disk if present
    if os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception:
            pass

    db.delete(resume)
    db.commit()
    return None
