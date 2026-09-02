from typing import Dict, Any, List
from app.services.embeddings.embedding_service import EmbeddingService

class SkillMatchingService:
    # Skill normalization dictionary
    NORMALIZATION_MAP = {
        "js": "javascript",
        "reactjs": "react",
        "react.js": "react",
        "node": "node.js",
        "nodejs": "node.js",
        "postgres": "postgresql",
        "py": "python",
        "ts": "typescript",
        "vuejs": "vue",
        "vue.js": "vue",
        "aws": "amazon web services",
        "k8s": "kubernetes",
        "docker": "docker containerization"
    }

    @staticmethod
    def normalize_skill(skill_name: str) -> str:
        s = skill_name.strip().lower()
        return SkillMatchingService.NORMALIZATION_MAP.get(s, s)

    @staticmethod
    def analyze_skills(candidate_skills_dict: Dict[str, Any], job_skills_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Multi-level skill matching:
        Exact Match, Strong Match, Partial Match, Related, Missing.
        """
        # Extract candidate skills
        candidate_skills = []
        if isinstance(candidate_skills_dict, dict):
            for v in candidate_skills_dict.values():
                if isinstance(v, list):
                    candidate_skills.extend([str(x) for x in v])
        elif isinstance(candidate_skills_dict, list):
            candidate_skills = [str(x) for x in candidate_skills_dict]

        candidate_normalized = {SkillMatchingService.normalize_skill(s): s for s in candidate_skills}

        # Extract job skills
        req_skills = job_skills_dict.get("required_skills", [])
        pref_skills = job_skills_dict.get("preferred_skills", [])
        opt_skills = job_skills_dict.get("optional_skills", [])

        all_job_skills = []
        for s in req_skills:
            all_job_skills.append((s, "Required"))
        for s in pref_skills:
            all_job_skills.append((s, "Preferred"))
        for s in opt_skills:
            all_job_skills.append((s, "Optional"))

        if not all_job_skills:
            all_job_skills = [("Python", "Required"), ("REST API", "Required"), ("Database", "Required")]

        skill_matches = []
        matched_skills = []
        partial_skills = []
        missing_skills = []

        total_weight = 0.0
        earned_weight = 0.0

        for skill, importance in all_job_skills:
            norm_skill = SkillMatchingService.normalize_skill(skill)
            imp_weight = 3.0 if importance == "Required" else (2.0 if importance == "Preferred" else 1.0)
            total_weight += imp_weight

            # 1. Exact / Normalized Match
            if norm_skill in candidate_normalized:
                skill_matches.append({
                    "skill": skill,
                    "match_type": "Exact",
                    "similarity_score": 1.0,
                    "importance": importance
                })
                matched_skills.append(skill)
                earned_weight += imp_weight
                continue

            # 2. Substring / Partial Match
            found_partial = False
            for cand_norm, cand_orig in candidate_normalized.items():
                if norm_skill in cand_norm or cand_norm in norm_skill:
                    skill_matches.append({
                        "skill": skill,
                        "match_type": "Strong",
                        "similarity_score": 0.85,
                        "importance": importance,
                        "matched_with": cand_orig
                    })
                    matched_skills.append(skill)
                    earned_weight += imp_weight * 0.85
                    found_partial = True
                    break
                
                # Semantic Vector Match check
                sim = EmbeddingService.compute_similarity(norm_skill, cand_norm)
                if sim >= 0.70:
                    skill_matches.append({
                        "skill": skill,
                        "match_type": "Partial",
                        "similarity_score": round(sim, 2),
                        "importance": importance,
                        "matched_with": cand_orig
                    })
                    partial_skills.append({
                        "skill": skill,
                        "importance": importance,
                        "related_experience": cand_orig,
                        "similarity": round(sim * 100, 1)
                    })
                    earned_weight += imp_weight * sim
                    found_partial = True
                    break

            if not found_partial:
                skill_matches.append({
                    "skill": skill,
                    "match_type": "Missing",
                    "similarity_score": 0.0,
                    "importance": importance
                })
                missing_skills.append({
                    "skill": skill,
                    "importance": importance
                })

        skill_score = (earned_weight / total_weight * 100.0) if total_weight > 0 else 70.0
        skill_score = max(0.0, min(100.0, round(skill_score, 1)))

        return {
            "skill_score": skill_score,
            "skill_matches": skill_matches,
            "matched_skills": sorted(list(set(matched_skills))),
            "partial_skills": partial_skills,
            "missing_skills": missing_skills,
            "total_job_skills_count": len(all_job_skills),
            "matched_count": len(matched_skills)
        }
