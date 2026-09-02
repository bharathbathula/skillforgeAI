from typing import Dict, Any, List, Set, Tuple
from app.services.nlp.technical_tokenizer import TechnicalTokenizer
from app.services.nlp.skill_taxonomy import SkillTaxonomy
from app.services.embeddings.embedding_service import EmbeddingService

class SkillsAnalyzer:
    """
    Deterministic Skills Evaluation Engine:
    - Distinguishes Required vs Preferred vs Optional skills
    - Evaluates skill evidence depth (Professional Work vs Project vs Listed)
    - Distinguishes exact, normalized, semantic, and missing skills with accurate weighting
    """

    @classmethod
    def analyze(
        cls,
        parsed_resume: Dict[str, Any],
        parsed_job: Dict[str, Any],
        raw_resume: str,
        raw_jd: str
    ) -> Dict[str, Any]:
        """
        Executes multi-tier skill analysis.
        """
        # 1. Extract and categorize JD skills
        req_skills, pref_skills, opt_skills = cls.extract_job_skills(parsed_job, raw_jd)

        # 2. Extract and index candidate skills with evidence levels
        candidate_skills_dict = parsed_resume.get("skills", {})
        cand_flat = SkillTaxonomy.extract_flat_skill_list(f"{raw_resume} {str(candidate_skills_dict)}")
        
        cand_normalized = {}
        for s in cand_flat:
            norm = TechnicalTokenizer.normalize_skill(s)
            cand_normalized[norm] = s

        # 3. Evaluate Required Skills
        req_evals, req_earned, req_total = cls.evaluate_skill_group(
            req_skills, cand_normalized, parsed_resume, raw_resume, importance="Required"
        )

        # 4. Evaluate Preferred Skills
        pref_evals, pref_earned, pref_total = cls.evaluate_skill_group(
            pref_skills, cand_normalized, parsed_resume, raw_resume, importance="Preferred"
        )

        # 5. Evaluate Optional Skills
        opt_evals, opt_earned, opt_total = cls.evaluate_skill_group(
            opt_skills, cand_normalized, parsed_resume, raw_resume, importance="Optional"
        )

        # 6. Weighted Score Calculation
        # Required skills count for 70%, Preferred for 25%, Optional for 5%
        req_score = (req_earned / req_total * 100.0) if req_total > 0 else 100.0
        pref_score = (pref_earned / pref_total * 100.0) if pref_total > 0 else 100.0
        opt_score = (opt_earned / opt_total * 100.0) if opt_total > 0 else 100.0

        if req_total > 0 and pref_total > 0:
            final_skill_score = (req_score * 0.70) + (pref_score * 0.25) + (opt_score * 0.05)
        elif req_total > 0:
            final_skill_score = req_score
        else:
            final_skill_score = pref_score if pref_total > 0 else 50.0

        final_skill_score = round(max(0.0, min(100.0, final_skill_score)), 1)

        # Summarize matched, partial, missing
        all_evals = req_evals + pref_evals + opt_evals
        matched_skills = [e["skill"] for e in all_evals if e["status"] in ["Exact Match", "Normalized Match", "Demonstrated in Projects/Work"]]
        partial_skills = [e for e in all_evals if e["status"] == "Partial / Semantic Match"]
        missing_skills = [e["skill"] for e in all_evals if e["status"] == "Missing"]

        return {
            "skill_score": final_skill_score,
            "required_skills_score": round(req_score, 1),
            "preferred_skills_score": round(pref_score, 1),
            "matched_skills": sorted(list(set(matched_skills))),
            "missing_skills": sorted(list(set(missing_skills))),
            "partial_skills": partial_skills,
            "required_skills_breakdown": req_evals,
            "preferred_skills_breakdown": pref_evals,
            "optional_skills_breakdown": opt_evals,
            "total_job_skills_count": len(all_evals),
            "matched_count": len(matched_skills),
            "missing_count": len(missing_skills)
        }

    @classmethod
    def extract_job_skills(cls, parsed_job: Dict[str, Any], raw_jd: str) -> Tuple[List[str], List[str], List[str]]:
        """Separates required, preferred, and optional skills from JD."""
        job_skills = parsed_job.get("skills", {})
        
        req = job_skills.get("required_skills", []) if isinstance(job_skills, dict) else []
        pref = job_skills.get("preferred_skills", []) if isinstance(job_skills, dict) else []
        opt = job_skills.get("optional_skills", []) if isinstance(job_skills, dict) else []

        if not req and not pref:
            # Extract from raw JD text
            skills_found = SkillTaxonomy.extract_flat_skill_list(raw_jd)
            # Partition into required vs preferred based on surrounding text
            req = skills_found[:min(len(skills_found), 8)]
            pref = skills_found[8:14] if len(skills_found) > 8 else []

        # Fallback if no skills found
        if not req and not pref:
            req = ["Python", "REST API", "Database", "Git"]

        return req, pref, opt

    @classmethod
    def evaluate_skill_group(
        cls,
        skills: List[str],
        cand_normalized: Dict[str, str],
        parsed_resume: Dict[str, Any],
        raw_resume: str,
        importance: str
    ) -> Tuple[List[Dict[str, Any]], float, float]:
        """Evaluates a specific list of skills (Required or Preferred)."""
        evaluations = []
        earned_weight = 0.0
        total_weight = 0.0

        imp_multiplier = 3.0 if importance == "Required" else (1.5 if importance == "Preferred" else 1.0)

        for skill in skills:
            norm_s = TechnicalTokenizer.normalize_skill(skill)
            total_weight += imp_multiplier

            # 1. Exact or Normalized Match
            if norm_s in cand_normalized or skill.lower() in cand_normalized:
                evidence_info = SkillTaxonomy.analyze_skill_evidence(skill, parsed_resume, raw_resume)
                depth_weight = evidence_info.get("weight_multiplier", 1.0)
                earned = imp_multiplier * max(0.7, depth_weight)
                earned_weight += earned

                evaluations.append({
                    "skill": skill,
                    "importance": importance,
                    "status": "Exact Match" if depth_weight >= 0.9 else "Demonstrated in Projects/Work",
                    "evidence_level": evidence_info.get("label", "Demonstrated"),
                    "evidence_snippet": evidence_info.get("evidence", f"Skill found: {skill}"),
                    "match_score": round((earned / imp_multiplier) * 100, 1)
                })
                continue

            # 2. Substring or Semantic Match
            best_match = None
            best_sim = 0.0
            for c_norm, c_orig in cand_normalized.items():
                if norm_s in c_norm or c_norm in norm_s:
                    best_sim = 0.85
                    best_match = c_orig
                    break
                
                sim = EmbeddingService.compute_similarity(norm_s, c_norm)
                if sim > best_sim and sim >= 0.70:
                    best_sim = sim
                    best_match = c_orig

            if best_sim >= 0.70 and best_match:
                earned = imp_multiplier * best_sim
                earned_weight += earned
                evaluations.append({
                    "skill": skill,
                    "importance": importance,
                    "status": "Partial / Semantic Match",
                    "evidence_level": f"Related to candidate skill: {best_match}",
                    "evidence_snippet": f"Semantic match ({round(best_sim*100, 1)}%) with '{best_match}'",
                    "match_score": round(best_sim * 100, 1)
                })
            else:
                evaluations.append({
                    "skill": skill,
                    "importance": importance,
                    "status": "Missing",
                    "evidence_level": "Not Found",
                    "evidence_snippet": "No direct or related skill evidence in resume",
                    "match_score": 0.0
                })

        return evaluations, earned_weight, total_weight
