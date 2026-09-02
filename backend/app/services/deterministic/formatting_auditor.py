import re
from typing import Dict, Any, List

class FormattingAuditor:
    """
    Evaluates Resume ATS readability, structure, section completeness,
    and contact info parsability.
    """

    @classmethod
    def audit(cls, parsed_resume: Dict[str, Any], raw_resume: str) -> Dict[str, Any]:
        """
        Audits ATS formatting and calculates structure score with actionable feedback.
        """
        score = 100.0
        checks = []
        improvements = []

        # 1. Contact Information Check
        pinfo = parsed_resume.get("personal_info", {})
        email = pinfo.get("email")
        phone = pinfo.get("phone")

        if email and "@" in str(email) and "." in str(email):
            checks.append({"item": "Email Address", "status": "Passed", "detail": email})
        else:
            score -= 15.0
            checks.append({"item": "Email Address", "status": "Missing", "detail": "Valid email address not found"})
            improvements.append("Add a professional email address at the top of your resume.")

        if phone and phone != "Not Provided" and re.search(r'\d{7,}', re.sub(r'\D', '', str(phone))):
            checks.append({"item": "Phone Number", "status": "Passed", "detail": phone})
        else:
            score -= 10.0
            checks.append({"item": "Phone Number", "status": "Missing", "detail": "Phone number not detected"})
            improvements.append("Include a direct contact phone number with country code.")

        # 2. Key Sections Completeness
        skills = parsed_resume.get("skills", {})
        if skills and (isinstance(skills, list) or (isinstance(skills, dict) and any(skills.values()))):
            checks.append({"item": "Skills Section", "status": "Passed", "detail": "Structured skills detected"})
        else:
            score -= 20.0
            checks.append({"item": "Skills Section", "status": "Missing", "detail": "No explicit skills section found"})
            improvements.append("Add a dedicated 'Technical Skills' or 'Core Competencies' section.")

        edu = parsed_resume.get("education", [])
        if edu and len(edu) > 0:
            checks.append({"item": "Education Section", "status": "Passed", "detail": f"{len(edu)} degree entry/entries"})
        else:
            score -= 15.0
            checks.append({"item": "Education Section", "status": "Missing", "detail": "Education section not detected"})
            improvements.append("Add an 'Education' section with degree, institution, and graduation year.")

        exp = parsed_resume.get("experience", [])
        proj = parsed_resume.get("projects", [])
        if exp and len(exp) > 0:
            checks.append({"item": "Work Experience Section", "status": "Passed", "detail": f"{len(exp)} role(s) detected"})
        elif proj and len(proj) > 0:
            checks.append({"item": "Projects Section", "status": "Passed", "detail": f"{len(proj)} project(s) detected"})
            score -= 5.0
        else:
            score -= 25.0
            checks.append({"item": "Experience / Projects", "status": "Missing", "detail": "Neither work history nor projects found"})
            improvements.append("Include detailed 'Work Experience' or 'Technical Projects' demonstrating practical work.")

        # 3. Text Length and Density
        word_count = len(raw_resume.split())
        if word_count < 100:
            score -= 20.0
            checks.append({"item": "Content Length", "status": "Too Brief", "detail": f"{word_count} words (minimum recommended: 250)"})
            improvements.append("Resume content is sparse; expand on role descriptions and quantifiable project outcomes.")
        elif word_count > 1500:
            score -= 10.0
            checks.append({"item": "Content Length", "status": "Too Long", "detail": f"{word_count} words (recommended: 350-900 words)"})
            improvements.append("Consider condensing resume to 1-2 pages for maximum ATS readability.")
        else:
            checks.append({"item": "Content Length", "status": "Optimal", "detail": f"{word_count} words"})

        final_score = round(max(0.0, min(100.0, score)), 1)

        return {
            "formatting_score": final_score,
            "word_count": word_count,
            "checks": checks,
            "formatting_improvements": improvements,
            "summary": f"ATS structure score: {final_score}%. {len(checks) - len(improvements)} of {len(checks)} formatting criteria passed."
        }
