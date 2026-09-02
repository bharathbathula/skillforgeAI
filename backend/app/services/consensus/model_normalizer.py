from typing import Dict, Any, List
from app.services.nlp.technical_tokenizer import TechnicalTokenizer

class ModelNormalizer:
    """
    Normalizes parameter scores, skill names, and comparison tables across
    Gemini, OpenAI, Claude, and Deterministic baseline models.
    """

    PARAMETER_LABELS = {
        "overall_score": "Overall ATS Score",
        "skill_score": "Skills Match",
        "experience_score": "Relevant Experience",
        "responsibility_score": "Responsibilities Match",
        "keyword_score": "Required Keywords",
        "technical_skills": "Technical Skills",
        "soft_skills": "Soft Skills & Leadership",
        "education_score": "Education & Degree",
        "semantic_score": "Semantic Alignment",
        "job_fit": "Job Fit Assessment",
        "confidence": "Evaluation Confidence"
    }

    @classmethod
    def normalize_model_output(cls, raw_model_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes parameter scores and lists for a single AI model."""
        params = raw_model_dict.get("parameter_scores", {})
        
        normalized_params = {
            "overall_score": float(raw_model_dict.get("overall_score", params.get("overall_score", 50.0))),
            "skill_score": float(params.get("skill_score", params.get("skills", 50.0))),
            "experience_score": float(params.get("experience_score", params.get("experience", 50.0))),
            "responsibility_score": float(params.get("responsibility_score", params.get("responsibilities", 50.0))),
            "keyword_score": float(params.get("keyword_score", params.get("keywords", 50.0))),
            "technical_skills": float(params.get("technical_skills", params.get("skill_score", 50.0))),
            "soft_skills": float(params.get("soft_skills", 70.0)),
            "education_score": float(params.get("education_score", params.get("education", 75.0))),
            "semantic_score": float(params.get("semantic_score", params.get("semantic_match", 50.0)))
        }

        # Normalize skill lists
        norm_matched = list(set([TechnicalTokenizer.normalize_skill(s) for s in raw_model_dict.get("matched_skills", [])]))
        norm_missing = list(set([TechnicalTokenizer.normalize_skill(s) for s in raw_model_dict.get("missing_skills", [])]))

        return {
            "provider_name": raw_model_dict.get("provider_name", "AI Model"),
            "model_id": raw_model_dict.get("model_id", "ai-model"),
            "status": raw_model_dict.get("status", "success"),
            "overall_score": round(normalized_params["overall_score"], 1),
            "job_fit": raw_model_dict.get("job_fit", "Moderate"),
            "confidence": float(raw_model_dict.get("confidence", 85.0)),
            "parameter_scores": normalized_params,
            "matched_skills": raw_model_dict.get("matched_skills", []),
            "missing_skills": raw_model_dict.get("missing_skills", []),
            "partial_skills": raw_model_dict.get("partial_skills", []),
            "matched_responsibilities": raw_model_dict.get("matched_responsibilities", []),
            "missing_responsibilities": raw_model_dict.get("missing_responsibilities", []),
            "strengths": raw_model_dict.get("strengths", []),
            "weaknesses": raw_model_dict.get("weaknesses", []),
            "recommendations": raw_model_dict.get("recommendations", []),
            "learning_requirements": raw_model_dict.get("learning_requirements", []),
            "resume_improvements": raw_model_dict.get("resume_improvements", []),
            "evidence_summary": raw_model_dict.get("evidence_summary", [])
        }

    @classmethod
    def build_comparison_matrix(
        cls,
        gemini: Dict[str, Any],
        openai: Dict[str, Any],
        claude: Dict[str, Any],
        consensus: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Builds a multi-column comparison table containing all parameters across models.
        """
        rows = []
        param_keys = [
            "overall_score",
            "skill_score",
            "experience_score",
            "responsibility_score",
            "keyword_score",
            "technical_skills",
            "soft_skills",
            "education_score",
            "semantic_score"
        ]

        for pk in param_keys:
            label = cls.PARAMETER_LABELS.get(pk, pk.replace("_", " ").title())
            g_val = gemini.get("parameter_scores", {}).get(pk, gemini.get("overall_score") if pk == "overall_score" else "N/A")
            o_val = openai.get("parameter_scores", {}).get(pk, openai.get("overall_score") if pk == "overall_score" else "N/A")
            c_val = claude.get("parameter_scores", {}).get(pk, claude.get("overall_score") if pk == "overall_score" else "N/A")
            cons_val = consensus.get("parameter_scores", {}).get(pk, consensus.get("overall_score") if pk == "overall_score" else "N/A")

            rows.append({
                "parameter_key": pk,
                "label": label,
                "gemini": g_val,
                "openai": o_val,
                "claude": c_val,
                "consensus": cons_val
            })

        # Add Job Fit & Confidence rows
        rows.append({
            "parameter_key": "job_fit",
            "label": "Job Fit Assessment",
            "gemini": gemini.get("job_fit", "N/A"),
            "openai": openai.get("job_fit", "N/A"),
            "claude": claude.get("job_fit", "N/A"),
            "consensus": consensus.get("job_fit", "N/A")
        })

        rows.append({
            "parameter_key": "confidence",
            "label": "Evaluation Confidence",
            "gemini": f"{gemini.get('confidence', 85)}%",
            "openai": f"{openai.get('confidence', 85)}%",
            "claude": f"{claude.get('confidence', 85)}%",
            "consensus": f"{consensus.get('confidence', 90)}%"
        })

        return rows
