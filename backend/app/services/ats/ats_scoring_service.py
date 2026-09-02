import asyncio
import logging
from typing import Dict, Any, List
from app.services.deterministic.deterministic_scorer import DeterministicScorer
from app.services.ai.multi_model_orchestrator import MultiModelOrchestrator
from app.services.consensus.consensus_engine import ConsensusEngine

logger = logging.getLogger(__name__)

class ATSScoringService:
    """
    Unified ATS Scoring Orchestrator:
    - Runs full Deterministic Baseline Evaluation (arithmetic, date calculations, keyword matches)
    - Runs concurrent Multi-Model AI Evaluation (Gemini, OpenAI, Claude)
    - Runs Consensus & Ensemble Engine to generate defensible, grounded final assessment
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
        Synchronous wrapper executing deterministic and AI consensus pipeline.
        """
        try:
            return asyncio.run(
                cls.compute_full_ats_report_async(
                    resume_parsed, job_parsed, raw_resume, raw_job, resume_sections, job_sections
                )
            )
        except RuntimeError:
            # asyncio.run() fails when called inside a running event loop (e.g. FastAPI async route)
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
        except Exception as e:
            # Final safety fallback — run deterministic scoring only without AI models
            logger.error(f"ATSScoringService complete failure, falling back to deterministic only: {e}")
            from app.services.deterministic.deterministic_scorer import DeterministicScorer
            det = DeterministicScorer.run_full_deterministic_analysis(
                resume_parsed, job_parsed, raw_resume, raw_job, resume_sections, job_sections
            )
            det_score = det.get("deterministic_score", 0.0)
            return {
                "overall_score": det_score,
                "job_fit": "Unable to Fully Assess",
                "confidence": 60,
                "score_breakdown": det.get("parameter_scores", {}),
                "skill_analysis": det.get("skills", {}),
                "project_analysis": det.get("projects", {}),
                "experience_analysis": det.get("experience", {}),
                "education_analysis": det.get("education", {}),
                "keyword_analysis": det.get("keywords", {}),
                "responsibility_analysis": det.get("responsibilities", {}),
                "formatting_analysis": det.get("formatting", {}),
                "strengths": [], "weaknesses": [],
                "recommendations": ["Multi-model AI analysis unavailable. Deterministic score shown."],
                "learning_roadmap": [],
                "resume_improvements": [],
                "disagreements": [],
                "disagreement_summary": "",
                "comparison_table": [],
                "models": {"deterministic": det},
                "consensus": {}
            }


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
        Executes end-to-end deterministic + multi-model AI + consensus pipeline.
        """
        if not isinstance(resume_parsed, dict):
            resume_parsed = {}
        if not isinstance(job_parsed, dict):
            job_parsed = {}

        # 1. Run full deterministic evaluation (grounded arithmetic anchor)
        deterministic_data = DeterministicScorer.run_full_deterministic_analysis(
            parsed_resume=resume_parsed,
            parsed_job=job_parsed,
            raw_resume=raw_resume,
            raw_jd=raw_job,
            resume_sections=resume_sections,
            job_sections=job_sections
        )

        # 2. Run parallel Multi-Model AI analysis (Gemini, OpenAI, Claude)
        multi_ai_results = await MultiModelOrchestrator.run_multi_model_evaluation(
            raw_resume=raw_resume,
            raw_jd=raw_job,
            parsed_resume=resume_parsed,
            parsed_job=job_parsed,
            deterministic_data=deterministic_data
        )

        # 3. Run Consensus Engine to reconcile scores & detect disagreements
        consensus_report = ConsensusEngine.reconcile(
            deterministic=deterministic_data,
            raw_gemini=multi_ai_results.get("gemini", {}),
            raw_openai=multi_ai_results.get("openai", {}),
            raw_claude=multi_ai_results.get("claude", {})
        )

        final_score = consensus_report["overall_score"]
        score_breakdown = consensus_report["score_breakdown"]
        consensus_data = consensus_report["consensus"]

        # 4. Extract structured analyses for UI backward-compatibility and deep inspection
        skills_res = deterministic_data["skills"]
        proj_res = deterministic_data["projects"]
        exp_res = deterministic_data["experience"]
        edu_res = deterministic_data["education"]
        kw_res = deterministic_data["keywords"]
        resp_res = deterministic_data["responsibilities"]
        fmt_res = deterministic_data["formatting"]

        return {
            "overall_score": final_score,
            "job_fit": consensus_report["job_fit"],
            "confidence": consensus_report["confidence"],
            "score_breakdown": score_breakdown,
            "skill_analysis": skills_res,
            "project_analysis": proj_res,
            "experience_analysis": exp_res,
            "education_analysis": edu_res,
            "keyword_analysis": kw_res,
            "responsibility_analysis": resp_res,
            "formatting_analysis": fmt_res,
            "strengths": consensus_data.get("strengths", []),
            "weaknesses": consensus_data.get("weaknesses", []),
            "recommendations": consensus_data.get("recommendations", []),
            "learning_roadmap": consensus_data.get("learning_roadmap", []),
            "resume_improvements": consensus_data.get("resume_improvements", []),
            "disagreements": consensus_data.get("disagreements", []),
            "disagreement_summary": consensus_data.get("disagreement_summary", ""),
            "comparison_table": consensus_report["comparison_table"],
            "models": {
                "gemini": consensus_report["gemini"],
                "openai": consensus_report["openai"],
                "claude": consensus_report["claude"],
                "deterministic": deterministic_data
            },
            "consensus": consensus_data
        }
