import math
import re
from typing import Dict, Any, List, Tuple

class EmbeddingService:
    @staticmethod
    def chunk_resume(parsed_resume: Dict[str, Any], raw_text: str) -> Dict[str, str]:
        """
        Split resume into structured logical sections:
        Summary, Skills, Experience, Projects, Education, Certifications.
        """
        sections = {}

        # Summary section
        sections["summary"] = parsed_resume.get("summary", "")

        # Skills section
        skills_data = parsed_resume.get("skills", {})
        if isinstance(skills_data, dict):
            all_skills = []
            for k, val in skills_data.items():
                if isinstance(val, list):
                    all_skills.extend([str(v) for v in val])
            sections["skills"] = ", ".join(all_skills)
        elif isinstance(skills_data, list):
            sections["skills"] = ", ".join(skills_data)
        else:
            sections["skills"] = str(skills_data)

        # Experience section
        exp_list = parsed_resume.get("experience", [])
        exp_texts = []
        for item in exp_list:
            if isinstance(item, dict):
                company = item.get("company", "")
                role = item.get("role", "")
                resps = " ".join(item.get("responsibilities", []))
                techs = " ".join(item.get("technologies", []))
                exp_texts.append(f"{role} at {company}. {resps} {techs}")
        sections["experience"] = " ".join(exp_texts)

        # Projects section
        proj_list = parsed_resume.get("projects", [])
        proj_texts = []
        for proj in proj_list:
            if isinstance(proj, dict):
                pname = proj.get("name", "")
                pdesc = proj.get("description", "")
                presps = " ".join(proj.get("responsibilities", []))
                ptechs = " ".join(proj.get("technologies", []))
                proj_texts.append(f"Project {pname}: {pdesc} {presps} {ptechs}")
        sections["projects"] = " ".join(proj_texts)

        # Education section
        edu_list = parsed_resume.get("education", [])
        edu_texts = []
        for edu in edu_list:
            if isinstance(edu, dict):
                degree = edu.get("degree", "")
                inst = edu.get("institution", "")
                edu_texts.append(f"{degree} from {inst}")
        sections["education"] = " ".join(edu_texts)

        return sections

    @staticmethod
    def chunk_job(parsed_job: Dict[str, Any], raw_text: str) -> Dict[str, str]:
        """
        Split job description into structured logical sections:
        Responsibilities, Required Skills, Preferred Skills, Qualifications.
        """
        sections = {}

        # Responsibilities
        resps = parsed_job.get("responsibilities", [])
        sections["responsibilities"] = " ".join(resps) if isinstance(resps, list) else str(resps)

        # Skills
        skills_data = parsed_job.get("skills", {})
        req_skills = skills_data.get("required_skills", [])
        pref_skills = skills_data.get("preferred_skills", [])
        sections["required_skills"] = ", ".join(req_skills)
        sections["preferred_skills"] = ", ".join(pref_skills)

        # Qualifications
        quals = parsed_job.get("qualifications", [])
        sections["qualifications"] = " ".join(quals) if isinstance(quals, list) else str(quals)

        # Overall Summary
        job_info = parsed_job.get("job_info", {})
        title = job_info.get("title", "")
        exp_req = job_info.get("experience_required", "")
        sections["summary"] = f"{title} position requiring {exp_req}. {raw_text[:500]}"

        return sections

    @staticmethod
    def compute_similarity(text1: str, text2: str) -> float:
        """
        Compute cosine similarity score (0.0 to 1.0) between two text blocks.
        Uses sentence-transformers if available, else TF-IDF cosine similarity.
        """
        if not text1 or not text2:
            return 0.0

        # Try sentence-transformers if available
        try:
            from sentence_transformers import SentenceTransformer, util
            model = SentenceTransformer("all-MiniLM-L6-v2")
            emb1 = model.encode(text1, convert_to_tensor=True)
            emb2 = model.encode(text2, convert_to_tensor=True)
            sim = util.cos_sim(emb1, emb2).item()
            return max(0.0, min(1.0, float(sim)))
        except Exception:
            pass

        # TF-IDF Cosine Fallback
        return EmbeddingService._tf_idf_cosine(text1, text2)

    @staticmethod
    def _tf_idf_cosine(text1: str, text2: str) -> float:
        words1 = re.findall(r'\b[a-zA-Z0-9_-]+\b', text1.lower())
        words2 = re.findall(r'\b[a-zA-Z0-9_-]+\b', text2.lower())

        if not words1 or not words2:
            return 0.0

        vocab = set(words1 + words2)
        tf1 = {w: words1.count(w) / len(words1) for w in vocab}
        tf2 = {w: words2.count(w) / len(words2) for w in vocab}

        dot_product = sum(tf1[w] * tf2[w] for w in vocab)
        magnitude1 = math.sqrt(sum(tf1[w] ** 2 for w in vocab))
        magnitude2 = math.sqrt(sum(tf2[w] ** 2 for w in vocab))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        similarity = dot_product / (magnitude1 * magnitude2)
        return max(0.0, min(1.0, float(similarity)))
