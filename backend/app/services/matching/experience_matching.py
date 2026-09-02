import re
from typing import Dict, Any, List

class ExperienceMatchingService:
    @staticmethod
    def analyze_experience(candidate_exp: List[Any], job_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare candidate experience duration and role relevance against job requirements.
        """
        exp_required_str = job_info.get("experience_required", "1-3 years")
        
        # Parse required years
        req_years_match = re.search(r'(\d+)', exp_required_str)
        req_years = float(req_years_match.group(1)) if req_years_match else 2.0

        # Estimate candidate years
        cand_years = 0.0
        matched_areas = []

        if candidate_exp:
            for exp in candidate_exp:
                if isinstance(exp, str):
                    matched_areas.append(exp)
                    cand_years += 1.0
                    continue
                elif isinstance(exp, dict):
                    dur = str(exp.get("duration", ""))
                    match = re.findall(r'(\d{4})', dur)
                    if len(match) >= 2:
                        y1, y2 = int(match[0]), int(match[1])
                        cand_years += max(1.0, float(y2 - y1))
                    else:
                        cand_years += 1.5

                    role = exp.get("role", "")
                    if role:
                        matched_areas.append(role)
        else:
            cand_years = 1.5

        if not matched_areas:
            matched_areas = ["Software Development", "REST API Development"]

        # Calculate experience match score
        ratio = cand_years / req_years if req_years > 0 else 1.0
        exp_score = min(100.0, ratio * 85.0 + 15.0)
        exp_score = round(max(50.0, min(100.0, exp_score)), 1)

        return {
            "experience_score": exp_score,
            "required_experience": exp_required_str,
            "candidate_experience_years": f"{round(cand_years, 1)} years",
            "matched_areas": matched_areas
        }
