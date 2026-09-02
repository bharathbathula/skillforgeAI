import re
from typing import Dict, Any, List

class KeywordMatchingService:
    @staticmethod
    def analyze_keywords(resume_text: str, job_keywords: List[str]) -> Dict[str, Any]:
        """
        Calculate Keyword Coverage Ratio and identify found vs missing keywords.
        """
        if not job_keywords:
            job_keywords = ["Python", "FastAPI", "PostgreSQL", "REST API", "Database", "Git"]

        resume_text_lower = resume_text.lower()
        found_keywords = []
        missing_keywords = []

        for kw in job_keywords:
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            if re.search(pattern, resume_text_lower):
                found_keywords.append(kw)
            else:
                missing_keywords.append(kw)

        found_count = len(found_keywords)
        total_count = len(job_keywords)

        coverage_ratio = (found_count / total_count) if total_count > 0 else 0.8
        keyword_score = round(max(0.0, min(100.0, coverage_ratio * 100.0)), 1)

        return {
            "keyword_score": keyword_score,
            "total_keywords_count": total_count,
            "found_keywords_count": found_count,
            "found_keywords": sorted(list(set(found_keywords))),
            "missing_keywords": sorted(list(set(missing_keywords)))
        }
