import sys
import unittest
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app.main import app
from app.services.deterministic.experience_calculator import ExperienceCalculator
from app.services.deterministic.skills_analyzer import SkillsAnalyzer
from app.services.deterministic.education_verifier import EducationVerifier
from app.services.deterministic.deterministic_scorer import DeterministicScorer
from app.services.ats.ats_scoring_service import ATSScoringService

class TestEdgeCasesAndEndToEnd(unittest.TestCase):

    def test_case_1_fresh_grad_on_senior_jd(self):
        """Case 1: Fresh Graduate with zero professional experience vs Senior 5+ yr JD."""
        parsed_resume = {
            "personal_info": {"name": "Alex Fresh", "email": "alex@example.com"},
            "skills": {"programming_languages": ["Python", "HTML", "CSS"]},
            "experience": [],
            "education": [{"degree": "B.S. in Computer Science", "institution": "State Univ"}]
        }
        parsed_jd = {
            "job_info": {"title": "Senior Backend Architect", "experience_required": "5+ years of experience"},
            "skills": {"required_skills": ["Python", "FastAPI", "Kubernetes", "AWS", "Distributed Systems"]}
        }
        raw_resume = "Alex Fresh. Email: alex@example.com. Skills: Python, HTML, CSS. Education: B.S. in Computer Science."
        raw_jd = "Senior Backend Architect. 5+ years of experience required. Must know Python, FastAPI, Kubernetes, AWS."

        res = DeterministicScorer.run_full_deterministic_analysis(
            parsed_resume, parsed_jd, raw_resume, raw_jd, {}, {}
        )

        # Experience score MUST be 0.0%
        self.assertEqual(res["experience"]["experience_score"], 0.0)
        self.assertEqual(res["experience"]["candidate_relevant_years"], 0.0)
        # Skills score must be low due to missing required skills
        self.assertLess(res["skills"]["skill_score"], 60.0)
        # Overall deterministic score must reflect significant gaps
        self.assertLess(res["deterministic_score"], 50.0)

    def test_case_2_experienced_matching_candidate(self):
        """Case 2: 5.5 yrs experienced developer on matching JD."""
        parsed_resume = {
            "personal_info": {"name": "Sara Senior", "email": "sara@tech.com", "phone": "+1234567890"},
            "skills": {"programming_languages": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Git"]},
            "experience": [
                {
                    "role": "Senior Backend Engineer",
                    "company": "Cloud Corp",
                    "duration": "2019 - Present",
                    "responsibilities": ["Architected REST APIs using FastAPI and PostgreSQL", "Deployed microservices on AWS cloud"],
                    "technologies": ["Python", "FastAPI", "PostgreSQL", "AWS", "Docker"]
                }
            ],
            "projects": [
                {"name": "API Gateway", "description": "High throughput FastAPI microservices on AWS", "technologies": ["Python", "FastAPI", "AWS"]}
            ],
            "education": [{"degree": "B.Tech in Computer Science", "institution": "Tech Institute", "field": "Computer Science"}]
        }
        parsed_jd = {
            "job_info": {"title": "Senior Python Developer", "experience_required": "5 years"},
            "skills": {"required_skills": ["Python", "FastAPI", "PostgreSQL", "AWS"], "preferred_skills": ["Docker"]},
            "responsibilities": ["Architect REST APIs using FastAPI", "Deploy microservices on AWS"]
        }
        raw_resume = """Sara Senior. Senior Backend Engineer. Phone: +1234567890. Email: sara@tech.com.
Skills: Python, FastAPI, PostgreSQL, AWS, Docker, Git.
Experience: Senior Backend Engineer at Cloud Corp (2019 - Present). Architected scalable REST APIs using FastAPI and PostgreSQL. Deployed microservices on AWS.
Projects: API Gateway in FastAPI and AWS.
Education: B.Tech in Computer Science."""
        raw_jd = "Senior Python Developer. 5 years experience required. Tech stack: Python, FastAPI, PostgreSQL, AWS, Docker. Architect REST APIs and deploy microservices on AWS."

        res = DeterministicScorer.run_full_deterministic_analysis(
            parsed_resume, parsed_jd, raw_resume, raw_jd, {}, {}
        )

        # Experience score must be 100%
        self.assertEqual(res["experience"]["experience_score"], 100.0)
        # Skills score must be high
        self.assertGreaterEqual(res["skills"]["skill_score"], 85.0)
        # Overall deterministic score must be >= 75.0
        self.assertGreaterEqual(res["deterministic_score"], 75.0)

    def test_case_3_unrelated_candidate_marketing_on_backend_jd(self):
        """Case 3: Marketing Manager candidate on Backend Developer JD."""
        parsed_resume = {
            "personal_info": {"name": "Mark Marketer", "email": "mark@agency.com"},
            "skills": {"soft_skills": ["SEO", "Social Media", "Copywriting", "Campaign Management"]},
            "experience": [
                {
                    "role": "Marketing Specialist",
                    "company": "Ad Agency",
                    "duration": "2020 - 2023",
                    "responsibilities": ["Ran Facebook and Google Ads campaigns", "Increased social media reach"]
                }
            ],
            "education": [{"degree": "B.A. in Marketing", "institution": "Business School"}]
        }
        parsed_jd = {
            "job_info": {"title": "Lead Python Developer", "experience_required": "4 years"},
            "skills": {"required_skills": ["Python", "Django", "PostgreSQL", "Redis", "Docker", "CI/CD"]}
        }
        raw_resume = "Mark Marketer. Marketing Specialist 2020-2023. Social Media, Copywriting, Google Ads."
        raw_jd = "Lead Python Developer. 4 years required. Python, Django, PostgreSQL, Redis, Docker, CI/CD."

        res = DeterministicScorer.run_full_deterministic_analysis(
            parsed_resume, parsed_jd, raw_resume, raw_jd, {}, {}
        )

        # Skills score must be 0% (no technical overlap)
        self.assertEqual(len(res["skills"]["matched_skills"]), 0)
        self.assertLess(res["skills"]["skill_score"], 20.0)
        # Overall score must be very low
        self.assertLess(res["deterministic_score"], 35.0)

    def test_case_4_full_pipeline_orchestration(self):
        """Case 4: Full ATSScoringService execution produces consensus, comparison table, and roadmap."""
        parsed_resume = {
            "personal_info": {"name": "Dev User", "email": "dev@test.com"},
            "skills": {"programming_languages": ["Python", "SQL", "Git", "REST API"]},
            "experience": [
                {"role": "Backend Engineer", "company": "Dev Co", "duration": "2022 - 2024", "responsibilities": ["Built REST APIs"]}
            ],
            "education": [{"degree": "B.S. in Software Engineering", "institution": "State Univ"}]
        }
        parsed_jd = {
            "job_info": {"title": "Python Developer", "experience_required": "2 years"},
            "skills": {"required_skills": ["Python", "PostgreSQL", "Docker"], "preferred_skills": ["Redis"]},
            "responsibilities": ["Build maintainable REST APIs", "Manage Docker container deployments"]
        }
        raw_resume = "Dev User. Backend Engineer. 2022-2024. Python, SQL, REST API, Git. B.S. Software Engineering."
        raw_jd = "Python Developer. 2 years experience. Python, PostgreSQL, Docker, Redis. Build REST APIs and Docker containers."

        report = ATSScoringService.compute_full_ats_report(
            parsed_resume, parsed_jd, raw_resume, raw_jd, {}, {}
        )

        self.assertIn("overall_score", report)
        self.assertIn("job_fit", report)
        self.assertIn("comparison_table", report)
        self.assertIn("learning_roadmap", report)
        self.assertIn("responsibility_analysis", report)
        self.assertGreater(len(report["comparison_table"]), 5)
        self.assertGreater(len(report["learning_roadmap"]), 0)

if __name__ == '__main__':
    unittest.main()
