import re
from typing import Dict, Any, List, Optional
from app.services.ai.gemini_service import GeminiService
from app.services.parsing.resume_parser import ResumeParser

class JobParser:
    @staticmethod
    def parse(job_title: str, job_text: str) -> Dict[str, Any]:
        """
        Parse raw job description text into structured JSON schema.
        Tries Gemini AI first. If API key is missing or fails, uses heuristic parser.
        """
        full_text = f"Title: {job_title}\nDescription:\n{job_text}"

        if GeminiService.is_available():
            ai_parsed = JobParser._parse_with_gemini(full_text)
            if ai_parsed and isinstance(ai_parsed, dict) and "required_skills" in ai_parsed.get("skills", {}):
                return ai_parsed

        return JobParser._parse_heuristically(job_title, job_text)

    @staticmethod
    def _parse_with_gemini(text: str) -> Optional[Dict[str, Any]]:
        prompt = f"""
Analyze and extract structured requirements from the following job description.
Return a JSON object with this exact structure:

{{
  "job_info": {{
    "title": "Job Title",
    "company": "Company Name if present",
    "experience_required": "2+ years",
    "education_required": "Bachelor's degree in Computer Science or related field"
  }},
  "skills": {{
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "preferred_skills": ["Docker", "AWS", "Redis"],
    "optional_skills": ["GraphQL", "Kubernetes"],
    "tools": ["Git", "Docker", "Jira"],
    "frameworks": ["FastAPI", "React"],
    "databases": ["PostgreSQL"],
    "cloud": ["AWS"]
  }},
  "responsibilities": [
    "Develop high-performance REST APIs",
    "Design database schemas and write optimized SQL queries"
  ],
  "qualifications": [
    "Bachelor's degree in Computer Science",
    "2+ years software engineering experience"
  ],
  "keywords": [
    "Python", "FastAPI", "PostgreSQL", "REST API", "Database", "AWS", "Docker"
  ]
}}

JOB DESCRIPTION:
{text[:4000]}
"""
        system_instruction = "You are an expert Job Description Analyzer and Recruiter."
        return GeminiService.generate_json_response(prompt, system_instruction)

    @staticmethod
    def _parse_heuristically(job_title: str, job_text: str) -> Dict[str, Any]:
        """
        Rule-based heuristic parsing for job description text.
        """
        combined = f"{job_title} {job_text}".lower()
        
        # Detect skills from known list
        detected_skills = []
        for skill in ResumeParser.KNOWN_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, combined):
                detected_skills.append(skill.upper() if len(skill) <= 3 else skill.title())

        unique_skills = sorted(list(set(detected_skills)))

        # Split into required vs preferred based on text clues
        required_skills = []
        preferred_skills = []
        
        for s in unique_skills:
            if s.lower() in ["docker", "aws", "kubernetes", "redis", "graphql", "azure"]:
                preferred_skills.append(s)
            else:
                required_skills.append(s)

        if not required_skills:
            required_skills = unique_skills[:3] if unique_skills else ["Python", "SQL"]

        # Responsibilities
        lines = job_text.split('\n')
        responsibilities = [l.lstrip('-*• ').strip() for l in lines if len(l.strip()) > 15 and len(l.strip()) < 150][:6]
        if not responsibilities:
            responsibilities = [
                "Develop clean, maintainable backend services and REST APIs.",
                "Collaborate with engineering team on system design and database architecture."
            ]

        # Experience & Education extraction
        exp_match = re.search(r'(\d+\+?\s*(?:-\s*\d+)?\s*(?:years?|yrs?))', job_text, re.IGNORECASE)
        exp_required = exp_match.group(0) if exp_match else "1-3 years"

        edu_match = re.search(r'(bachelor|master|b\.tech|b\.e|degree|computer science)', job_text, re.IGNORECASE)
        edu_required = "Bachelor's degree in Computer Science or related technical field" if edu_match else "Bachelor's degree"

        # Keywords extraction
        keywords = unique_skills.copy()
        for kw in ["API", "REST", "Database", "Backend", "Frontend", "Architecture", "Microservices", "Scalability"]:
            if kw.lower() in combined:
                keywords.append(kw)
        
        keywords = sorted(list(set(keywords)))

        return {
            "job_info": {
                "title": job_title or "Software Engineer",
                "company": "Hiring Organization",
                "experience_required": exp_required,
                "education_required": edu_required
            },
            "skills": {
                "required_skills": required_skills,
                "preferred_skills": preferred_skills,
                "optional_skills": ["Agile", "CI/CD"],
                "tools": [s for s in unique_skills if s.lower() in ["git", "docker", "jira", "linux"]],
                "frameworks": [s for s in unique_skills if s.lower() in ["fastapi", "django", "flask", "react", "angular", "node"]],
                "databases": [s for s in unique_skills if s.lower() in ["postgresql", "postgres", "mysql", "sqlite", "mongodb"]],
                "cloud": [s for s in unique_skills if s.lower() in ["aws", "azure", "gcp"]]
            },
            "responsibilities": responsibilities,
            "qualifications": [
                edu_required,
                f"{exp_required} experience in software development"
            ],
            "keywords": keywords
        }
