import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class ExperienceCalculator:
    """
    Deterministic, evidence-based experience calculation engine.
    Computes exact chronological work experience, detects internships vs full-time,
    and calculates accurate ratio against JD requirements with auditable explanations.
    """

    MONTH_MAP = {
        "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
        "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
        "aug": 8, "august": 8, "sep": 9, "september": 9, "sept": 9, "oct": 10, "october": 10,
        "nov": 11, "november": 11, "dec": 12, "december": 12
    }

    @classmethod
    def calculate(
        cls,
        candidate_exp: List[Any],
        job_info: Dict[str, Any],
        raw_resume: str,
        raw_jd: str
    ) -> Dict[str, Any]:
        """
        Calculates exact experience score, relevant vs total years, and evidence.
        """
        # 1. Parse required experience from JD
        req_years, req_evidence = cls.extract_required_years(job_info, raw_jd)

        # 2. Parse candidate work history
        role_evaluations, total_years, relevant_years, internship_years = cls.parse_candidate_experience(
            candidate_exp, raw_resume, raw_jd
        )

        # 3. Deterministic score calculation
        if total_years == 0.0:
            exp_score = 0.0
            gap_summary = f"No professional experience detected in resume. Role requires {req_years} years."
            match_status = "No Experience Found"
        else:
            # Weight relevant experience at 100%, general experience at 40%, internships at 50%
            effective_years = relevant_years + ((total_years - relevant_years) * 0.4) + (internship_years * 0.5)
            
            if req_years <= 0.0:
                exp_score = 100.0 if total_years > 0 else 0.0
            else:
                ratio = effective_years / req_years
                exp_score = round(min(100.0, ratio * 100.0), 1)

            if exp_score >= 90.0:
                match_status = "Fully Meets / Exceeds Requirement"
                gap_summary = f"Candidate has {round(relevant_years, 1)} years of relevant experience, meeting the {req_years} years requirement."
            elif exp_score >= 60.0:
                match_status = "Partially Meets Requirement"
                gap_summary = f"Candidate has {round(relevant_years, 1)} years of relevant experience vs {req_years} years required ({round(req_years - relevant_years, 1)} yr gap)."
            else:
                match_status = "Below Requirement"
                gap_summary = f"Candidate has {round(relevant_years, 1)} years of experience, falling short of the {req_years} years required."

        explanation = (
            f"Required: {req_years} years ({req_evidence}). "
            f"Candidate: {round(relevant_years, 1)} yrs relevant, {round(total_years, 1)} yrs total across {len(role_evaluations)} roles. "
            f"Score: {exp_score}%"
        )

        return {
            "experience_score": exp_score,
            "required_experience_years": req_years,
            "required_experience_text": req_evidence,
            "candidate_total_years": round(total_years, 1),
            "candidate_relevant_years": round(relevant_years, 1),
            "candidate_internship_years": round(internship_years, 1),
            "match_status": match_status,
            "gap_summary": gap_summary,
            "explanation": explanation,
            "role_breakdown": role_evaluations
        }

    @classmethod
    def extract_required_years(cls, job_info: Dict[str, Any], raw_jd: str) -> Tuple[float, str]:
        """Extract explicit required years of experience from JD text and metadata."""
        jd_combined = f"{job_info.get('title', '')} {job_info.get('experience_required', '')} {raw_jd}".lower()

        # Match patterns like: "5+ years", "3 to 5 years", "minimum 4 years", "2-4 yrs"
        explicit_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:\+|to|-|\s*-\s*)?\s*(\d+(?:\.\d+)?)?\s*(?:years?|yrs?)(?:\s+of\s+experience)?', jd_combined)
        if explicit_match:
            y1 = float(explicit_match.group(1))
            y2 = float(explicit_match.group(2)) if explicit_match.group(2) else y1
            req_years = max(y1, y2)
            evidence = explicit_match.group(0).strip()
            return req_years, f"Explicit requirement in JD: '{evidence}'"

        # Check seniority keywords if no numeric years found
        title = job_info.get("title", "").lower()
        if any(w in title for w in ["intern", "trainee", "entry level", "graduate"]):
            return 0.5, "Inferred from Entry-level / Intern role title"
        elif any(w in title for w in ["junior", "associate"]):
            return 1.0, "Inferred from Junior role title"
        elif any(w in title for w in ["senior", "sr.", "sr ", "lead", "principal", "staff", "architect", "manager"]):
            return 5.0, "Inferred from Senior / Lead role title"

        # Default fallback
        return 2.0, "Standard industry baseline (2.0 years) for unspecified role"

    @classmethod
    def parse_candidate_experience(
        cls,
        candidate_exp: List[Any],
        raw_resume: str,
        raw_jd: str
    ) -> Tuple[List[Dict[str, Any]], float, float, float]:
        """
        Parses candidate experience items, estimates dates & durations,
        and determines relevant vs total vs internship experience.
        """
        if not candidate_exp or not isinstance(candidate_exp, list):
            # Check raw text if structured experience list is empty
            lines = raw_resume.split('\n')
            exp_lines = [l for l in lines if any(k in l.lower() for k in ["engineer", "developer", "intern", "consultant", "analyst", "manager"])]
            if not exp_lines:
                return [], 0.0, 0.0, 0.0

        role_evals = []
        total_years = 0.0
        relevant_years = 0.0
        internship_years = 0.0

        jd_tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', raw_jd.lower()))

        for exp in candidate_exp:
            if isinstance(exp, str):
                role_title = exp
                company = "Organization"
                duration_str = ""
                resps = []
                techs = []
            elif isinstance(exp, dict):
                role_title = exp.get("role", "Software Role")
                company = exp.get("company", "Organization")
                duration_str = exp.get("duration", "")
                resps = exp.get("responsibilities", [])
                techs = exp.get("technologies", [])
            else:
                continue

            dur_years = cls.parse_duration_string(duration_str, role_title)
            is_intern = any(k in role_title.lower() for k in ["intern", "trainee", "apprentice", "fellow"])

            # Check domain relevance against target JD
            role_text = f"{role_title} {' '.join(resps)} {' '.join(techs)}".lower()
            role_tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', role_text))
            overlap = len(role_tokens.intersection(jd_tokens))
            is_relevant = overlap >= 3 or any(t in role_text for t in ["software", "developer", "engineer", "backend", "frontend", "full stack", "api", "database", "python", "data"])

            total_years += dur_years
            if is_intern:
                internship_years += dur_years
            elif is_relevant:
                relevant_years += dur_years
            else:
                relevant_years += (dur_years * 0.3)

            role_evals.append({
                "role": role_title,
                "company": company,
                "duration": duration_str if duration_str else f"{dur_years} year(s)",
                "duration_years": round(dur_years, 2),
                "is_internship": is_intern,
                "is_relevant": is_relevant,
                "technologies": techs[:4] if techs else []
            })

        return role_evals, total_years, relevant_years, internship_years

    @classmethod
    def parse_duration_string(cls, duration_str: str, role_title: str) -> float:
        """Parse years from date ranges like '2022 - 2024', 'Jan 2023 - Present', '6 months'."""
        if not duration_str:
            return 0.5 if "intern" in role_title.lower() else 1.0

        dur_clean = duration_str.lower().strip()

        # Match explicit months: "6 months", "3 mos"
        month_match = re.search(r'(\d+)\s*(?:months?|mos?)', dur_clean)
        if month_match:
            return round(int(month_match.group(1)) / 12.0, 2)

        # Match explicit years: "2.5 years", "3 yrs"
        yr_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)', dur_clean)
        if yr_match:
            return float(yr_match.group(1))

        # Match Year to Year: "2021 - 2024" or "2022-Present"
        years = re.findall(r'(\d{4})', dur_clean)
        current_year = datetime.now().year

        if len(years) >= 2:
            y1, y2 = int(years[0]), int(years[1])
            return max(0.5, float(abs(y2 - y1)))
        elif len(years) == 1:
            if "present" in dur_clean or "current" in dur_clean or "now" in dur_clean:
                y1 = int(years[0])
                return max(0.5, float(current_year - y1))
            else:
                return 1.0

        return 0.5 if "intern" in role_title.lower() else 1.0
