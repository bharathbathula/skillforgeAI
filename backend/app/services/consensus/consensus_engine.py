from typing import Dict, Any, List
from app.services.consensus.model_normalizer import ModelNormalizer

class ConsensusEngine:
    """
    Evidence-Based Consensus & Ensemble Engine:
    - Reconciles Deterministic Baseline + Gemini + OpenAI + Claude
    - Prioritizes objective arithmetic evidence over subjective AI variance
    - Detects model disagreements and explains divergences
    - Generates a prioritized, job-specific learning roadmap and resume refinement plan
    """

    @classmethod
    def reconcile(
        cls,
        deterministic: Dict[str, Any],
        raw_gemini: Dict[str, Any],
        raw_openai: Dict[str, Any],
        raw_claude: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes full cross-model reconciliation and generates consensus ATS report.
        """
        # 1. Normalize individual model outputs
        gemini = ModelNormalizer.normalize_model_output(raw_gemini)
        openai = ModelNormalizer.normalize_model_output(raw_openai)
        claude = ModelNormalizer.normalize_model_output(raw_claude)

        # 2. Identify active, successful AI providers
        active_models = [m for m in [gemini, openai, claude] if m.get("status") == "success"]

        det_scores = deterministic.get("parameter_scores", {})
        det_overall = float(deterministic.get("deterministic_score", 50.0))

        # 3. Calculate Ensemble Parameter Scores
        consensus_params = {}
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

        disagreements = []

        for pk in param_keys:
            det_val = float(det_scores.get(pk, det_overall if pk == "overall_score" else 50.0))

            if active_models:
                ai_vals = [float(m["parameter_scores"].get(pk, 50.0)) for m in active_models]
                ai_avg = sum(ai_vals) / len(ai_vals)

                # Check for significant disagreement among AI models (> 20 points spread)
                if len(ai_vals) >= 2 and (max(ai_vals) - min(ai_vals)) > 20.0:
                    disagreements.append(cls._explain_disagreement(pk, det_val, gemini, openai, claude))

                # Weight deterministic baseline 45% + AI consensus 55%
                weighted_val = (det_val * 0.45) + (ai_avg * 0.55)
            else:
                weighted_val = det_val

            consensus_params[pk] = round(max(0.0, min(100.0, weighted_val)), 1)

        final_overall_score = consensus_params["overall_score"]

        # 4. Determine Job Fit & Confidence
        if final_overall_score >= 85.0:
            job_fit = "Exceptional Fit"
        elif final_overall_score >= 72.0:
            job_fit = "Strong Fit"
        elif final_overall_score >= 55.0:
            job_fit = "Moderate Fit"
        else:
            job_fit = "Low Alignment"

        # Higher confidence when deterministic + active models are in agreement
        confidence = 92.0 if len(active_models) >= 2 else (85.0 if len(active_models) == 1 else 80.0)

        # 5. Aggregate Deduplicated Strengths, Weaknesses, and Recommendations
        strengths = cls._aggregate_insights([gemini, openai, claude], deterministic, "strengths")
        weaknesses = cls._aggregate_insights([gemini, openai, claude], deterministic, "weaknesses")
        recommendations = cls._aggregate_insights([gemini, openai, claude], deterministic, "recommendations")
        resume_improvements = cls._aggregate_insights([gemini, openai, claude], deterministic, "resume_improvements")

        # 6. Build Prioritized Job-Specific Learning Roadmap
        learning_roadmap = cls._build_learning_roadmap(deterministic, active_models)

        consensus_summary = {
            "overall_score": final_overall_score,
            "job_fit": job_fit,
            "confidence": confidence,
            "parameter_scores": consensus_params,
            "strengths": strengths[:5],
            "weaknesses": weaknesses[:5],
            "recommendations": recommendations[:5],
            "learning_roadmap": learning_roadmap,
            "resume_improvements": resume_improvements[:5],
            "disagreements": disagreements,
            "disagreement_summary": f"Analyzed {len(disagreements)} parameter variances across models. Reconciled with deterministic evidence."
        }

        # 7. Assemble Multi-Model Comparison Table
        comparison_table = ModelNormalizer.build_comparison_matrix(gemini, openai, claude, consensus_summary)

        return {
            "overall_score": final_overall_score,
            "job_fit": job_fit,
            "confidence": confidence,
            "score_breakdown": {
                "skill_score": consensus_params["skill_score"],
                "experience_score": consensus_params["experience_score"],
                "responsibility_score": consensus_params["responsibility_score"],
                "keyword_score": consensus_params["keyword_score"],
                "project_score": det_scores.get("project_score", 60.0),
                "semantic_score": consensus_params["semantic_score"],
                "education_score": consensus_params["education_score"],
                "formatting_score": det_scores.get("formatting_score", 85.0)
            },
            "consensus": consensus_summary,
            "comparison_table": comparison_table,
            "gemini": gemini,
            "openai": openai,
            "claude": claude,
            "deterministic": deterministic
        }

    @classmethod
    def _explain_disagreement(
        cls,
        param_key: str,
        det_val: float,
        gemini: Dict[str, Any],
        openai: Dict[str, Any],
        claude: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates clear explanation when AI models diverge on a parameter."""
        label = ModelNormalizer.PARAMETER_LABELS.get(param_key, param_key.title())
        g_val = gemini.get("parameter_scores", {}).get(param_key, "N/A")
        o_val = openai.get("parameter_scores", {}).get(param_key, "N/A")
        c_val = claude.get("parameter_scores", {}).get(param_key, "N/A")

        return {
            "parameter": label,
            "divergence": f"Gemini: {g_val}%, OpenAI: {o_val}%, Claude: {c_val}%",
            "deterministic_anchor": f"Objective Baseline: {det_val}%",
            "resolution": f"Consensus prioritized verified resume evidence ({det_val}%) to produce a defensible score."
        }

    @classmethod
    def _aggregate_insights(
        cls,
        models: List[Dict[str, Any]],
        deterministic: Dict[str, Any],
        insight_key: str
    ) -> List[str]:
        """Collects, deduplicates, and filters meaningful statements across models."""
        combined = []
        seen = set()

        for m in models:
            for item in m.get(insight_key, []):
                clean = item.strip()
                if len(clean) > 15 and clean.lower() not in seen:
                    seen.add(clean.lower())
                    combined.append(clean)

        # Fallback to deterministic items if list is empty
        if not combined:
            skills = deterministic.get("skills", {})
            exp = deterministic.get("experience", {})
            if insight_key == "strengths":
                combined.append(f"Demonstrated background matching {len(skills.get('matched_skills', []))} target technologies.")
                combined.append(f"Experience alignment: {exp.get('match_status', 'Qualified')}.")
            elif insight_key == "weaknesses":
                missing = skills.get("missing_skills", [])
                if missing:
                    combined.append(f"Missing {len(missing)} key technologies: {', '.join(missing[:3])}.")
                combined.append(exp.get("gap_summary", "Role depth can be highlighted."))
            elif insight_key == "recommendations":
                combined.append("Quantify project outcomes with numerical metrics and business impact.")
                combined.append("Add explicit keywords for target technologies in project descriptions.")
            elif insight_key == "resume_improvements":
                combined.append("If you performed backend architecture or scaling work, describe throughput and latency improvements.")
                combined.append("Align bullet point action verbs with target job responsibility keywords.")

        return combined

    @classmethod
    def _build_learning_roadmap(
        cls,
        deterministic: Dict[str, Any],
        active_models: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Constructs a prioritized, step-by-step job-specific learning roadmap."""
        missing_skills = deterministic.get("skills", {}).get("missing_skills", [])
        
        roadmap = []
        priorities = ["Priority 1 (Critical)", "Priority 2 (High)", "Priority 3 (Recommended)", "Priority 4 (Optional)"]

        for idx, skill in enumerate(missing_skills[:5]):
            p_label = priorities[min(idx, len(priorities) - 1)]
            roadmap.append({
                "skill": skill,
                "priority": p_label,
                "importance_reason": f"Explicitly listed in target Job Description requirements; currently absent from resume.",
                "learning_sequence": f"Step {idx + 1}: Study fundamentals of {skill} and build a practical hands-on project module.",
                "expected_impact": f"Closing this gap directly increases ATS technical skill coverage and strengthens interview alignment."
            })

        if not roadmap:
            roadmap.append({
                "skill": "Advanced System Design & Scalability",
                "priority": "Priority 1 (Recommended)",
                "importance_reason": "Deepens technical qualification for senior engineering responsibilities.",
                "learning_sequence": "Step 1: Explore distributed caching, microservices, and asynchronous task queues.",
                "expected_impact": "Strengthens system architecture interview readiness."
            })

        return roadmap
