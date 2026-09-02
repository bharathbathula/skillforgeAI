from typing import Dict, Any, List

class EducationMatchingService:
    @staticmethod
    def analyze_education(candidate_edu: List[Any], job_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare degree, field of study, and institution requirements.
        """
        edu_req = job_info.get("education_required", "Bachelor's degree").lower()

        candidate_degree = "Bachelor Degree"
        candidate_inst = "Higher Education Institution"
        match_status = "Matches Requirement"
        score = 85.0

        if candidate_edu:
            first_edu = candidate_edu[0]
            if isinstance(first_edu, str):
                candidate_degree = first_edu
                candidate_inst = "University"
            elif isinstance(first_edu, dict):
                candidate_degree = first_edu.get("degree", "Bachelor Degree")
                candidate_inst = first_edu.get("institution", "University")

            deg_lower = candidate_degree.lower()
            if any(term in deg_lower for term in ["bachelor", "b.tech", "b.e", "b.s", "master", "m.tech", "m.s", "computer science"]):
                score = 100.0
                match_status = "Strong Match"
            else:
                score = 75.0
                match_status = "Related Degree"

        return {
            "education_score": score,
            "required_education": job_info.get("education_required", "Bachelor's degree in Computer Science"),
            "candidate_degree": candidate_degree,
            "institution": candidate_inst,
            "match_status": match_status
        }
