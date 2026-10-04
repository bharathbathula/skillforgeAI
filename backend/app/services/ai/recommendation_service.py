import json
import logging
import re
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class RecommendationService:
    """
    Downstream AI Recommendation Service.
    
    Architectural Guarantees:
    1. Core ATS scoring is 100% deterministic and runs before this service.
    2. This service NEVER changes or overwrites the ATS score.
    3. No sensitive candidate PII (name, email, phone) or raw resume is sent to external LLMs.
    4. If no AI API key is configured or the provider fails, a robust rule-based fallback
       is generated deterministically from missing skill gaps and the target role.
    """

    @classmethod
    async def get_recommendations(cls, analysis_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates actionable recommendations (priority skills, project ideas, learning directions,
        and resume improvements). Tries external AI provider first if configured, else rule-based fallback.
        """
        target_role = analysis_context.get("target_role", "Target Role")
        matched_skills = analysis_context.get("matched_skills", [])
        missing_skills = analysis_context.get("missing_skills", [])
        skill_score = analysis_context.get("skill_score", 0.0)
        exp_score = analysis_context.get("experience_score", 0.0)
        gap_summary = analysis_context.get("gap_summary", "")
        formatting_improvements = analysis_context.get("formatting_improvements", [])

        # Check if external AI provider is configured (e.g. Gemini)
        gemini_key = getattr(settings, "GEMINI_API_KEY", None)
        openai_key = getattr(settings, "OPENAI_API_KEY", None)

        if gemini_key and gemini_key.strip():
            try:
                ai_result = await cls._generate_with_gemini(
                    gemini_key, target_role, matched_skills, missing_skills,
                    skill_score, exp_score, gap_summary, formatting_improvements
                )
                if cls._validate_schema(ai_result):
                    ai_result["source"] = "ai_assisted"
                    ai_result["provider"] = "Gemini"
                    ai_result["is_ai_generated"] = True
                    return ai_result
            except Exception as e:
                logger.warning(f"External Gemini recommendation provider failed, falling back to rule-based: {e}")

        elif openai_key and openai_key.strip():
            try:
                ai_result = await cls._generate_with_openai(
                    openai_key, target_role, matched_skills, missing_skills,
                    skill_score, exp_score, gap_summary, formatting_improvements
                )
                if cls._validate_schema(ai_result):
                    ai_result["source"] = "ai_assisted"
                    ai_result["provider"] = "OpenAI"
                    ai_result["is_ai_generated"] = True
                    return ai_result
            except Exception as e:
                logger.warning(f"External OpenAI recommendation provider failed, falling back to rule-based: {e}")

        # Deterministic rule-based fallback
        fallback = cls.generate_rule_based_recommendations(analysis_context)
        fallback["source"] = "rule_based"
        fallback["provider"] = "none"
        fallback["is_ai_generated"] = False
        return fallback

    @classmethod
    def generate_rule_based_recommendations(cls, analysis_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates deterministic, grounded recommendations based strictly on identified skill gaps
        and target role requirements without using any external LLM.
        """
        target_role = analysis_context.get("target_role", "Software Engineer")
        missing_skills = analysis_context.get("missing_skills", [])
        matched_skills = analysis_context.get("matched_skills", [])
        formatting_improvements = analysis_context.get("formatting_improvements", [])
        gap_summary = analysis_context.get("gap_summary", "")

        priority_skills = missing_skills[:5]

        # Generate 2-4 concrete project suggestions tied directly to missing skills
        project_suggestions = []
        if priority_skills:
            # Group 1: Infrastructure / Cloud / DevOps
            infra_skills = [s for s in priority_skills if s.lower() in [
                "docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "terraform", "linux"
            ]]
            if infra_skills:
                project_suggestions.append({
                    "title": f"Containerized Cloud Deployment Pipeline for {target_role}",
                    "why_relevant": f"Demonstrates hands-on containerization and automated deployment required for {target_role}.",
                    "skills_practiced": infra_skills[:3],
                    "difficulty": "Intermediate"
                })

            # Group 2: Database / Performance
            db_skills = [s for s in priority_skills if s.lower() in [
                "postgresql", "postgres", "sql", "redis", "mongodb", "elasticsearch", "mysql"
            ]]
            if db_skills:
                project_suggestions.append({
                    "title": f"High-Throughput Data Persistence & Caching Service",
                    "why_relevant": f"Addresses critical database design and query optimization requirements identified in the job description.",
                    "skills_practiced": db_skills[:3],
                    "difficulty": "Intermediate"
                })

            # Group 3: Core Framework / Language / API
            code_skills = [s for s in priority_skills if s not in infra_skills and s not in db_skills]
            if code_skills:
                lead_skill = code_skills[0]
                other_skills = code_skills[1:3]
                project_suggestions.append({
                    "title": f"Production-Ready {lead_skill} Service Architecture",
                    "why_relevant": f"Directly bridges your highest priority skill gap in {lead_skill} tailored to {target_role} expectations.",
                    "skills_practiced": [lead_skill] + other_skills,
                    "difficulty": "Intermediate"
                })
        else:
            # When candidate matched all skills
            project_suggestions.append({
                "title": f"Advanced Scalability & Performance Benchmarking System",
                "why_relevant": f"Strengthens profile for {target_role} by demonstrating system optimization and reliability engineering.",
                "skills_practiced": matched_skills[:3] if matched_skills else ["System Design", "Performance Tuning"],
                "difficulty": "Advanced"
            })

        # Learning direction
        learning_direction = []
        if priority_skills:
            for s in priority_skills[:3]:
                learning_direction.append(
                    f"Master core fundamentals and architecture of {s}, then build and test a standalone module before integrating it."
                )
        if gap_summary:
            learning_direction.append(f"Experience alignment: {gap_summary}")
        else:
            learning_direction.append("Deepen domain knowledge in system design, distributed data handling, and automated unit testing.")

        # Resume improvements
        resume_improvements = []
        if formatting_improvements:
            resume_improvements.extend(formatting_improvements[:3])

        if priority_skills:
            resume_improvements.append(
                f"Once you complete hands-on work with {', '.join(priority_skills[:2])}, list them explicitly under 'Technical Skills' and include metric-driven bullet points under 'Projects'."
            )
        else:
            resume_improvements.append(
                "Ensure every project bullet point follows the Action-Context-Result framework (e.g. 'Reduced API latency by 35% using Redis caching')."
            )

        return {
            "priority_skills": priority_skills,
            "project_suggestions": project_suggestions[:3],
            "learning_direction": learning_direction[:4],
            "resume_improvements": resume_improvements[:4]
        }

    @classmethod
    async def _generate_with_gemini(
        cls,
        api_key: str,
        target_role: str,
        matched_skills: List[str],
        missing_skills: List[str],
        skill_score: float,
        exp_score: float,
        gap_summary: str,
        formatting_improvements: List[str]
    ) -> Dict[str, Any]:
        """Calls Gemini API with structured prompt (no candidate PII)."""
        import httpx

        prompt = f"""You are a Technical Career Advisor. Generate realistic, grounded recommendations for a candidate targeting the role: '{target_role}'.

Context (No candidate PII):
- Matched Skills: {', '.join(matched_skills) if matched_skills else 'None'}
- Missing Required/Preferred Skills: {', '.join(missing_skills) if missing_skills else 'None'}
- Skill Alignment Score: {skill_score}%
- Experience Alignment: {gap_summary}

RULES:
1. Recommend ONLY 2-3 realistic projects that directly practice the missing skills.
2. DO NOT invent employers, certifications, guaranteed hiring outcomes, or job openings.
3. DO NOT change any score or mention score calculations.
4. Return ONLY a valid JSON object matching the schema below (no markdown fences, no extra text).

SCHEMA:
{{
  "priority_skills": ["<skill1>", "<skill2>"],
  "project_suggestions": [
    {{
      "title": "<Project Title>",
      "why_relevant": "<Why relevant to target role and gaps>",
      "skills_practiced": ["<skill1>", "<skill2>"],
      "difficulty": "<Beginner | Intermediate | Advanced>"
    }}
  ],
  "learning_direction": ["<actionable learning direction 1>", "<actionable learning direction 2>"],
  "resume_improvements": ["<concrete resume phrasing improvement 1>", "<concrete resume phrasing improvement 2>"]
}}"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                # Strip markdown if present
                clean_json = re.sub(r'^```json\s*', '', raw_text)
                clean_json = re.sub(r'```$', '', clean_json).strip()
                return json.loads(clean_json)
            else:
                raise RuntimeError(f"Gemini API returned status {resp.status_code}")

    @classmethod
    async def _generate_with_openai(
        cls,
        api_key: str,
        target_role: str,
        matched_skills: List[str],
        missing_skills: List[str],
        skill_score: float,
        exp_score: float,
        gap_summary: str,
        formatting_improvements: List[str]
    ) -> Dict[str, Any]:
        """Calls OpenAI API with structured prompt (no candidate PII)."""
        import httpx

        prompt = f"""You are a Technical Career Advisor. Generate realistic, grounded recommendations for a candidate targeting the role: '{target_role}'.

Context:
- Matched Skills: {', '.join(matched_skills) if matched_skills else 'None'}
- Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}
- Skill Alignment: {skill_score}%
- Experience Alignment: {gap_summary}

Return ONLY valid JSON matching:
{{
  "priority_skills": [],
  "project_suggestions": [
    {{
      "title": "",
      "why_relevant": "",
      "skills_practiced": [],
      "difficulty": ""
    }}
  ],
  "learning_direction": [],
  "resume_improvements": []
}}"""

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a Technical Career Advisor. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                raw_text = data["choices"][0]["message"]["content"].strip()
                return json.loads(raw_text)
            else:
                raise RuntimeError(f"OpenAI API returned status {resp.status_code}")

    @classmethod
    def _validate_schema(cls, data: Any) -> bool:
        """Validates that recommendation response matches the strict schema."""
        if not isinstance(data, dict):
            return False

        if "priority_skills" not in data or not isinstance(data["priority_skills"], list):
            return False

        if "project_suggestions" not in data or not isinstance(data["project_suggestions"], list):
            return False

        for p in data["project_suggestions"]:
            if not isinstance(p, dict):
                return False
            if "title" not in p or "why_relevant" not in p or "skills_practiced" not in p:
                return False

        if "learning_direction" not in data or not isinstance(data["learning_direction"], list):
            return False

        if "resume_improvements" not in data or not isinstance(data["resume_improvements"], list):
            return False

        return True
