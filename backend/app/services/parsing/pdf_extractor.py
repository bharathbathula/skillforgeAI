import os
import re
from typing import Tuple

class PDFExtractor:
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract readable raw text from PDF or DOCX file.
        Raises ValueError if text cannot be extracted or file is corrupt.
        """
        if not os.path.exists(file_path):
            raise ValueError(f"File not found on disk: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()
        raw_text = ""

        if file_ext == ".pdf":
            # Attempt 1: pypdf
            try:
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                text_list = []
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        text_list.append(t)
                raw_text = "\n".join(text_list)
            except Exception as e:
                raw_text = ""

            # Attempt 2: pdfplumber fallback if pypdf returned empty
            if not raw_text.strip():
                try:
                    import pdfplumber
                    with pdfplumber.open(file_path) as pdf:
                        text_list = [page.extract_text() or "" for page in pdf.pages]
                        raw_text = "\n".join(text_list)
                except Exception:
                    pass

        elif file_ext in [".docx", ".doc"]:
            try:
                import docx
                doc = docx.Document(file_path)
                text_list = [p.text for p in doc.paragraphs if p.text]
                for table in doc.tables:
                    for row in table.rows:
                        text_list.extend([cell.text for cell in row.cells if cell.text])
                raw_text = "\n".join(text_list)
            except Exception as e:
                raise ValueError(f"Failed to read DOCX file: {str(e)}")

        cleaned_text = PDFExtractor.clean_text(raw_text)
        if not cleaned_text.strip():
            raise ValueError("No extractable text found in the uploaded resume file. Please ensure it is not a scanned image PDF.")

        return cleaned_text

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize raw extracted text.
        """
        if not text:
            return ""

        # Normalize unicode whitespace & linebreaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Replace common unicode bullet characters with standard hyphen and space
        bullet_chars = ['\u2022', '\u2023', '\u25e6', '\u2043', '\u2219', '\u25aa', '\u25ab', '\u25cf', '\uf0b7', '\ufffd', '·']
        for b in bullet_chars:
            text = text.replace(b, '\n- ')

        # Replace typographical quotes and dashes
        text = text.replace('\u2013', '-').replace('\u2014', '-').replace('\u2018', "'").replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')

        # Replace multiple spaces/tabs with single space while keeping linebreaks
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_line = re.sub(r'[ \t]+', ' ', line).strip()
            # Normalize bullet points if formatted like "-Something"
            if cleaned_line.startswith('-') and len(cleaned_line) > 1 and cleaned_line[1] != ' ':
                cleaned_line = '- ' + cleaned_line[1:].strip()
            cleaned_lines.append(cleaned_line)
        
        # Remove excess empty lines
        result_lines = []
        empty_count = 0
        for line in cleaned_lines:
            if not line:
                empty_count += 1
                if empty_count <= 1:
                    result_lines.append(line)
            else:
                empty_count = 0
                result_lines.append(line)

        return "\n".join(result_lines).strip()

