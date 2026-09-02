import json
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseAIProvider(ABC):
    """
    Abstract Base Class for Multi-Model AI ATS Providers (Gemini, OpenAI, Claude).
    Enforces identical prompt formulation, analysis requirements, and strict JSON output schemas.
    """

    def __init__(self, provider_name: str, model_id: str, api_key: Optional[str]):
        self.provider_name = provider_name
        self.model_id = model_id
        self.api_key = api_key

    @abstractmethod
    async def analyze(
        self,
        raw_resume: str,
        raw_jd: str,
        parsed_resume: Dict[str, Any],
        parsed_job: Dict[str, Any],
        deterministic_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute model-specific inference and return normalized analysis dict."""
        pass

    @classmethod
    def get_canonical_system_prompt(cls) -> str:
        """Shared system instructions enforcing strict evidence-based ATS evaluation."""
        return """You are a Principal Technical Recruiter and ATS Evaluation Engine.
Your goal is to perform a rigorous, evidence-based evaluation of a candidate's resume against a target job description.

RULES YOU MUST STRICTLY FOLLOW:
1. Ground every score in direct evidence from the resume and JD text. NEVER invent skills, years of experience, or responsibilities.
2. If experience is lacking (e.g. fresh graduate for a senior role), the experience score MUST reflect that gap accurately (e.g. 0-30%). Never award a generic 100%.
3. Distinguish Required vs Preferred skills: Missing a Required skill must significantly lower the skills score.
4. For responsibilities, evaluate each requirement in the JD individually with specific evidence snippets from the resume.
5. All recommendations must be personalized and job-specific based on actual missing technologies or gaps.
6. Return your response ONLY as valid, raw JSON with NO markdown code fences (no ```json, no ```)."""

    @classmethod
    def build_user_prompt(
        cls,
        raw_resume: str,
        raw_jd: str,
        parsed_resume: Dict[str, Any],
        parsed_job: Dict[str, Any],
        deterministic_data: Dict[str, Any]
    ) -> str:
        """Constructs standardized evaluation prompt with deterministic anchor data."""
        det_scores = deterministic_data.get("parameter_scores", {})
        det_exp = deterministic_data.get("experience", {})
        det_skills = deterministic_data.get("skills", {})

        return f"""Analyze the following Candidate Resume against the Target Job Description.

--- TARGET JOB DESCRIPTION ---
{raw_jd}

--- CANDIDATE RESUME ---
{raw_resume}

--- OBJECTIVE DETERMINISTIC BASELINE METRICS (For Context) ---
- Objective Skills Score: {det_scores.get('skill_score', 'N/A')}%
- Required Skills Matched: {len(det_skills.get('matched_skills', []))} / {det_skills.get('total_job_skills_count', 'N/A')}
- Objective Experience Score: {det_scores.get('experience_score', 'N/A')}%
- Candidate Relevant Experience: {det_exp.get('candidate_relevant_years', 0)} years vs {det_exp.get('required_experience_years', 0)} years required
- Objective Keyword Coverage: {det_scores.get('keyword_score', 'N/A')}%

--- REQUIRED OUTPUT JSON SCHEMA ---
{{
  "overall_score": <number 0-100>,
  "job_fit": "<'Poor' | 'Moderate' | 'Good' | 'Strong' | 'Exceptional'>",
  "confidence": <number 0-100>,
  "parameter_scores": {{
    "skill_score": <number 0-100>,
    "experience_score": <number 0-100>,
    "responsibility_score": <number 0-100>,
    "keyword_score": <number 0-100>,
    "technical_skills": <number 0-100>,
    "soft_skills": <number 0-100>,
    "education_score": <number 0-100>,
    "semantic_score": <number 0-100>
  }},
  "matched_skills": ["<Skill 1>", "<Skill 2>"],
  "missing_skills": ["<Missing Skill 1>", "<Missing Skill 2>"],
  "partial_skills": [
    {{
      "skill": "<Required Skill>",
      "related_experience": "<Related skill or context in resume>",
      "similarity": <number 0-100>
    }}
  ],
  "matched_responsibilities": [
    {{
      "responsibility": "<JD Responsibility statement>",
      "match_percentage": <number 0-100>,
      "status": "<'Strong Match' | 'Partial Match' | 'Missing'>",
      "evidence": "<Specific evidence from resume or 'No direct evidence found'>",
      "gap": "<Gap explanation>"
    }}
  ],
  "missing_responsibilities": ["<Unmatched Responsibility 1>"],
  "strengths": ["<Evidence-backed strength 1>", "<Evidence-backed strength 2>"],
  "weaknesses": ["<Evidence-backed weakness 1>", "<Evidence-backed weakness 2>"],
  "recommendations": ["<Actionable job-specific recommendation 1>", "<Actionable job-specific recommendation 2>"],
  "learning_requirements": [
    {{
      "skill": "<Missing Technology>",
      "priority": "<'High' | 'Medium' | 'Low'>",
      "reason": "<Why this technology is required for this specific job>",
      "expected_benefit": "<How acquiring this skill boosts ATS score and interview readiness>"
    }}
  ],
  "resume_improvements": [
    "<Specific recommendation for resume content, e.g. If you performed X, quantify Y>"
  ],
  "evidence_summary": [
    "<Key quantitative evidence justifying the overall score>"
  ]
}}"""

    @classmethod
    def clean_json_response(cls, text: str) -> Optional[Dict[str, Any]]:
        """Extracts and parses JSON from AI text response with markdown stripping and repair."""
        if not text:
            return None

        clean_text = text.strip()

        # Remove markdown code block fences if present
        if clean_text.startswith("```"):
            clean_text = re.sub(r'^```(?:json)?\s*', '', clean_text, flags=re.IGNORECASE)
            clean_text = re.sub(r'\s*```$', '', clean_text)

        # Try direct parse
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            pass

        # Search for first { and last }
        start_idx = clean_text.find('{')
        end_idx = clean_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            substring = clean_text[start_idx:end_idx + 1]
            try:
                return json.loads(substring)
            except json.JSONDecodeError:
                # Attempt minor JSON fixes (trailing commas)
                repaired = re.sub(r',\s*([\]}])', r'\1', substring)
                try:
                    return json.loads(repaired)
                except Exception:
                    pass

        return None

    @classmethod
    def create_fallback_response(
        cls,
        provider_name: str,
        model_id: str,
        status: str,
        error_msg: str,
        deterministic_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates a safe fallback matching the exact schema when provider is unavailable/fails."""
        det_scores = deterministic_data.get("parameter_scores", {})
        det_skills = deterministic_data.get("skills", {})
        det_exp = deterministic_data.get("experience", {})
        det_resp = deterministic_data.get("responsibilities", {})

        return {
            "provider_name": provider_name,
            "model_id": model_id,
            "status": status,
            "error_message": error_msg,
            "overall_score": det_scores.get("overall_score", 50.0),
            "job_fit": "Moderate" if det_scores.get("overall_score", 50) >= 60 else "Poor",
            "confidence": 85.0 if status == "success" else 50.0,
            "parameter_scores": {
                "skill_score": det_scores.get("skill_score", 50.0),
                "experience_score": det_scores.get("experience_score", 50.0),
                "responsibility_score": det_scores.get("responsibility_score", 50.0),
                "keyword_score": det_scores.get("keyword_score", 50.0),
                "technical_skills": det_scores.get("skill_score", 50.0),
                "soft_skills": 70.0,
                "education_score": det_scores.get("education_score", 75.0),
                "semantic_score": det_scores.get("semantic_score", 50.0)
            },
            "matched_skills": det_skills.get("matched_skills", []),
            "missing_skills": det_skills.get("missing_skills", []),
            "partial_skills": det_skills.get("partial_skills", []),
            "matched_responsibilities": det_resp.get("evaluations", []),
            "missing_responsibilities": [e["responsibility"] for e in det_resp.get("evaluations", []) if e.get("match_percentage", 0) < 35.0],
            "strengths": [
                f"Candidate matches {len(det_skills.get('matched_skills', []))} key technical requirements.",
                f"Demonstrates relevant background in {det_exp.get('match_status', 'Technical Development')}."
            ],
            "weaknesses": [
                f"Missing {len(det_skills.get('missing_skills', []))} target technologies from job description.",
                det_exp.get("gap_summary", "Experience depth could be strengthened.")
            ],
            "recommendations": [
                f"Target key missing skills: {', '.join(det_skills.get('missing_skills', [])[:3])}.",
                "Quantify achievements in resume project bullet points."
            ],
            "learning_requirements": [
                {
                    "skill": s,
                    "priority": "High" if idx < 2 else "Medium",
                    "reason": "Listed in target Job Description requirements.",
                    "expected_benefit": "Directly addresses core skill gap for role readiness."
                }
                for idx, s in enumerate(det_skills.get("missing_skills", [])[:4])
            ],
            "resume_improvements": [
                "Highlight target technology keywords in work history bullet points.",
                "Detail measurable impact and outcomes for each project."
            ],
            "evidence_summary": [
                det_exp.get("explanation", "Experience calculated from work history."),
                f"Matched {len(det_skills.get('matched_skills', []))} target skills."
            ]
        }
