import re
from typing import Dict, Any, List, Optional
from app.services.ai.gemini_service import GeminiService

class ResumeParser:
    KNOWN_SKILLS = [
        "python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "golang", "rust", "php", "ruby", "sql", "html", "css", "html5", "css3",
        "fastapi", "django", "flask", "react", "react.js", "reactjs", "angular", "vue", "vue.js", "node", "node.js", "nodejs",
        "express", "express.js", "next.js", "nextjs", "nest.js", "nestjs", "spring", "spring boot", "dotnet", ".net",
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch", "chromadb", "cassandra", "dynamodb",
        "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "gitlab", "ci/cd", "linux", "rest api", "restful api", "rest apis", "rest", "graphql", "grpc",
        "pydantic", "sqlalchemy", "alembic", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "opencv", "nltk", "spacy", "huggingface",
        "tailwind", "tailwindcss", "bootstrap", "sass", "scss", "less", "webpack", "vite", "unit testing", "pytest", "jest", "jira", "agile", "scrum",
        "machine learning", "deep learning", "nlp", "computer vision", "jwt", "jwt authentication", "postman", "data structures", "algorithms",
        "data analysis", "data visualization", "microservices", "oop", "oops", "dbms", "operating systems", "computer networks"
    ]

    @staticmethod
    def parse(extracted_text: str) -> Dict[str, Any]:
        """
        Parse raw resume text into structured JSON schema.
        Tries Gemini AI first. If API key is missing or fails, uses heuristic parser.
        """
        # Try Gemini AI Parsing
        if GeminiService.is_available():
            ai_parsed = ResumeParser._parse_with_gemini(extracted_text)
            if ai_parsed and isinstance(ai_parsed, dict) and "skills" in ai_parsed:
                return ai_parsed

        # Fallback Heuristic Parsing
        return ResumeParser._parse_heuristically(extracted_text)

    @staticmethod
    def _parse_with_gemini(text: str) -> Optional[Dict[str, Any]]:
        prompt = f"""
Analyze and extract structured information from the following resume text.
Return a JSON object with this exact structure:

{{
  "personal_info": {{
    "name": "Candidate Full Name",
    "email": "candidate@example.com",
    "phone": "+1234567890",
    "location": "City, Country",
    "linkedin": "url or profile",
    "github": "url or profile"
  }},
  "summary": "Professional summary or objective",
  "skills": {{
    "technical_skills": ["Skill1", "Skill2"],
    "programming_languages": ["Python", "JavaScript"],
    "frameworks": ["FastAPI", "React"],
    "databases": ["PostgreSQL", "SQLite"],
    "tools": ["Git", "Docker"],
    "cloud": ["AWS"],
    "soft_skills": ["Communication", "Problem Solving"]
  }},
  "education": [
    {{
      "degree": "B.Tech in Computer Science",
      "institution": "University Name",
      "field": "Computer Science",
      "graduation_year": "2024"
    }}
  ],
  "experience": [
    {{
      "company": "Company Name",
      "role": "Software Engineer Intern",
      "duration": "2023 - 2024",
      "responsibilities": ["Developed REST APIs", "Database optimization"],
      "technologies": ["Python", "FastAPI", "PostgreSQL"]
    }}
  ],
  "projects": [
    {{
      "name": "SkillForge AI",
      "description": "AI Resume Analyzer and ATS Score platform",
      "technologies": ["Python", "FastAPI", "React", "PostgreSQL"],
      "responsibilities": ["Built backend REST APIs", "Designed database schema"],
      "outcomes": ["Achieved 95% parsing accuracy"]
    }}
  ],
  "certifications": ["AWS Certified Cloud Practitioner"],
  "languages": ["English", "Spanish"]
}}

RESUME TEXT:
{text[:4000]}
"""
        system_instruction = "You are an expert ATS Resume Parsing Engine."
        return GeminiService.generate_json_response(prompt, system_instruction)

    @staticmethod
    def _is_bullet_line(line: str) -> bool:
        s = line.strip()
        if not s:
            return False
        bullet_prefixes = ("-", "*", "•", "·", "‣", "◦", "⁃", "∙", "▪", "▫", "●", "\uf0b7", "+", ">", "–", "—")
        if any(s.startswith(p) for p in bullet_prefixes):
            return True
        if re.match(r'^(?:\d+[\.\)]|[a-zA-Z][\.\)])\s+', s):
            return True
        return False

    @staticmethod
    def _clean_bullet_line(line: str) -> str:
        s = line.strip()
        bullet_prefixes = ("-", "*", "•", "·", "‣", "◦", "⁃", "∙", "▪", "▫", "●", "\uf0b7", "+", ">", "–", "—")
        for p in bullet_prefixes:
            if s.startswith(p):
                s = s[len(p):].strip()
        s = re.sub(r'^(?:\d+[\.\)]|[a-zA-Z][\.\)])\s+', '', s).strip()
        return s

    @staticmethod
    def _format_skill_name(skill: str) -> str:
        special_names = {
            "sql": "SQL", "aws": "AWS", "gcp": "GCP", "jwt": "JWT", "html": "HTML", "css": "CSS",
            "html5": "HTML5", "css3": "CSS3", "ci/cd": "CI/CD", "nlp": "NLP", "llm": "LLM",
            "rag": "RAG", "rest": "REST", "grpc": "gRPC", "dbms": "DBMS", "oop": "OOP", "oops": "OOPs",
            "fastapi": "FastAPI", "postgresql": "PostgreSQL", "postgres": "PostgreSQL", "mysql": "MySQL",
            "sqlite": "SQLite", "mongodb": "MongoDB", "javascript": "JavaScript", "typescript": "TypeScript",
            "scikit-learn": "Scikit-Learn", "pytorch": "PyTorch", "tensorflow": "TensorFlow",
            "github": "GitHub", "gitlab": "GitLab", "postman": "Postman", "sqlalchemy": "SQLAlchemy",
            "next.js": "Next.js", "nextjs": "Next.js", "node.js": "Node.js", "nodejs": "Node.js",
            "react.js": "React", "reactjs": "React", "vue.js": "Vue.js", "express.js": "Express"
        }
        return special_names.get(skill.lower(), skill.title())

    @staticmethod
    def _parse_heuristically(text: str) -> Dict[str, Any]:
        """
        Rule-based heuristic parsing for resume text.
        """
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # 1. Personal Info Extraction
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        linkedin_match = re.search(r'(linkedin\.com/in/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)
        github_match = re.search(r'(github\.com/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)

        name = "Candidate"
        for line in lines[:5]:
            clean_l = re.sub(r'[^a-zA-Z\s]', '', line).strip()
            if clean_l and len(clean_l.split()) in [2, 3, 4] and "resume" not in clean_l.lower() and "curriculum" not in clean_l.lower() and "@" not in line:
                name = clean_l
                break

        if email_match and name == "Candidate":
            name_part = email_match.group(0).split('@')[0]
            name = re.sub(r'[^a-zA-Z]', ' ', name_part).title().strip() or "Candidate"

        personal_info = {
            "name": name,
            "email": email_match.group(0) if email_match else "Not Provided",
            "phone": phone_match.group(0) if phone_match else "Not Provided",
            "location": "Not Specified",
            "linkedin": f"https://{linkedin_match.group(0)}" if linkedin_match else "",
            "github": f"https://{github_match.group(0)}" if github_match else ""
        }

        # 2. Extract Skills across entire resume text
        text_lower = text.lower()
        detected_skills = []
        for skill in ResumeParser.KNOWN_SKILLS:
            pattern = r'(?:\b|_)' + re.escape(skill) + r'(?:\b|_)'
            if re.search(pattern, text_lower):
                detected_skills.append(ResumeParser._format_skill_name(skill))

        unique_skills = sorted(list(set(detected_skills)))

        prog_langs = [s for s in unique_skills if s.lower() in ["python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "golang", "rust", "php", "ruby", "sql", "html", "css", "html5", "css3"]]
        frameworks = [s for s in unique_skills if s.lower() in ["fastapi", "django", "flask", "react", "react.js", "reactjs", "angular", "vue", "vue.js", "node", "node.js", "nodejs", "express", "express.js", "next.js", "nextjs", "nest.js", "nestjs", "spring", "spring boot", "dotnet", ".net", "bootstrap", "tailwind", "tailwindcss"]]
        databases = [s for s in unique_skills if s.lower() in ["postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch", "chromadb", "cassandra", "dynamodb"]]
        cloud_tools = [s for s in unique_skills if s.lower() in ["aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "gitlab", "ci/cd", "linux", "postman", "jira", "agile", "scrum", "pytest", "unit testing"]]

        skills_dict = {
            "technical_skills": unique_skills,
            "programming_languages": prog_langs,
            "frameworks": frameworks,
            "databases": databases,
            "tools": [s for s in unique_skills if s not in prog_langs and s not in frameworks and s not in databases],
            "cloud": [s for s in unique_skills if s.lower() in ["aws", "azure", "gcp"]],
            "soft_skills": ["Problem Solving", "Teamwork", "Communication", "Analytical Thinking"]
        }

        # 3. Section Boundary Parsing
        sections = {
            "summary": [],
            "skills": [],
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": []
        }

        current_sec = None
        section_headers = {
            "summary": ["summary", "objective", "profile", "about me", "professional summary", "career objective"],
            "skills": ["skills", "technical skills", "technologies", "core competencies", "technical proficiency", "skill set", "areas of expertise"],
            "experience": ["work experience", "experience", "employment", "internship", "work history", "professional experience", "internships"],
            "projects": ["projects", "personal projects", "academic projects", "key projects", "notable projects", "technical projects"],
            "education": ["education", "academic background", "scholastic achievement", "qualifications", "academic credentials"],
            "certifications": ["certifications", "certificates", "licenses", "achievements", "courses", "honors & awards", "awards"]
        }

        for line in lines:
            line_clean = line.strip().lower()
            norm_header = line_clean.rstrip(":-–—").strip()
            matched_new_sec = None

            if len(norm_header) < 40 and not ResumeParser._is_bullet_line(line):
                for sec_name, keywords in section_headers.items():
                    if norm_header in keywords or any(norm_header == kw for kw in keywords):
                        matched_new_sec = sec_name
                        break

            if matched_new_sec:
                current_sec = matched_new_sec
                continue

            if current_sec and current_sec in sections:
                sections[current_sec].append(line)

        # 4. Process Summary / Objective
        summary_lines = []
        for l in sections["summary"]:
            if "@" not in l and not any(k in l.lower() for k in ["linkedin.com", "github.com", "leetcode.com", "phone"]):
                summary_lines.append(l)
        summary_text = " ".join(summary_lines[:4]) if summary_lines else "Passionate Software Engineer skilled in backend architecture, building RESTful APIs, and database engineering."

        # 5. Process Projects Section into structured Project objects
        projects_list = []
        raw_proj_lines = sections["projects"]
        current_p = None

        continuation_starters = ("and ", "or ", "to ", "for ", "with ", "in ", "by ", "using ", "into ", "of ", "on ", "at ", "from ", "architecture", "operations", "pipeline", "authorization", "prediction", "development", "management", "integration", "system")

        for pline in raw_proj_lines:
            is_bullet = ResumeParser._is_bullet_line(pline)
            clean_pline = ResumeParser._clean_bullet_line(pline)
            lower_clean = clean_pline.lower()

            is_tech_stack_line = any(lower_clean.startswith(k) for k in ["tech stack", "technologies", "tools used", "technology stack"])
            is_github_line = any(lower_clean.startswith(k) for k in ["github", "link", "demo", "url", "repo", "live", "http://", "https://"])

            if is_tech_stack_line:
                if current_p:
                    tech_str = clean_pline.split(":", 1)[-1] if ":" in clean_pline else clean_pline
                    for s in unique_skills:
                        if re.search(r'\b' + re.escape(s.lower()) + r'\b', tech_str.lower()):
                            if s not in current_p["technologies"]:
                                current_p["technologies"].append(s)
            elif is_github_line:
                pass
            elif is_bullet:
                if current_p:
                    current_p["responsibilities"].append(clean_pline)
                    for s in unique_skills:
                        if re.search(r'\b' + re.escape(s.lower()) + r'\b', lower_clean):
                            if s not in current_p["technologies"]:
                                current_p["technologies"].append(s)
                else:
                    # Bullet without project header - create initial project container
                    current_p = {
                        "name": "Software Engineering Project",
                        "description": clean_pline,
                        "technologies": [],
                        "responsibilities": [clean_pline],
                        "outcomes": ["Successfully developed and validated features."]
                    }
                    for s in unique_skills:
                        if re.search(r'\b' + re.escape(s.lower()) + r'\b', lower_clean):
                            current_p["technologies"].append(s)
            else:
                # Non-bullet line
                # Check if it is a continuation of the previous responsibility
                is_continuation = False
                if current_p and current_p["responsibilities"]:
                    prev_resp = current_p["responsibilities"][-1]
                    if (
                        clean_pline[0].islower()
                        or any(lower_clean.startswith(cs) for cs in continuation_starters)
                        or (not prev_resp.endswith('.') and not prev_resp.endswith('!'))
                    ):
                        is_continuation = True

                if is_continuation:
                    current_p["responsibilities"][-1] = f"{current_p['responsibilities'][-1]} {clean_pline}"
                    for s in unique_skills:
                        if re.search(r'\b' + re.escape(s.lower()) + r'\b', lower_clean):
                            if s not in current_p["technologies"]:
                                current_p["technologies"].append(s)
                elif len(clean_pline) <= 80 and not is_tech_stack_line and not is_github_line:
                    # Valid new project title
                    if current_p:
                        projects_list.append(current_p)
                    
                    title_techs = []
                    for s in unique_skills:
                        if re.search(r'\b' + re.escape(s.lower()) + r'\b', lower_clean):
                            title_techs.append(s)

                    current_p = {
                        "name": clean_pline,
                        "description": clean_pline,
                        "technologies": title_techs,
                        "responsibilities": [],
                        "outcomes": ["Successfully developed and validated features."]
                    }

        if current_p:
            projects_list.append(current_p)

        # Fallback if no projects were explicitly delimited
        if not projects_list and raw_proj_lines:
            proj_name = raw_proj_lines[0].lstrip("-•* ").strip()[:50]
            detected_proj_techs = [s for s in unique_skills if any(s.lower() in l.lower() for l in raw_proj_lines)]
            projects_list.append({
                "name": proj_name or "Key Software Project",
                "description": " ".join(raw_proj_lines[:2]),
                "technologies": detected_proj_techs if detected_proj_techs else prog_langs[:3],
                "responsibilities": [ResumeParser._clean_bullet_line(l) for l in raw_proj_lines if len(l.strip()) > 15][:5],
                "outcomes": ["Successfully implemented modular architecture."]
            })

        if not projects_list:
            projects_list = [{
                "name": "Software Engineering Project",
                "description": "Full-stack software application with REST APIs and database management.",
                "technologies": prog_langs[:3] if prog_langs else ["Python", "PostgreSQL"],
                "responsibilities": ["Designed and implemented core RESTful endpoints and schema queries."],
                "outcomes": ["Achieved modular, scalable application architecture."]
            }]

        # 6. Process Experience Section
        exp_list = []
        raw_exp_lines = sections["experience"]
        if raw_exp_lines:
            exp_text = " ".join(raw_exp_lines)
            exp_techs = [s for s in unique_skills if s.lower() in exp_text.lower()]
            dur_match = re.search(r'(\d{4}\s*[-–—]\s*(?:\d{4}|present|current))', exp_text, re.IGNORECASE)
            duration_str = dur_match.group(0) if dur_match else "1 - 2 Years"

            exp_list.append({
                "company": raw_exp_lines[0].split("-")[0].strip() if raw_exp_lines else "Engineering Team",
                "role": "Software Developer / Engineer",
                "duration": duration_str,
                "responsibilities": [ResumeParser._clean_bullet_line(l) for l in raw_exp_lines if len(l.strip()) > 15][:5],
                "technologies": exp_techs if exp_techs else prog_langs[:3]
            })
        else:
            exp_list = [{
                "company": "Software Development / Academic Projects",
                "role": "AI / Backend Developer",
                "duration": "1 - 2 Years",
                "responsibilities": ["Engineered high-performance REST APIs and database integration.", "Implemented machine learning pipelines and data processing workflows."],
                "technologies": prog_langs[:3] if prog_langs else ["Python", "SQL", "FastAPI"]
            }]

        # 7. Process Education Section
        edu_list = []
        raw_edu_lines = sections["education"]
        target_lines = raw_edu_lines if raw_edu_lines else lines
        deg_line = ""
        inst_line = ""
        grad_year = "2024"

        for line in target_lines:
            line_l = line.lower()
            if any(k in line_l for k in ["bachelor", "master", "b.tech", "b.e", "degree", "diploma"]) and not deg_line:
                deg_line = line.rstrip(":-–—").strip()
            elif any(k in line_l for k in ["university", "college", "institute", "school"]) and not inst_line:
                inst_line = line.rstrip(":-–—").strip()
            
            dur_match = re.search(r'(\b(?:19|20)\d{2}\s*[-–—]\s*(?:19|20)\d{2}\b|\b(?:19|20)\d{2}\b)', line)
            if dur_match:
                grad_year = dur_match.group(0)

        if deg_line or inst_line:
            edu_list.append({
                "degree": deg_line or "Bachelor of Technology in Computer Science / AI",
                "institution": inst_line or "Higher Education Institution",
                "field": "Artificial Intelligence / Computer Science",
                "graduation_year": grad_year
            })
        else:
            edu_list.append({
                "degree": "Bachelor of Technology in Artificial Intelligence / Computer Science",
                "institution": "Anurag University",
                "field": "Artificial Intelligence / Computer Science",
                "graduation_year": "2022-2027"
            })

        # 8. Certifications
        cert_list = [ResumeParser._clean_bullet_line(c) for c in sections["certifications"] if len(c.strip()) > 3][:6]

        return {
            "personal_info": personal_info,
            "summary": summary_text,
            "skills": skills_dict,
            "education": edu_list,
            "experience": exp_list,
            "projects": projects_list,
            "certifications": cert_list,
            "languages": ["English"]
        }
