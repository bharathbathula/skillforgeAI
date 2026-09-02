import sys
import unittest
import asyncio
sys.path.insert(0, '.')

from app.services.nlp.technical_tokenizer import TechnicalTokenizer
from app.services.nlp.skill_taxonomy import SkillTaxonomy
from app.services.deterministic.experience_calculator import ExperienceCalculator
from app.services.deterministic.skills_analyzer import SkillsAnalyzer
from app.services.deterministic.responsibility_matcher import ResponsibilityMatcher
from app.services.deterministic.education_verifier import EducationVerifier
from app.services.deterministic.keyword_matcher import KeywordMatcher
from app.services.deterministic.deterministic_scorer import DeterministicScorer
from app.services.consensus.model_normalizer import ModelNormalizer
from app.services.consensus.consensus_engine import ConsensusEngine

class TestMultiAIATSSuite(unittest.TestCase):

    def test_technical_tokenizer(self):
        """Verify preservation of C++, C#, .NET, Node.js, CI/CD, etc."""
        text = "Experienced in C++, C#, .NET, Node.js, React.js, CI/CD, and REST APIs."
        tokens = TechnicalTokenizer.tokenize_preserve_tech(text)
        self.assertIn("C++", tokens)
        self.assertIn("C#", tokens)
        self.assertIn(".NET", tokens)
        self.assertIn("Node.js", tokens)
        self.assertIn("React.js", tokens)
        self.assertIn("CI/CD", tokens)

    def test_experience_calculator_zero_experience(self):
        """Verify 0 experience against 5 yr requirement produces 0.0% (NEVER 100% or 50%)."""
        cand_exp = []
        job_info = {"title": "Senior Backend Engineer", "experience_required": "5+ years"}
        res = ExperienceCalculator.calculate(cand_exp, job_info, "No experience text", "5+ years required")
        self.assertEqual(res["experience_score"], 0.0)
        self.assertEqual(res["candidate_relevant_years"], 0.0)
        self.assertEqual(res["required_experience_years"], 5.0)

    def test_experience_calculator_partial_experience(self):
        """Verify 2.5 yrs against 5 yr requirement produces ~50%."""
        cand_exp = [
            {"role": "Backend Developer", "company": "Tech Corp", "duration": "2021 - 2023", "responsibilities": ["API dev"]}
        ]
        job_info = {"title": "Senior Engineer", "experience_required": "5 years"}
        res = ExperienceCalculator.calculate(cand_exp, job_info, "", "5 years of experience")
        self.assertGreaterEqual(res["experience_score"], 35.0)
        self.assertLessEqual(res["experience_score"], 65.0)

    def test_experience_calculator_full_match(self):
        """Verify 5 yrs against 5 yr requirement produces 100%."""
        cand_exp = [
            {"role": "Software Engineer", "company": "A", "duration": "2019 - 2024", "responsibilities": ["Backend services"]}
        ]
        job_info = {"title": "Senior Engineer", "experience_required": "5 years"}
        res = ExperienceCalculator.calculate(cand_exp, job_info, "", "5 years of experience")
        self.assertEqual(res["experience_score"], 100.0)

    def test_education_verifier_no_education(self):
        """Verify missing education produces 0.0% without fabricating degree."""
        res = EducationVerifier.verify([], {"education_required": "Bachelor's degree"}, "No degree mentioned", "Bachelor's required")
        self.assertEqual(res["education_score"], 0.0)
        self.assertEqual(res["match_status"], "No Education Credentials Detected")

    def test_education_verifier_valid_degree(self):
        """Verify valid CS degree produces 100%."""
        cand_edu = [{"degree": "B.Tech in Computer Science", "institution": "IIT", "field_of_study": "Computer Science"}]
        res = EducationVerifier.verify(cand_edu, {"education_required": "Bachelor's degree"}, "B.Tech Computer Science", "")
        self.assertEqual(res["education_score"], 100.0)

    def test_skills_analyzer_required_vs_preferred(self):
        """Verify required skills impact score more heavily than preferred."""
        parsed_resume = {"skills": {"programming_languages": ["Python", "SQL"]}}
        parsed_job = {"skills": {"required_skills": ["Python", "Kubernetes"], "preferred_skills": ["Redis"]}}
        res = SkillsAnalyzer.analyze(parsed_resume, parsed_job, "Python SQL", "Python Kubernetes Redis")
        self.assertIn("Python", res["matched_skills"])
        self.assertIn("Kubernetes", res["missing_skills"])
        self.assertLess(res["skill_score"], 80.0)

    def test_responsibility_matcher_itemized(self):
        """Verify individual responsibility evaluation returns match % and evidence."""
        parsed_job = {"responsibilities": ["Develop REST APIs in Python", "Manage Kubernetes clusters"]}
        parsed_resume = {
            "experience": [{"role": "Backend Developer", "responsibilities": ["Built REST APIs with Python and FastAPI"]}]
        }
        res = ResponsibilityMatcher.analyze(parsed_job, parsed_resume, "Built REST APIs with Python", "")
        self.assertEqual(len(res["evaluations"]), 2)
        self.assertGreater(res["evaluations"][0]["match_percentage"], res["evaluations"][1]["match_percentage"])

    def test_consensus_engine_reconciliation(self):
        """Verify consensus engine reconciles deterministic and AI model data."""
        det_data = {
            "deterministic_score": 75.0,
            "parameter_scores": {
                "overall_score": 75.0, "skill_score": 80.0, "experience_score": 70.0,
                "responsibility_score": 75.0, "keyword_score": 70.0, "technical_skills": 80.0,
                "soft_skills": 70.0, "education_score": 100.0, "semantic_score": 72.0
            },
            "skills": {"matched_skills": ["Python"], "missing_skills": ["AWS"]},
            "experience": {"candidate_relevant_years": 3.0, "required_experience_years": 4.0, "match_status": "Qualified"},
            "responsibilities": {"evaluations": []}
        }
        raw_gemini = {
            "provider_name": "Gemini", "status": "success", "overall_score": 80.0,
            "parameter_scores": {"overall_score": 80.0, "skill_score": 85.0, "experience_score": 75.0},
            "matched_skills": ["Python"], "missing_skills": ["AWS"], "strengths": ["Strong Python skill"]
        }
        raw_openai = {
            "provider_name": "OpenAI", "status": "success", "overall_score": 76.0,
            "parameter_scores": {"overall_score": 76.0, "skill_score": 80.0, "experience_score": 70.0},
            "matched_skills": ["Python"], "missing_skills": ["AWS"], "strengths": ["Solid foundation"]
        }
        raw_claude = {
            "provider_name": "Claude", "status": "unavailable", "overall_score": 50.0,
            "parameter_scores": {}, "matched_skills": [], "missing_skills": []
        }

        res = ConsensusEngine.reconcile(det_data, raw_gemini, raw_openai, raw_claude)
        self.assertGreaterEqual(res["overall_score"], 70.0)
        self.assertLessEqual(res["overall_score"], 85.0)
        self.assertEqual(len(res["comparison_table"]), 11)
        self.assertIn("learning_roadmap", res["consensus"])

if __name__ == '__main__':
    unittest.main()
