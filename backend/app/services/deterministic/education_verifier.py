import re
from typing import Dict, Any, List, Tuple

class EducationVerifier:
    """
    Verifies candidate education qualifications against Job Description requirements.
    Never fabricates degrees or institutions when resume education is absent.
    """

    DEGREE_HIERARCHY = {
        "phd": 5, "doctorate": 5, "doctor": 5,
        "master": 4, "ms": 4, "m.s": 4, "msc": 4, "m.tech": 4, "mba": 4, "mca": 4,
        "bachelor": 3, "bs": 3, "b.s": 3, "bsc": 3, "b.tech": 3, "b.e": 3, "bba": 3, "bca": 3,
        "associate": 2, "diploma": 2,
        "high school": 1, "secondary": 1
    }

    @classmethod
    def verify(
        cls,
        candidate_edu: List[Any],
        job_info: Dict[str, Any],
        raw_resume: str,
        raw_jd: str
    ) -> Dict[str, Any]:
        """
        Calculates deterministic education score and match status based on real evidence.
        """
        # 1. Parse JD required degree and field
        req_degree_str = job_info.get("education_required", "")
        if not req_degree_str:
            jd_lower = raw_jd.lower()
            if any(k in jd_lower for k in ["master's", "masters degree", "m.s.", "m.tech", "mba"]):
                req_degree_str = "Master's Degree in Computer Science or related field"
            elif any(k in jd_lower for k in ["bachelor's", "bachelors", "b.tech", "b.e.", "b.s."]):
                req_degree_str = "Bachelor's Degree in Computer Science or related field"
            elif "degree" in jd_lower:
                req_degree_str = "Degree in Computer Science or related field"
            else:
                req_degree_str = "Bachelor's Degree preferred or equivalent practical experience"

        req_level = cls._parse_degree_level(req_degree_str)

        # 2. Parse candidate education
        cand_level, candidate_degree, candidate_inst, cand_field = cls._parse_candidate_education(
            candidate_edu, raw_resume
        )

        # 3. Calculate score & status based on actual evidence
        if cand_level == 0:
            score = 0.0
            match_status = "No Education Credentials Detected"
            evidence = "No degree or formal higher education found in resume."
        else:
            if cand_level >= req_level:
                # Check field of study relevance
                field_lower = cand_field.lower()
                is_tech_field = any(k in field_lower for k in ["computer", "software", "information", "engineering", "data", "electronics", "technology", "math", "science", "physics"])
                
                if is_tech_field or not cand_field:
                    score = 100.0
                    match_status = "Fully Meets Education Requirement"
                    evidence = f"Candidate holds {candidate_degree} from {candidate_inst} in {cand_field or 'Technical Field'}."
                else:
                    score = 80.0
                    match_status = "Degree Level Met (Non-CS Major)"
                    evidence = f"Candidate holds {candidate_degree} from {candidate_inst} in {cand_field}."
            elif cand_level == req_level - 1:
                score = 65.0
                match_status = "Partially Meets Requirement"
                evidence = f"Candidate holds {candidate_degree} ({cand_level}/5) vs required level ({req_level}/5)."
            else:
                score = 40.0
                match_status = "Below Required Degree Level"
                evidence = f"Candidate holds {candidate_degree} from {candidate_inst} vs {req_degree_str} required."

        return {
            "education_score": score,
            "required_education": req_degree_str,
            "candidate_degree": candidate_degree,
            "candidate_institution": candidate_inst,
            "candidate_field": cand_field,
            "match_status": match_status,
            "evidence": evidence
        }

    @classmethod
    def _parse_degree_level(cls, text: str) -> int:
        """Determines academic tier level (1-5) from text."""
        t_low = text.lower()
        for deg, level in cls.DEGREE_HIERARCHY.items():
            if deg in t_low:
                return level
        return 3  # Default baseline is Bachelor's (3)

    @classmethod
    def _parse_candidate_education(cls, candidate_edu: List[Any], raw_resume: str) -> Tuple[int, str, str, str]:
        """Extracts candidate degree level, name, institution, and major."""
        if candidate_edu and isinstance(candidate_edu, list):
            first = candidate_edu[0]
            if isinstance(first, dict):
                deg = str(first.get("degree") or "")
                inst = str(first.get("institution") or "")
                field = str(first.get("field_of_study") or first.get("field") or "")
                if deg:
                    level = cls._parse_degree_level(f"{deg} {field}")
                    return level, deg, inst, field
            elif isinstance(first, str) and first.strip():
                level = cls._parse_degree_level(first)
                return level, first, "University / College", ""

        # Scan raw resume text for education lines
        if raw_resume:
            lines = raw_resume.split('\n')
            in_edu = False
            for line in lines:
                l_low = line.strip().lower()
                if any(k in l_low for k in ["education", "academic background", "qualifications"]):
                    in_edu = True
                    continue
                if in_edu:
                    if any(k in l_low for k in ["experience", "projects", "skills", "certifications"]):
                        break
                    for deg, level in cls.DEGREE_HIERARCHY.items():
                        if deg in l_low:
                            return level, line.strip()[:60], "University / College", ""

        # Absolutely no education found — return zero (never fabricate)
        return 0, "None", "None", ""
