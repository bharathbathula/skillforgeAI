import os
from typing import Dict, Any, List
from app.services.parsing.pdf_extractor import PDFExtractor
from app.services.parsing.resume_parser import ResumeParser as CoreResumeParser

class ResumeParser:
    """Unified service for extracting text and structured sections from PDF and DOCX resume files."""

    @staticmethod
    def extract_text(file_path: str) -> str:
        return PDFExtractor.extract_text(file_path)

    @classmethod
    def parse(cls, file_path: str) -> Dict[str, Any]:
        raw_text = PDFExtractor.extract_text(file_path)
        return CoreResumeParser.parse(raw_text)

