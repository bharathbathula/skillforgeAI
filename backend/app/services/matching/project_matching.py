from typing import Dict, Any, List
from app.services.embeddings.embedding_service import EmbeddingService
from app.services.nlp.technical_tokenizer import TechnicalTokenizer

class ProjectMatchingService:
    @staticmethod
    def analyze_projects(candidate_projects: List[Any], job_parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare each candidate project against job description responsibilities & skills.
        Calculates grounded project relevance based on actual technology overlap and semantic similarity.
        """
        if not candidate_projects:
            return {
                "project_score": 0.0,
                "project_evaluations": []
            }

        job_resps = job_parsed.get("responsibilities", [])
        if isinstance(job_resps, list):
            job_resps_text = " ".join(job_resps)
        else:
            job_resps_text = str(job_resps)

        skills_dict = job_parsed.get("skills", {})
        if isinstance(skills_dict, dict):
            req_skills = skills_dict.get("required_skills", [])
            pref_skills = skills_dict.get("preferred_skills", [])
            job_skills = list(req_skills) + list(pref_skills)
        elif isinstance(skills_dict, list):
            job_skills = list(skills_dict)
        else:
            job_skills = []

        norm_job_skills = {TechnicalTokenizer.normalize_skill(s): s for s in job_skills}

        project_evals = []
        total_relevance = 0.0

        for proj in candidate_projects:
            if isinstance(proj, str):
                pname = proj
                pdesc = proj
                presps = ""
                ptechs = []
            elif isinstance(proj, dict):
                pname = proj.get("name", "Project")
                pdesc = proj.get("description", "")
                raw_resps = proj.get("responsibilities", [])
                presps = " ".join(raw_resps) if isinstance(raw_resps, list) else str(raw_resps)
                ptechs = proj.get("technologies", [])
                if not isinstance(ptechs, list):
                    ptechs = [str(ptechs)]
            else:
                continue

            proj_text = f"{pname} {pdesc} {presps} {' '.join(ptechs)}".strip()
            if not proj_text:
                continue

            # Semantic similarity to job requirements
            sim = EmbeddingService.compute_similarity(proj_text, job_resps_text) if job_resps_text else 0.5

            # Detect genuine project technologies matching JD skills
            matched_techs = []
            proj_tokens = [t.lower() for t in TechnicalTokenizer.tokenize_preserve_tech(proj_text)]
            proj_tokens_set = set(proj_tokens)

            for norm_js, orig_js in norm_job_skills.items():
                if norm_js in proj_tokens_set or orig_js.lower() in proj_tokens_set:
                    matched_techs.append(orig_js)
                elif any(TechnicalTokenizer.normalize_skill(t) == norm_js for t in ptechs):
                    matched_techs.append(orig_js)

            matched_techs = sorted(list(set(matched_techs)))
            missing_techs = [orig_js for norm_js, orig_js in norm_job_skills.items() if orig_js not in matched_techs][:4]

            # Grounded relevance calculation
            tech_match_ratio = (len(matched_techs) / len(job_skills)) if job_skills else 0.5
            relevance = (sim * 0.5 + tech_match_ratio * 0.5) * 100.0
            relevance = round(max(0.0, min(100.0, relevance)), 1)
            total_relevance += relevance

            # Check matching responsibilities
            matched_responsibilities = []
            if isinstance(job_resps, list):
                for jr in job_resps[:4]:
                    resp_sim = EmbeddingService.compute_similarity(proj_text, jr)
                    if resp_sim >= 0.55:
                        matched_responsibilities.append(jr[:90])

            project_evals.append({
                "name": pname,
                "relevance_percentage": relevance,
                "matched_technologies": matched_techs,
                "matched_responsibilities": matched_responsibilities,
                "missing_technologies": missing_techs
            })

        avg_score = round(total_relevance / len(project_evals), 1) if project_evals else 0.0

        return {
            "project_score": avg_score,
            "project_evaluations": project_evals
        }
