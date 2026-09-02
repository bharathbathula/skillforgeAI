import re
from typing import Dict, Any, List
from app.services.nlp.technical_tokenizer import TechnicalTokenizer
from app.services.embeddings.embedding_service import EmbeddingService

class ResponsibilityMatcher:
    """
    Evaluates individual Job Description responsibilities against candidate resume.
    Produces per-responsibility match scores, extracted evidence snippets, and gap analysis.
    """

    @classmethod
    def analyze(
        cls,
        parsed_job: Dict[str, Any],
        parsed_resume: Dict[str, Any],
        raw_resume: str,
        raw_jd: str
    ) -> Dict[str, Any]:
        """
        Breaks JD into individual responsibilities and compares each against resume evidence.
        """
        # 1. Extract discrete responsibilities from JD
        responsibilities = cls.extract_responsibilities(parsed_job, raw_jd)

        # 2. Build candidate evidence pools (experience, projects, summary)
        candidate_blocks = cls.build_candidate_evidence_blocks(parsed_resume, raw_resume)

        # 3. Evaluate each responsibility individually
        evaluations = []
        total_score = 0.0

        for resp in responsibilities:
            eval_item = cls.evaluate_single_responsibility(resp, candidate_blocks)
            evaluations.append(eval_item)
            total_score += eval_item["match_percentage"]

        avg_score = round(total_score / len(evaluations), 1) if evaluations else 0.0

        matched_count = sum(1 for e in evaluations if e["match_percentage"] >= 65.0)
        partial_count = sum(1 for e in evaluations if 35.0 <= e["match_percentage"] < 65.0)
        missing_count = sum(1 for e in evaluations if e["match_percentage"] < 35.0)

        return {
            "responsibility_score": avg_score,
            "total_responsibilities_count": len(evaluations),
            "matched_count": matched_count,
            "partial_count": partial_count,
            "missing_count": missing_count,
            "evaluations": evaluations,
            "explanation": f"Evaluated {len(evaluations)} individual JD responsibilities against resume evidence. {matched_count} strongly matched, {partial_count} partial, {missing_count} missing."
        }

    @classmethod
    def extract_responsibilities(cls, parsed_job: Dict[str, Any], raw_jd: str) -> List[str]:
        """Extract clean individual responsibility statements from parsed JD or raw text."""
        resps = parsed_job.get("responsibilities", [])
        if resps and isinstance(resps, list) and len(resps) >= 2:
            clean_list = [r.strip() for r in resps if len(r.strip()) > 15]
            if clean_list:
                return clean_list[:8]

        # Extract from raw JD lines
        lines = raw_jd.split('\n')
        extracted = []
        in_resp_section = False

        for line in lines:
            l_str = line.strip()
            l_low = l_str.lower()
            if any(k in l_low for k in ["responsibilities", "duties", "what you will do", "role overview", "what you'll do"]):
                in_resp_section = True
                continue

            if in_resp_section:
                if any(k in l_low for k in ["requirements", "qualifications", "skills", "benefits", "about us"]):
                    break
                is_bullet = l_str.startswith("-") or l_str.startswith("•") or l_str.startswith("*")
                clean_l = l_str.lstrip("-•* \t").strip()
                if len(clean_l) > 15:
                    extracted.append(clean_l)

        if extracted:
            return extracted[:8]

        # Fallback to key sentences
        sentences = re.split(r'(?<=[.!?])\s+', raw_jd)
        sens = [s.strip() for s in sentences if len(s.strip()) > 20 and any(w in s.lower() for w in ["develop", "build", "design", "manage", "lead", "implement", "collaborate", "ensure", "maintain"])]
        if sens:
            return sens[:6]

        return [
            "Develop clean, maintainable backend services and REST APIs.",
            "Design database schemas and optimize query performance.",
            "Collaborate with cross-functional engineering teams on system architecture."
        ]

    @classmethod
    def build_candidate_evidence_blocks(cls, parsed_resume: Dict[str, Any], raw_resume: str) -> List[Dict[str, str]]:
        """Collects distinct evidence chunks from candidate resume."""
        blocks = []

        # Work experience items
        for exp in parsed_resume.get("experience", []):
            if isinstance(exp, dict):
                role = exp.get("role", "")
                company = exp.get("company", "")
                resps = " ".join(exp.get("responsibilities", []))
                techs = " ".join(exp.get("technologies", []))
                text = f"{role} at {company}. {resps} {techs}".strip()
                if text:
                    blocks.append({"type": "Work Experience", "title": role, "text": text})

        # Projects
        for proj in parsed_resume.get("projects", []):
            if isinstance(proj, dict):
                pname = proj.get("name", "")
                pdesc = proj.get("description", "")
                presps = " ".join(proj.get("responsibilities", []))
                ptechs = " ".join(proj.get("technologies", []))
                text = f"Project {pname}: {pdesc}. {presps} {ptechs}".strip()
                if text:
                    blocks.append({"type": "Project", "title": pname, "text": text})

        # Summary
        summary = parsed_resume.get("summary", "")
        if summary:
            blocks.append({"type": "Summary", "title": "Professional Summary", "text": summary})

        # Fallback if no structured blocks
        if not blocks:
            for para in raw_resume.split('\n\n'):
                if len(para.strip()) > 30:
                    blocks.append({"type": "Resume Section", "title": "Resume Content", "text": para.strip()})

        return blocks

    @classmethod
    def evaluate_single_responsibility(cls, resp: str, candidate_blocks: List[Dict[str, str]]) -> Dict[str, Any]:
        """Compares one responsibility against all candidate evidence blocks."""
        best_sim = 0.0
        best_block = None

        resp_tokens = set([t.lower() for t in TechnicalTokenizer.extract_keywords_filtered(resp)])

        for block in candidate_blocks:
            b_text = block["text"]
            sim = EmbeddingService.compute_similarity(resp, b_text)

            # Boost if shared technical keywords appear
            b_tokens = set([t.lower() for t in TechnicalTokenizer.extract_keywords_filtered(b_text)])
            shared_keywords = resp_tokens.intersection(b_tokens)
            keyword_overlap_ratio = len(shared_keywords) / len(resp_tokens) if resp_tokens else 0.0

            # Combined match score
            combined_match = max(sim, keyword_overlap_ratio * 0.90, (sim * 0.4 + keyword_overlap_ratio * 0.6))

            if combined_match > best_sim:
                best_sim = combined_match
                best_block = block

        # Convert to percentage
        match_pct = round(max(0.0, min(100.0, best_sim * 100.0)), 1)

        # Guard against best_block being None (empty resume or no evidence blocks)
        if best_block is None:
            return {
                "responsibility": resp,
                "match_percentage": 0.0,
                "status": "Missing / No Evidence",
                "evidence": "Resume has no work experience, projects, or relevant sections to evaluate.",
                "gap": "No candidate evidence available to match this responsibility."
            }

        if match_pct >= 70.0:
            status = "Strong Match"
            evidence = f"Demonstrated in {best_block['type']} ({best_block['title']}): '{best_block['text'][:140]}...'"
            gap = "Fully aligned with candidate background."
        elif match_pct >= 40.0:
            status = "Partial Match"
            evidence = f"Related capability in {best_block['type']} ({best_block['title']}): '{best_block['text'][:140]}...'"
            gap = "Related experience shown, but specific tools or depth could be clarified."
        else:
            status = "Missing / No Evidence"
            evidence = f"Weak or no match found. Closest: '{best_block['text'][:100]}...' — does not adequately address this requirement."
            gap = "No demonstrated experience matching this responsibility."

        return {
            "responsibility": resp,
            "match_percentage": match_pct,
            "status": status,
            "evidence": evidence,
            "gap": gap
        }
