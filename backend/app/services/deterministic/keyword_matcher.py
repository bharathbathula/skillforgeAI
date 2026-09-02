import re
from typing import Dict, Any, List, Set, Optional
from app.services.nlp.technical_tokenizer import TechnicalTokenizer
from app.services.nlp.skill_taxonomy import SkillTaxonomy

class KeywordMatcher:
    """
    Dynamic, context-aware keyword matching engine.
    Extracts relevant domain and technical keywords strictly from the target Job Description,
    and calculates exact coverage and density in candidate resume.
    """

    @classmethod
    def analyze(
        cls,
        raw_resume: str,
        raw_jd: str,
        job_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extracts JD keywords dynamically and matches against resume text.
        """
        # 1. Dynamically extract keywords from JD if not provided
        if not job_keywords or len(job_keywords) == 0:
            target_keywords = cls.extract_target_keywords_from_jd(raw_jd)
        else:
            target_keywords = list(set(job_keywords))

        if not target_keywords:
            target_keywords = ["Software", "Development", "API", "System", "Database"]

        # 2. Match against resume text
        resume_lower = raw_resume.lower()
        found = []
        missing = []

        for kw in target_keywords:
            kw_clean = kw.strip()
            if not kw_clean:
                continue

            # Check boundary regex or normalized match
            kw_norm = TechnicalTokenizer.normalize_skill(kw_clean)
            pattern = r'(?:\b|(?<=[\s,;:(/]))' + re.escape(kw_clean.lower()) + r'(?:\b|(?=[\s,;:)/.]))'
            
            if re.search(pattern, resume_lower) or kw_norm in resume_lower:
                found.append(kw_clean)
            else:
                missing.append(kw_clean)

        total_kws = len(target_keywords)
        found_count = len(found)
        coverage_pct = round((found_count / total_kws * 100.0), 1) if total_kws > 0 else 0.0

        return {
            "keyword_score": coverage_pct,
            "total_keywords_count": total_kws,
            "found_keywords_count": found_count,
            "found_keywords": sorted(list(set(found))),
            "missing_keywords": sorted(list(set(missing))),
            "density_analysis": f"Matched {found_count} of {total_kws} target keywords from the Job Description ({coverage_pct}% coverage)."
        }

    @classmethod
    def extract_target_keywords_from_jd(cls, raw_jd: str) -> List[str]:
        """Dynamically extracts meaningful technical and domain terms from JD."""
        # 1. Extract from skill taxonomy
        skills = SkillTaxonomy.extract_flat_skill_list(raw_jd)

        # 2. Extract technical tokens & capitalized multi-word phrases
        tech_tokens = TechnicalTokenizer.extract_keywords_filtered(raw_jd)
        
        # Filter tokens with meaningful frequency
        token_freq: Dict[str, int] = {}
        for t in tech_tokens:
            low = t.lower()
            token_freq[low] = token_freq.get(low, 0) + 1

        top_tokens = [t for t, freq in sorted(token_freq.items(), key=lambda x: x[1], reverse=True) if len(t) >= 3 and not t.isdigit()][:15]

        combined = list(set(skills + top_tokens))
        return sorted(combined[:20], key=lambda x: len(x), reverse=False)
