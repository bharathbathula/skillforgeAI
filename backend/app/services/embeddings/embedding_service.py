import importlib
import math
import re
from collections import Counter
from typing import Dict, Any, List, Optional

class EmbeddingService:
    """
    Pretrained Bi-Encoder Embedding Service (all-MiniLM-L6-v2)
    with cached singleton instance and deterministic TF-IDF cosine similarity fallback.
    """

    @staticmethod
    def chunk_resume(parsed_resume: Dict[str, Any], raw_text: str) -> Dict[str, str]:
        """
        Split resume into structured logical sections:
        Summary, Skills, Experience, Projects, Education, Certifications.
        """
        if not isinstance(parsed_resume, dict):
            parsed_resume = {}

        sections = {}

        # Summary section
        sections["summary"] = parsed_resume.get("summary", "")

        # Skills section
        skills_data = parsed_resume.get("skills", {})
        if isinstance(skills_data, dict):
            all_skills = []
            for val in skills_data.values():
                if isinstance(val, list):
                    all_skills.extend([str(v) for v in val])
            sections["skills"] = ", ".join(all_skills)
        elif isinstance(skills_data, list):
            sections["skills"] = ", ".join(skills_data)
        else:
            sections["skills"] = str(skills_data)

        # Experience section
        exp_list = parsed_resume.get("experience", [])
        if not isinstance(exp_list, list):
            exp_list = []
        exp_texts = []
        for item in exp_list:
            if isinstance(item, dict):
                company = item.get("company", "")
                role = item.get("role", "")
                resps = " ".join(item.get("responsibilities", [])) if isinstance(item.get("responsibilities"), list) else str(item.get("responsibilities", ""))
                techs = " ".join(item.get("technologies", [])) if isinstance(item.get("technologies"), list) else str(item.get("technologies", ""))
                exp_texts.append(f"{role} at {company}. {resps} {techs}")
        sections["experience"] = " ".join(exp_texts)

        # Projects section
        proj_list = parsed_resume.get("projects", [])
        if not isinstance(proj_list, list):
            proj_list = []
        proj_texts = []
        for proj in proj_list:
            if isinstance(proj, dict):
                pname = proj.get("name", "")
                pdesc = proj.get("description", "")
                presps = " ".join(proj.get("responsibilities", [])) if isinstance(proj.get("responsibilities"), list) else str(proj.get("responsibilities", ""))
                ptechs = " ".join(proj.get("technologies", [])) if isinstance(proj.get("technologies"), list) else str(proj.get("technologies", ""))
                proj_texts.append(f"Project {pname}: {pdesc} {presps} {ptechs}")
        sections["projects"] = " ".join(proj_texts)

        # Education section
        edu_list = parsed_resume.get("education", [])
        if not isinstance(edu_list, list):
            edu_list = []
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
        if not isinstance(parsed_job, dict):
            parsed_job = {}

        sections = {}

        # Responsibilities
        resps = parsed_job.get("responsibilities", [])
        sections["responsibilities"] = " ".join(resps) if isinstance(resps, list) else str(resps)

        # Skills
        skills_data = parsed_job.get("skills", {})
        if not isinstance(skills_data, dict):
            skills_data = {}
        req_skills = skills_data.get("required_skills", [])
        pref_skills = skills_data.get("preferred_skills", [])
        sections["required_skills"] = ", ".join(req_skills) if isinstance(req_skills, list) else str(req_skills)
        sections["preferred_skills"] = ", ".join(pref_skills) if isinstance(pref_skills, list) else str(pref_skills)

        # Qualifications
        quals = parsed_job.get("qualifications", [])
        sections["qualifications"] = " ".join(quals) if isinstance(quals, list) else str(quals)

        # Overall Summary
        job_info = parsed_job.get("job_info", {})
        if not isinstance(job_info, dict):
            job_info = {}
        title = job_info.get("title", "")
        exp_req = job_info.get("experience_required", "")
        sections["summary"] = f"{title} position requiring {exp_req}. {raw_text[:500]}"

        return sections

    _model_instance: Any = None
    _model_attempted: bool = False

    @classmethod
    def _get_sentence_transformer(cls) -> Any:
        """
        Returns cached singleton instance of all-MiniLM-L6-v2 sentence-transformer embedding model.
        Uses dynamic import to avoid static unresolved import errors when sentence-transformers
        is not pre-installed in the virtual environment.
        """
        if cls._model_attempted:
            return cls._model_instance

        cls._model_attempted = True
        try:
            st_mod = importlib.import_module("sentence_transformers")
            st_cls = getattr(st_mod, "SentenceTransformer", None)
            if st_cls is not None:
                cls._model_instance = st_cls("all-MiniLM-L6-v2")
        except Exception:
            # sentence_transformers not installed, torch missing, or offline environment
            cls._model_instance = None

        return cls._model_instance

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        """
        Generate embedding vector for a single text block.
        Returns a float vector from all-MiniLM-L6-v2, or a deterministic hash-based normalized vector.
        """
        if not text or not text.strip():
            return []

        model = cls._get_sentence_transformer()
        if model is not None:
            try:
                emb = model.encode(text.strip())
                if hasattr(emb, "tolist"):
                    return [float(x) for x in emb.tolist()]
                return [float(x) for x in emb]
            except Exception:
                pass

        # Deterministic lightweight fallback vector
        words = re.findall(r'\b[a-zA-Z0-9_+#.-]+\b', text.lower())
        if not words:
            return []
        counts = Counter(words)
        total = float(len(words))
        return [round(count / total, 5) for _, count in counts.most_common(20)]

    @classmethod
    def compute_similarity(cls, text1: Optional[str], text2: Optional[str]) -> float:
        """
        Compute cosine similarity score (0.0 to 1.0) between two text blocks.
        Uses cached all-MiniLM-L6-v2 sentence-transformer embedding model when available,
        with robust deterministic TF-IDF cosine similarity fallback.
        """
        if not text1 or not text2:
            return 0.0

        t1_clean = text1.strip()
        t2_clean = text2.strip()
        if not t1_clean or not t2_clean:
            return 0.0

        # Exact match optimization
        if t1_clean.lower() == t2_clean.lower():
            return 1.0

        # 1. Try cached sentence-transformers embedding model
        model = cls._get_sentence_transformer()
        if model is not None:
            try:
                st_mod = importlib.import_module("sentence_transformers")
                util = getattr(st_mod, "util", None)
                emb1 = model.encode(t1_clean, convert_to_tensor=True)
                emb2 = model.encode(t2_clean, convert_to_tensor=True)
                if util is not None:
                    sim = util.cos_sim(emb1, emb2).item()
                    return max(0.0, min(1.0, float(sim)))
            except Exception:
                pass

        # 2. Deterministic TF-IDF Cosine Fallback
        return cls._tf_idf_cosine(t1_clean, t2_clean)

    @classmethod
    def compute_similarity_percent(cls, text1: Optional[str], text2: Optional[str]) -> float:
        """
        Normalized 0-100 percentage representation of cosine similarity for reporting.
        """
        raw = cls.compute_similarity(text1, text2)
        return round(raw * 100.0, 1)

    @staticmethod
    def _tf_idf_cosine(text1: str, text2: str) -> float:
        """
        Deterministic TF-IDF style cosine similarity between two text strings.
        Efficient O(N) term frequency computation using Counter.
        """
        words1 = re.findall(r'\b[a-zA-Z0-9_+#.-]+\b', text1.lower())
        words2 = re.findall(r'\b[a-zA-Z0-9_+#.-]+\b', text2.lower())

        if not words1 or not words2:
            return 0.0

        len1 = len(words1)
        len2 = len(words2)

        c1 = Counter(words1)
        c2 = Counter(words2)

        tf1 = {w: count / len1 for w, count in c1.items()}
        tf2 = {w: count / len2 for w, count in c2.items()}

        # Dot product over shared vocabulary
        shared = set(tf1.keys()).intersection(tf2.keys())
        if not shared:
            return 0.0

        dot_product = sum(tf1[w] * tf2[w] for w in shared)
        magnitude1 = math.sqrt(sum(v ** 2 for v in tf1.values()))
        magnitude2 = math.sqrt(sum(v ** 2 for v in tf2.values()))

        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0

        similarity = dot_product / (magnitude1 * magnitude2)
        return max(0.0, min(1.0, similarity))
