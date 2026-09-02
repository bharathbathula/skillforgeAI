from typing import Dict, Any, List
from app.services.deterministic.skills_analyzer import SkillsAnalyzer
from app.services.deterministic.experience_calculator import ExperienceCalculator
from app.services.deterministic.responsibility_matcher import ResponsibilityMatcher
from app.services.deterministic.education_verifier import EducationVerifier
from app.services.deterministic.keyword_matcher import KeywordMatcher
from app.services.deterministic.formatting_auditor import FormattingAuditor
from app.services.matching.project_matching import ProjectMatchingService
from app.services.embeddings.embedding_service import EmbeddingService

class DeterministicScorer:
    """
    Orchestrates all deterministic & objective evaluation modules.
    Produces an auditable, reproducible baseline ATS score with zero hallucinations.
    """

    @classmethod
    def run_full_deterministic_analysis(
        cls,
        parsed_resume: Dict[str, Any],
        parsed_job: Dict[str, Any],
        raw_resume: str,
        raw_jd: str,
        resume_sections: Dict[str, str],
        job_sections: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Runs all objective analyses and combines them into an auditable evaluation.
        """
        # 1. Skills Analysis (Required vs Preferred)
        skills_res = SkillsAnalyzer.analyze(parsed_resume, parsed_job, raw_resume, raw_jd)

        # 2. Experience Calculation (Exact dates & required ratio)
        exp_res = ExperienceCalculator.calculate(
            parsed_resume.get("experience", []),
            parsed_job.get("job_info", {}),
            raw_resume,
            raw_jd
        )

        # 3. Individual Responsibility Matching
        resp_res = ResponsibilityMatcher.analyze(parsed_job, parsed_resume, raw_resume, raw_jd)

        # 4. Education Verification
        edu_res = EducationVerifier.verify(
            parsed_resume.get("education", []),
            parsed_job.get("job_info", {}),
            raw_resume,
            raw_jd
        )

        # 5. Dynamic Keyword Matching
        kw_res = KeywordMatcher.analyze(raw_resume, raw_jd, parsed_job.get("keywords", []))

        # 6. Project Matching
        proj_res = ProjectMatchingService.analyze_projects(parsed_resume.get("projects", []), parsed_job)

        # 7. Semantic Vector Similarity
        sem_sim = EmbeddingService.compute_similarity(raw_resume, raw_jd)
        semantic_score = round(max(0.0, min(100.0, sem_sim * 100.0)), 1)

        # 8. Formatting & ATS Readability
        fmt_res = FormattingAuditor.audit(parsed_resume, raw_resume)

        # 9. Calculate Deterministic Overall Score
        # Weights: Skills 25%, Experience 20%, Responsibilities 20%, Keywords 10%, Semantic 10%, Education 5%, Projects 5%, Formatting 5%
        skill_s = skills_res["skill_score"]
        exp_s = exp_res["experience_score"]
        resp_s = resp_res["responsibility_score"]
        kw_s = kw_res["keyword_score"]
        sem_s = semantic_score
        edu_s = edu_res["education_score"]
        proj_s = proj_res["project_score"]
        fmt_s = fmt_res["formatting_score"]

        deterministic_overall = (
            (skill_s * 0.25) +
            (exp_s * 0.20) +
            (resp_s * 0.20) +
            (kw_s * 0.10) +
            (sem_s * 0.10) +
            (edu_s * 0.05) +
            (proj_s * 0.05) +
            (fmt_s * 0.05)
        )
        deterministic_overall = round(max(0.0, min(100.0, deterministic_overall)), 1)

        parameter_scores = {
            "overall_score": deterministic_overall,
            "skill_score": skill_s,
            "experience_score": exp_s,
            "responsibility_score": resp_s,
            "keyword_score": kw_s,
            "semantic_score": sem_s,
            "education_score": edu_s,
            "project_score": proj_s,
            "formatting_score": fmt_s
        }

        return {
            "deterministic_score": deterministic_overall,
            "parameter_scores": parameter_scores,
            "skills": skills_res,
            "experience": exp_res,
            "responsibilities": resp_res,
            "education": edu_res,
            "keywords": kw_res,
            "projects": proj_res,
            "semantic_similarity": semantic_score,
            "formatting": fmt_res
        }
