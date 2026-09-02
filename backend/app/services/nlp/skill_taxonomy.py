import re
from typing import Dict, List, Set, Any, Optional
from app.services.nlp.technical_tokenizer import TechnicalTokenizer

class SkillTaxonomy:
    """
    Rich multi-domain skill taxonomy and pattern extraction service.
    Classifies skills into categories and tracks evidence levels.
    """

    CATEGORIES = {
        "programming_languages": [
            "python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "rust",
            "ruby", "php", "swift", "kotlin", "scala", "r", "dart", "sql", "bash", "shell",
            "html", "css", "html5", "css3", "sass", "less", "perl", "haskell", "elixir", "clojure",
            "assembly", "vba", "matlab"
        ],
        "frameworks_libraries": [
            "fastapi", "django", "flask", "react", "react.js", "react native", "next.js",
            "angular", "vue", "vue.js", "nuxt.js", "node.js", "express", "express.js",
            "spring boot", "spring", "asp.net", ".net", ".net core", "ruby on rails", "rails",
            "laravel", "symfony", "graphql", "tailwind", "tailwind css", "bootstrap", "material-ui",
            "chakra ui", "redux", "zustand", "rxjs", "jquery", "pytorch", "tensorflow", "keras",
            "scikit-learn", "pandas", "numpy", "scipy", "opencv", "matplotlib", "seaborn",
            "langchain", "llamaindex", "huggingface", "transformers", "sqlalchemy", "alembic",
            "prisma", "typeorm", "hibernate", "pydantic", "pytest", "unittest", "jest", "mocha",
            "cypress", "selenium", "playwright"
        ],
        "databases_storage": [
            "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
            "opensearch", "dynamodb", "cassandra", "mariadb", "oracle", "microsoft sql server",
            "ms sql", "couchbase", "neo4j", "chromadb", "pinecone", "weaviate", "qdrant",
            "milvus", "snowflake", "bigquery", "redshift", "firebase", "supabase"
        ],
        "cloud_devops": [
            "aws", "amazon web services", "azure", "microsoft azure", "gcp", "google cloud platform",
            "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins", "github actions",
            "gitlab ci", "ci/cd", "circleci", "argo cd", "helm", "linux", "ubuntu", "centos",
            "debian", "nginx", "apache", "prometheus", "grafana", "datadog", "splunk", "elk stack",
            "serverless", "aws lambda", "cloudformation", "ec2", "s3", "rds", "iam", "cloudwatch",
            "eks", "ecs", "fargate", "kafka", "rabbitmq", "celery", "sqs", "sns"
        ],
        "ai_ml_data": [
            "machine learning", "deep learning", "artificial intelligence", "natural language processing",
            "nlp", "computer vision", "llm", "large language models", "generative ai", "genai",
            "rag", "retrieval-augmented generation", "vector search", "embeddings", "prompt engineering",
            "fine-tuning", "bert", "gpt", "reinforcement learning", "feature engineering", "mlops",
            "data pipelines", "etl", "data analysis", "data science", "data modeling", "spark", "hadoop",
            "airflow", "dbt", "databricks", "power bi", "tableau"
        ],
        "architecture_methodologies": [
            "rest api", "restful apis", "restful api", "rest", "microservices", "system design",
            "software architecture", "event-driven architecture", "domain-driven design", "ddd",
            "object-oriented programming", "oop", "functional programming", "design patterns",
            "solid principles", "agile", "scrum", "kanban", "sprint planning", "test-driven development",
            "tdd", "behavior-driven development", "bdd", "code review", "peer review", "continuous integration",
            "continuous deployment", "scalability", "high availability", "distributed systems",
            "security", "authentication", "authorization", "jwt", "oauth", "oauth2", "rbac", "cors",
            "api security", "owasp", "mvc", "mvvm"
        ],
        "tools_platforms": [
            "git", "github", "gitlab", "bitbucket", "jira", "confluence", "trello", "postman",
            "swagger", "openapi", "insomnia", "vs code", "visual studio", "intellij", "pycharm",
            "docker desktop", "vite", "webpack", "npm", "yarn", "pnpm", "pip", "poetry", "conda",
            "virtualenv", "pipenv", "linux cli", "bash scripting", "powershell"
        ],
        "soft_skills": [
            "communication", "written communication", "verbal communication", "leadership",
            "teamwork", "collaboration", "cross-functional collaboration", "problem solving",
            "analytical thinking", "critical thinking", "adaptability", "flexibility",
            "time management", "project management", "mentorship", "mentoring", "code mentoring",
            "decision making", "stakeholder management", "presentation skills", "self-motivated",
            "work ethic", "attention to detail", "creativity", "conflict resolution", "negotiation"
        ],
        "certifications": [
            "aws certified solutions architect", "aws certified developer", "aws certified cloud practitioner",
            "aws certified sysops administrator", "aws certified devops engineer",
            "azure fundamentals", "azure solutions architect", "azure developer associate",
            "google cloud certified associate cloud engineer", "google cloud certified professional cloud architect",
            "certified kubernetes administrator", "cka", "certified kubernetes application developer", "ckad",
            "pmp", "project management professional", "scrum master", "csm", "psm i",
            "cissp", "comptia security+", "comptia network+", "ceh", "certified ethical hacker"
        ]
    }

    # Flattened master lookup list
    ALL_CANONICAL_SKILLS: List[str] = []

    @classmethod
    def get_all_skills(cls) -> List[str]:
        if not cls.ALL_CANONICAL_SKILLS:
            seen = set()
            for cat, items in cls.CATEGORIES.items():
                for item in items:
                    if item not in seen:
                        seen.add(item)
                        cls.ALL_CANONICAL_SKILLS.append(item)
        return cls.ALL_CANONICAL_SKILLS

    @classmethod
    def extract_skills_from_text(cls, text: str) -> Dict[str, List[str]]:
        """
        Extracts and categorizes all skills detected in given text with word boundary matching.
        """
        if not text:
            return {cat: [] for cat in cls.CATEGORIES}

        text_lower = text.lower()
        extracted: Dict[str, List[str]] = {cat: [] for cat in cls.CATEGORIES}
        found_set: Set[str] = set()

        for category, skills in cls.CATEGORIES.items():
            for skill in skills:
                # Skill boundary regex handling special chars like C++, C#, .NET
                pattern = r'(?:\b|(?<=[\s,;:(/]))' + re.escape(skill) + r'(?:\b|(?=[\s,;:)/.]))'
                if re.search(pattern, text_lower):
                    display_name = cls._format_skill_name(skill)
                    if display_name not in found_set:
                        found_set.add(display_name)
                        extracted[category].append(display_name)

        return extracted

    @classmethod
    def extract_flat_skill_list(cls, text: str) -> List[str]:
        """Extract a deduplicated flat list of display-formatted skills from text."""
        by_cat = cls.extract_skills_from_text(text)
        all_skills = []
        for items in by_cat.values():
            all_skills.extend(items)
        return sorted(list(set(all_skills)))

    @classmethod
    def analyze_skill_evidence(cls, skill: str, resume_parsed: Dict[str, Any], raw_resume: str) -> Dict[str, Any]:
        """
        Determines evidence level for a specific skill in candidate resume:
        - demonstrated_work: Mentioned in work experience responsibilities / roles
        - demonstrated_project: Mentioned in projects / tech stack
        - mentioned: Listed in skills section or raw resume text
        - not_found: Absent
        """
        skill_norm = TechnicalTokenizer.normalize_skill(skill)
        skill_lower = skill.lower()

        # Check work experience
        exp_list = resume_parsed.get("experience", [])
        for exp in exp_list:
            exp_text = ""
            if isinstance(exp, dict):
                exp_text = f"{exp.get('role', '')} {exp.get('company', '')} {' '.join(exp.get('responsibilities', []))} {' '.join(exp.get('technologies', []))}"
            elif isinstance(exp, str):
                exp_text = exp

            if skill_lower in exp_text.lower() or skill_norm in exp_text.lower():
                return {
                    "level": "demonstrated_work",
                    "label": "Professional Work Experience",
                    "weight_multiplier": 1.0,
                    "evidence": exp_text[:120].strip()
                }

        # Check projects
        proj_list = resume_parsed.get("projects", [])
        for proj in proj_list:
            proj_text = ""
            if isinstance(proj, dict):
                proj_text = f"{proj.get('name', '')} {proj.get('description', '')} {' '.join(proj.get('responsibilities', []))} {' '.join(proj.get('technologies', []))}"
            elif isinstance(proj, str):
                proj_text = proj

            if skill_lower in proj_text.lower() or skill_norm in proj_text.lower():
                return {
                    "level": "demonstrated_project",
                    "label": "Project Implementation",
                    "weight_multiplier": 0.85,
                    "evidence": proj_text[:120].strip()
                }

        # Check skills section
        skills_data = resume_parsed.get("skills", {})
        skills_text = str(skills_data).lower()
        if skill_lower in skills_text or skill_norm in skills_text or skill_lower in raw_resume.lower():
            return {
                "level": "mentioned",
                "label": "Listed in Skills",
                "weight_multiplier": 0.65,
                "evidence": f"Skill listed: {skill}"
            }

        return {
            "level": "not_found",
            "label": "Missing / Not Found",
            "weight_multiplier": 0.0,
            "evidence": "No evidence found in resume"
        }

    @staticmethod
    def _format_skill_name(skill: str) -> str:
        """Format skill name with correct casing for industry standard."""
        specials = {
            "c++": "C++",
            "c#": "C#",
            "c": "C",
            "r": "R",
            ".net": ".NET",
            ".net core": ".NET Core",
            "asp.net": "ASP.NET",
            "node.js": "Node.js",
            "react.js": "React.js",
            "next.js": "Next.js",
            "vue.js": "Vue.js",
            "nuxt.js": "Nuxt.js",
            "express.js": "Express.js",
            "ci/cd": "CI/CD",
            "rest api": "REST API",
            "restful apis": "RESTful APIs",
            "restful api": "RESTful API",
            "rest": "REST",
            "graphql": "GraphQL",
            "sql": "SQL",
            "nosql": "NoSQL",
            "html": "HTML",
            "html5": "HTML5",
            "css": "CSS",
            "css3": "CSS3",
            "aws": "AWS",
            "gcp": "GCP",
            "azure": "Azure",
            "mysql": "MySQL",
            "postgresql": "PostgreSQL",
            "mongodb": "MongoDB",
            "sqlite": "SQLite",
            "redis": "Redis",
            "dynamodb": "DynamoDB",
            "elasticsearch": "Elasticsearch",
            "chromadb": "ChromaDB",
            "pinecone": "Pinecone",
            "fastapi": "FastAPI",
            "django": "Django",
            "flask": "Flask",
            "pytorch": "PyTorch",
            "tensorflow": "TensorFlow",
            "scikit-learn": "Scikit-Learn",
            "pandas": "Pandas",
            "numpy": "NumPy",
            "pytest": "PyTest",
            "docker": "Docker",
            "kubernetes": "Kubernetes",
            "terraform": "Terraform",
            "ansible": "Ansible",
            "jenkins": "Jenkins",
            "github actions": "GitHub Actions",
            "gitlab ci": "GitLab CI",
            "jwt": "JWT",
            "oauth": "OAuth",
            "oauth2": "OAuth2",
            "rbac": "RBAC",
            "pmp": "PMP",
            "cka": "CKA",
            "ckad": "CKAD",
            "cissp": "CISSP",
            "llm": "LLMs",
            "large language models": "Large Language Models",
            "generative ai": "Generative AI",
            "genai": "GenAI",
            "rag": "RAG",
            "nlp": "NLP",
            "mlops": "MLOps"
        }

        s_lower = skill.strip().lower()
        if s_lower in specials:
            return specials[s_lower]

        return skill.title()
