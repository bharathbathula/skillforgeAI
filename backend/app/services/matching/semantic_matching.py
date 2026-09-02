from typing import Dict, Any
from app.services.embeddings.embedding_service import EmbeddingService

class SemanticMatchingService:
    @staticmethod
    def analyze_semantic(resume_sections: Dict[str, str], job_sections: Dict[str, str], raw_resume: str, raw_job: str) -> Dict[str, Any]:
        """
        Overall & Section-level semantic similarity calculation using vector embeddings.
        """
        # Overall vector similarity
        overall_sim = EmbeddingService.compute_similarity(raw_resume, raw_job)
        overall_score = round(max(40.0, min(98.0, overall_sim * 100.0)), 1)

        # Section-level similarities
        exp_vs_resp = EmbeddingService.compute_similarity(resume_sections.get("experience", ""), job_sections.get("responsibilities", ""))
        proj_vs_resp = EmbeddingService.compute_similarity(resume_sections.get("projects", ""), job_sections.get("responsibilities", ""))
        skills_vs_req = EmbeddingService.compute_similarity(resume_sections.get("skills", ""), job_sections.get("required_skills", ""))

        return {
            "semantic_score": overall_score,
            "overall_similarity_percentage": overall_score,
            "experience_vs_responsibilities": round(max(40.0, min(98.0, exp_vs_resp * 100.0)), 1),
            "projects_vs_responsibilities": round(max(40.0, min(98.0, proj_vs_resp * 100.0)), 1),
            "skills_vs_requirements": round(max(40.0, min(98.0, skills_vs_req * 100.0)), 1)
        }
