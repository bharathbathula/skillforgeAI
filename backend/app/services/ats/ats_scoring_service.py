import asyncio
import logging
from typing import Dict, Any, List
from app.services.deterministic.deterministic_scorer import DeterministicScorer
from app.services.ai.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)

class ATSScoringService:
    """
    Core ATS Scoring and Analysis Engine.

    Architectural Invariants:
    1. The core ATS compatibility score is 100% deterministic and auditable.
       It is derived exclusively from the project's own analytical logic and
       pretrained sentence-transformer embeddings (all-MiniLM-L6-v2 / TF-IDF fallback).
    2. External AI models NEVER participate in or alter the ATS score.
    3. The pipeline completes successfully and returns full analytical reports
       even if no external AI API key is configured.
    4. Downstream recommendations are generated as an optional advisory layer.
    """

    @staticmethod
    def calculate_formatting_score(resume_parsed: Dict[str, Any], raw_text: str) -> float:
        from app.services.deterministic.formatting_auditor import FormattingAuditor
        res = FormattingAuditor.audit(resume_parsed, raw_text)
        return res.get("formatting_score", 85.0)

    @classmethod
    def compute_full_ats_report(
        cls,
        resume_parsed: Dict[str, Any],
        job_parsed: Dict[str, Any],
        raw_resume: str,
        raw_job: str,
        resume_sections: Dict[str, str],
        job_sections: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper executing deterministic ATS analysis and downstream recommendations.
        """
        try:
            return asyncio.run(
                cls.compute_full_ats_report_async(
                    resume_parsed, job_parsed, raw_resume, raw_job, resume_sections, job_sections
                )
            )
        except RuntimeError:
            try:
                import nest_asyncio
                nest_asyncio.apply()
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(
                    cls.compute_full_ats_report_async(
                        resume_parsed, job_parsed, raw_resume, raw_job, resume_sections, job_sections
                    )
                )
            except Exception:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(
                        cls.compute_full_ats_report_async(
                            resume_parsed, job_parsed, raw_resume, raw_job, resume_sections, job_sections
                        )
                    )
                finally:
                    loop.close()

    @classmethod
    async def compute_full_ats_report_async(
        cls,
        resume_parsed: Dict[str, Any],
        job_parsed: Dict[str, Any],
        raw_resume: str,
        raw_job: str,
        resume_sections: Dict[str, str],
        job_sections: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Executes end-to-end ATS evaluation:
        1. Full deterministic multi-component analysis (skills, experience, responsibilities,
           education, projects, keywords, formatting, semantic vector similarity).
        2. Grounded deterministic scoring formula.
        3. Optional downstream recommendation layer.
        """
        if not isinstance(resume_parsed, dict):
            resume_parsed = {}
        if not isinstance(job_parsed, dict):
            job_parsed = {}

        # 1. Run full deterministic evaluation (core engine)
        deterministic_data = DeterministicScorer.run_full_deterministic_analysis(
            parsed_resume=resume_parsed,
            parsed_job=job_parsed,
            raw_resume=raw_resume,
            raw_jd=raw_job,
            resume_sections=resume_sections,
            job_sections=job_sections
        )

        final_score = deterministic_data["deterministic_score"]
        score_breakdown = deterministic_data["parameter_scores"]

        skills_res = deterministic_data["skills"]
        proj_res = deterministic_data["projects"]
        exp_res = deterministic_data["experience"]
        edu_res = deterministic_data["education"]
        kw_res = deterministic_data["keywords"]
        resp_res = deterministic_data["responsibilities"]
        fmt_res = deterministic_data["formatting"]
        semantic_sim = deterministic_data["semantic_similarity"]

        # Determine alignment label based on objective score
        if final_score >= 85.0:
            job_fit = "Exceptional Alignment"
        elif final_score >= 70.0:
            job_fit = "Strong Alignment"
        elif final_score >= 50.0:
            job_fit = "Moderate Alignment"
        else:
            job_fit = "Needs Alignment & Development"

        # Strengths & Weaknesses derived deterministically from evidence
        strengths = []
        weaknesses = []

        if skills_res.get("matched_skills"):
            strengths.append(f"Demonstrated proficiency in {len(skills_res['matched_skills'])} key job skills, including {', '.join(skills_res['matched_skills'][:3])}.")
        if exp_res.get("experience_score", 0) >= 80.0:
            strengths.append(f"Relevant professional experience ({exp_res.get('candidate_relevant_years', 0)} years) satisfies target requirement ({exp_res.get('required_experience_years', 0)} years).")
        if edu_res.get("education_score", 0) >= 80.0:
            strengths.append(f"Formal education credentials meet role requirements ({edu_res.get('candidate_degree', 'Degree')}).")
        if kw_res.get("keyword_score", 0) >= 70.0:
            strengths.append(f"High technical vocabulary and keyword alignment with the job description ({kw_res.get('keyword_score')}%).")
        if semantic_sim >= 70.0:
            strengths.append(f"Strong overall semantic similarity ({semantic_sim}%) between resume and job description.")

        if not strengths:
            strengths.append("Foundational technical background documented in resume.")

        if skills_res.get("missing_skills"):
            weaknesses.append(f"Missing priority skills identified in job requirements: {', '.join(skills_res['missing_skills'][:4])}.")
        if exp_res.get("experience_score", 0) < 60.0:
            weaknesses.append(f"Experience gap: {exp_res.get('gap_summary', 'Experience below requirement.')}")
        if resp_res.get("missing_count", 0) > 0:
            weaknesses.append(f"{resp_res.get('missing_count')} job responsibilities lack direct evidence in work history or projects.")
        if fmt_res.get("formatting_improvements"):
            weaknesses.append(fmt_res["formatting_improvements"][0])

        if not weaknesses:
            weaknesses.append("Profile strongly matches role requirements with minimal detectable gaps.")

        # 2. Downstream Recommendation Layer (never alters final_score)
        target_role = job_parsed.get("job_info", {}).get("title", "Target Role")
        recommendation_context = {
            "target_role": target_role,
            "matched_skills": skills_res.get("matched_skills", []),
            "missing_skills": skills_res.get("missing_skills", []),
            "skill_score": score_breakdown.get("skill_score", 0.0),
            "experience_score": score_breakdown.get("experience_score", 0.0),
            "gap_summary": exp_res.get("gap_summary", ""),
            "formatting_improvements": fmt_res.get("formatting_improvements", []),
            "weaknesses": weaknesses
        }

        try:
            rec_result = await RecommendationService.get_recommendations(recommendation_context)
        except Exception as e:
            logger.warning(f"Recommendation generation encountered exception: {e}, using rule-based fallback")
            rec_result = RecommendationService.generate_rule_based_recommendations(recommendation_context)
            rec_result["source"] = "rule_based"
            rec_result["provider"] = "none"
            rec_result["is_ai_generated"] = False

        # Format comparison table for auditability (recording component weights and scores)
        scoring_weights = [
            ("Skills Match", 0.25, score_breakdown.get("skill_score", 0.0)),
            ("Experience Match", 0.20, score_breakdown.get("experience_score", 0.0)),
            ("Responsibilities", 0.20, score_breakdown.get("responsibility_score", 0.0)),
            ("Keyword Coverage", 0.10, score_breakdown.get("keyword_score", 0.0)),
            ("Semantic Similarity", 0.10, score_breakdown.get("semantic_score", 0.0)),
            ("Education Verification", 0.05, score_breakdown.get("education_score", 0.0)),
            ("Project Alignment", 0.05, score_breakdown.get("project_score", 0.0)),
            ("Formatting & ATS Readability", 0.05, score_breakdown.get("formatting_score", 0.0)),
        ]

        comparison_table = [
            {
                "parameter": name,
                "weight": f"{int(weight * 100)}%",
                "score": score,
                "weighted_contribution": round(score * weight, 2)
            }
            for name, weight, score in scoring_weights
        ]

        return {
            "overall_score": final_score,
            "job_fit": job_fit,
            "confidence": 92.0,
            "scoring_formula": "Skills (25%) + Experience (20%) + Responsibilities (20%) + Keywords (10%) + Semantic (10%) + Education (5%) + Projects (5%) + Formatting (5%)",
            "score_breakdown": score_breakdown,
            "skill_analysis": skills_res,
            "project_analysis": proj_res,
            "experience_analysis": exp_res,
            "education_analysis": edu_res,
            "keyword_analysis": kw_res,
            "responsibility_analysis": resp_res,
            "formatting_analysis": fmt_res,
            "semantic_similarity": semantic_sim,
            "strengths": strengths[:4],
            "weaknesses": weaknesses[:4],
            "recommendations": rec_result,
            "learning_roadmap": rec_result.get("learning_direction", []),
            "resume_improvements": rec_result.get("resume_improvements", []),
            "comparison_table": comparison_table,
            "models": {
                "deterministic": deterministic_data
            },
            "consensus": {
                "overall_score": final_score,
                "job_fit": job_fit,
                "confidence": 92.0,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "learning_roadmap": rec_result.get("learning_direction", []),
                "resume_improvements": rec_result.get("resume_improvements", []),
                "project_suggestions": rec_result.get("project_suggestions", [])
            }
        }
