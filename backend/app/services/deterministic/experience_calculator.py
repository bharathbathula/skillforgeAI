import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class ExperienceCalculator:
    """
    Deterministic, evidence-based experience calculation engine.
    Computes exact chronological work experience with interval merging to prevent
    double-counting overlapping roles, parses standard date formats and current/ongoing roles,
    and calculates accurate ratios against JD requirements with auditable explanations.
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

        # 2. Parse candidate work history with overlapping interval reconciliation
        role_evaluations, total_years, relevant_years, internship_years = cls.parse_candidate_experience(
            candidate_exp, raw_resume, raw_jd, job_info
        )


        # 3. Deterministic score calculation
        if req_years <= 0.0:
            exp_score = 100.0
            if total_years > 0.0:
                gap_summary = f"No minimum experience required in JD. Candidate possesses {round(relevant_years, 1)} years of experience."
                match_status = "Fully Meets / Exceeds Requirement"
            else:
                gap_summary = "No minimum experience required for this role. Baseline criteria satisfied."
                match_status = "Meets Baseline Requirement"
        elif total_years <= 0.0:
            exp_score = 0.0
            gap_summary = f"No professional experience detected in resume. Role requires {req_years} years."
            match_status = "No Experience Found"
        else:
            # Weight relevant experience at 100%, general experience at 40%, internships at 50%
            effective_years = relevant_years + ((total_years - relevant_years) * 0.4) + (internship_years * 0.5)
            # Ensure effective years never unrealistically exceeds total calendar experience
            effective_years = min(total_years, effective_years)

            ratio = effective_years / req_years
            exp_score = round(min(100.0, max(0.0, ratio * 100.0)), 1)

            if exp_score >= 90.0:
                match_status = "Fully Meets / Exceeds Requirement"
                gap_summary = f"Candidate has {round(relevant_years, 1)} years of relevant experience, meeting the {req_years} years requirement."
            elif exp_score >= 60.0:
                match_status = "Partially Meets Requirement"
                gap_summary = f"Candidate has {round(relevant_years, 1)} years of relevant experience vs {req_years} years required ({round(max(0.0, req_years - relevant_years), 1)} yr gap)."
            else:
                match_status = "Below Requirement"
                gap_summary = f"Candidate has {round(relevant_years, 1)} years of experience, falling short of the {req_years} years required."

        explanation = (
            f"Required: {req_years} years ({req_evidence}). "
            f"Candidate: {round(relevant_years, 1)} yrs relevant, {round(total_years, 1)} yrs total (de-overlapped) across {len(role_evaluations)} roles. "
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
        """
        Extract required years of experience from JD text and metadata.
        Robustly handles '2 years', '2+ years', 'minimum 3 years', ranges ('3-5 years'), and absent requirements.
        """
        if not isinstance(job_info, dict):
            job_info = {}

        jd_combined = f"{job_info.get('title', '')} {job_info.get('experience_required', '')} {raw_jd}".lower()

        # Pattern 1: Explicit ranges like "3 to 5 years", "3-5 years", "2-4 yrs"
        range_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:to|-|\s*-\s*)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)(?:\s+(?:of\s+)?experience)?', jd_combined)
        if range_match:
            y1 = float(range_match.group(1))
            y2 = float(range_match.group(2))
            min_y = min(y1, y2)
            evidence = range_match.group(0).strip()
            return min_y, f"Explicit range in JD: '{evidence}' (entry baseline: {min_y} years)"

        # Pattern 2: Explicit minimums like "minimum 3 years", "min 2 years", "at least 4 years"
        min_match = re.search(r'(?:minimum|min\.?|at least)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)(?:\s+(?:of\s+)?experience)?', jd_combined)
        if min_match:
            req_years = float(min_match.group(1))
            evidence = min_match.group(0).strip()
            return req_years, f"Explicit minimum requirement in JD: '{evidence}'"

        # Pattern 3: Plus notation like "5+ years", "3+ yrs", "2 + years"
        plus_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:\+|plus)\s*(?:years?|yrs?)(?:\s+(?:of\s+)?experience)?', jd_combined)
        if plus_match:
            req_years = float(plus_match.group(1))
            evidence = plus_match.group(0).strip()
            return req_years, f"Explicit requirement in JD: '{evidence}'"

        # Pattern 4: Standard "X years of experience" or "X years"
        std_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)(?:\s+(?:of\s+)?experience)?', jd_combined)
        if std_match:
            req_years = float(std_match.group(1))
            evidence = std_match.group(0).strip()
            return req_years, f"Explicit requirement in JD: '{evidence}'"

        # Pattern 5: Inferred from role seniority if no numeric years found
        title = job_info.get("title", "").lower()
        if any(w in title for w in ["intern", "trainee", "entry level", "entry-level", "graduate"]):
            return 0.5, "Inferred from Entry-level / Intern role title"
        elif any(w in title for w in ["junior", "associate"]):
            return 1.0, "Inferred from Junior role title"
        elif any(w in title for w in ["senior", "sr.", "sr ", "lead", "principal", "staff", "architect", "manager"]):
            return 5.0, "Inferred from Senior / Lead role title"

        # Pattern 6: Absent requirement -> 0.0 years (no requirement)
        return 0.0, "No explicit experience requirement specified in Job Description"

    @classmethod
    def parse_date_range(cls, duration_str: str) -> Optional[Tuple[float, float]]:
        """
        Parses start and end dates from date range strings into fractional years.
        Supports 'Jan 2021 - Mar 2023', '06/2020 - Present', '2019 - 2022', etc.
        """
        if not duration_str or not isinstance(duration_str, str):
            return None

        dur_clean = duration_str.strip().lower()
        now = datetime.now()
        current_frac = now.year + (now.month / 12.0)

        # 1. Month Year - Month Year: "Jan 2021 - Mar 2023", "January 2021 to March 2023"
        m_range = re.search(r'([a-z]+)\.?\s*(\d{4})\s*(?:-|–|—|to)\s*([a-z]+)\.?\s*(\d{4})', dur_clean)
        if m_range:
            m1, y1_str, m2, y2_str = m_range.group(1), m_range.group(2), m_range.group(3), m_range.group(4)
            if m1 in cls.MONTH_MAP and m2 in cls.MONTH_MAP:
                start = int(y1_str) + (cls.MONTH_MAP[m1] - 1) / 12.0
                end = int(y2_str) + cls.MONTH_MAP[m2] / 12.0
                return (min(start, end), max(start, end))

        # 2. Month Year - Present / Current: "Jan 2022 - Present", "March 2023 to Current"
        m_pres = re.search(r'([a-z]+)\.?\s*(\d{4})\s*(?:-|–|—|to)\s*(present|current|ongoing|now)', dur_clean)
        if m_pres:
            m1, y1_str = m_pres.group(1), m_pres.group(2)
            if m1 in cls.MONTH_MAP:
                start = int(y1_str) + (cls.MONTH_MAP[m1] - 1) / 12.0
                return (start, current_frac)

        # 3. MM/YYYY - MM/YYYY or MM-YYYY to MM-YYYY
        d_range = re.search(r'(\d{1,2})[/-](\d{4})\s*(?:-|–|—|to)\s*(\d{1,2})[/-](\d{4})', dur_clean)
        if d_range:
            m1, y1, m2, y2 = int(d_range.group(1)), int(d_range.group(2)), int(d_range.group(3)), int(d_range.group(4))
            start = y1 + (max(1, min(12, m1)) - 1) / 12.0
            end = y2 + max(1, min(12, m2)) / 12.0
            return (min(start, end), max(start, end))

        # 4. MM/YYYY - Present
        d_pres = re.search(r'(\d{1,2})[/-](\d{4})\s*(?:-|–|—|to)\s*(present|current|ongoing|now)', dur_clean)
        if d_pres:
            m1, y1 = int(d_pres.group(1)), int(d_pres.group(2))
            start = y1 + (max(1, min(12, m1)) - 1) / 12.0
            return (start, current_frac)

        # 5. YYYY - YYYY: "2021 - 2024", "2019 to 2021"
        y_range = re.search(r'(\d{4})\s*(?:-|–|—|to)\s*(\d{4})', dur_clean)
        if y_range:
            y1, y2 = int(y_range.group(1)), int(y_range.group(2))
            start = float(min(y1, y2))
            end = float(max(y1, y2))
            # If same year (e.g. 2023 - 2023), treat as 0.5 year minimum
            if end == start:
                end = start + 0.5
            return (start, end)

        # 6. YYYY - Present / Current: "2022 - Present", "2023 - Current"
        y_pres = re.search(r'(\d{4})\s*(?:-|–|—|to)\s*(present|current|ongoing|now)', dur_clean)
        if y_pres:
            y1 = int(y_pres.group(1))
            return (float(y1), current_frac)

        return None

    @classmethod
    def merge_intervals(cls, intervals: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Merges overlapping calendar intervals to eliminate double-counting of simultaneous roles.
        """
        if not intervals:
            return []

        # Filter invalid intervals and sort by start time
        valid = [(s, e) for s, e in intervals if e > s]
        if not valid:
            return []

        sorted_intervals = sorted(valid, key=lambda x: x[0])
        merged = [sorted_intervals[0]]

        for current in sorted_intervals[1:]:
            prev_start, prev_end = merged[-1]
            curr_start, curr_end = current

            if curr_start <= prev_end:
                # Overlap detected: extend end date of previous interval
                merged[-1] = (prev_start, max(prev_end, curr_end))
            else:
                merged.append(current)

        return merged

    @classmethod
    def parse_candidate_experience(
        cls,
        candidate_exp: List[Any],
        raw_resume: str,
        raw_jd: str,
        job_info: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Dict[str, Any]], float, float, float]:
        """
        Parses candidate experience items, estimates durations, detects domain relevance,
        and merges overlapping intervals to compute accurate non-duplicated calendar experience.
        """
        if not candidate_exp or not isinstance(candidate_exp, list):
            # Fallback: scan raw resume text for role lines if structured list is empty
            lines = raw_resume.split('\n')
            exp_lines = [l for l in lines if any(k in l.lower() for k in ["engineer", "developer", "dev", "intern", "consultant", "analyst", "architect"])]
            if not exp_lines:
                return [], 0.0, 0.0, 0.0

        role_evals = []
        all_intervals: List[Tuple[float, float]] = []
        relevant_intervals: List[Tuple[float, float]] = []
        unbounded_total_years = 0.0
        unbounded_relevant_years = 0.0
        internship_years = 0.0

        jd_tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', raw_jd.lower()))
        target_title = (job_info.get("title", "") if isinstance(job_info, dict) else "").lower()
        target_tokens = set(re.findall(r'\b[a-zA-Z]{2,}\b', target_title))

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

            # 1. Parse date range interval
            interval = cls.parse_date_range(duration_str)
            if interval:
                dur_years = max(0.1, round(interval[1] - interval[0], 2))
                all_intervals.append(interval)
            else:
                # Fallback to duration string regex or sensible defaults
                dur_years = cls.parse_duration_string(duration_str, role_title)
                unbounded_total_years += dur_years

            is_intern = any(k in role_title.lower() for k in ["intern", "trainee", "apprentice", "fellow"])

            # 2. Check domain relevance against target JD
            role_text = f"{role_title} {' '.join(resps) if isinstance(resps, list) else str(resps)} {' '.join(techs) if isinstance(techs, list) else str(techs)}".lower()
            role_tokens = set(re.findall(r'\b[a-zA-Z]{2,}\b', role_text))
            overlap = len(role_tokens.intersection(jd_tokens))
            is_relevant = (
                overlap >= 2
                or len(role_tokens.intersection(target_tokens)) >= 1
                or any(t in role_text for t in [
                    "software", "developer", "dev", "engineer", "backend", "frontend",
                    "full stack", "fullstack", "api", "database", "python", "data", "web",
                    "architect", "programmer", "coder", "cloud", "devops"
                ])
            )

            if is_intern:
                internship_years += dur_years
            elif is_relevant:
                if interval:
                    relevant_intervals.append(interval)
                else:
                    unbounded_relevant_years += dur_years

            role_evals.append({
                "role": role_title,
                "company": company,
                "duration": duration_str if duration_str else f"{dur_years} year(s)",
                "duration_years": round(dur_years, 2),
                "is_internship": is_intern,
                "is_relevant": is_relevant,
                "technologies": techs[:4] if isinstance(techs, list) and techs else []
            })

        # 3. Calculate merged calendar duration (de-overlapped)
        if all_intervals:
            merged_all = cls.merge_intervals(all_intervals)
            merged_calendar_years = sum(end - start for start, end in merged_all)
            total_years = round(merged_calendar_years + unbounded_total_years, 2)
        else:
            total_years = round(unbounded_total_years, 2)

        if relevant_intervals:
            merged_rel = cls.merge_intervals(relevant_intervals)
            relevant_years = round(sum(end - start for start, end in merged_rel) + unbounded_relevant_years, 2)
        else:
            rel_unbounded = sum(
                e["duration_years"] for e in role_evals if e["is_relevant"] and not e["is_internship"]
            )
            relevant_years = round(rel_unbounded, 2)

        # Ensure relevant_years does not exceed total_years
        relevant_years = min(total_years, relevant_years)

        return role_evals, float(total_years), float(relevant_years), float(internship_years)


    @classmethod
    def parse_duration_string(cls, duration_str: str, role_title: str) -> float:
        """
        Fallback parser for durations like '2.5 years', '6 months', '2021 - 2023', etc.
        Safely handles missing or malformed dates without crashing.
        """
        if not duration_str or not isinstance(duration_str, str):
            return 0.5 if "intern" in role_title.lower() else 1.0

        dur_clean = duration_str.lower().strip()

        # Match explicit months: "6 months", "3 mos"
        month_match = re.search(r'(\d+)\s*(?:months?|mos?)', dur_clean)
        if month_match:
            return max(0.1, round(int(month_match.group(1)) / 12.0, 2))

        # Match explicit years: "2.5 years", "3 yrs"
        yr_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)', dur_clean)
        if yr_match:
            return max(0.1, float(yr_match.group(1)))

        # Match Year to Year: "2021 - 2024" or "2022 - Present"
        years = re.findall(r'(\d{4})', dur_clean)
        current_year = datetime.now().year

        if len(years) >= 2:
            y1, y2 = int(years[0]), int(years[1])
            diff = abs(y2 - y1)
            return max(0.5, float(diff))
        elif len(years) == 1:
            if any(w in dur_clean for w in ["present", "current", "ongoing", "now"]):
                y1 = int(years[0])
                diff = current_year - y1
                return max(0.5, float(diff))
            else:
                return 1.0

        return 0.5 if "intern" in role_title.lower() else 1.0
