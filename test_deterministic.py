import unittest
import asyncio

from backend.deterministic.gate import process_deterministic

class TestDeterministicLayer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.extraction_result = {
            "resume": {
                "name": "Jane Doe",
                "skills": {"technical": ["Python", "SQL"], "soft": ["Communication"]},
                "experience": [],
                "education": [{"degree": "Bachelor of Science", "institution": "State Univ"}],
                "total_years_experience": "4 years",
                "raw_text": "Python SQL Communication 4 years Bachelor of Science"
            },
            "job_description": {
                "job_title": "Data Engineer",
                "required_skills": ["Python", "SQL", "AWS"],
                "preferred_skills": ["Docker"],
                "required_experience": "3+ years",
                "education": ["Bachelor's degree"]
            }
        }
        
        self.valid_ai_result = {
            "status": "success",
            "data": {
                "required_skill_match": {
                    "matched": ["Python", "SQL"],
                    "missing": ["AWS"]
                },
                "preferred_skill_match": {
                    "matched": [],
                    "missing": ["Docker"]
                },
                "experience_match": {
                    "meets_requirement": True,
                    "assessment": "Has 4 years of experience."
                },
                "education_match": {
                    "meets_requirement": True,
                    "assessment": "Has a Bachelor's degree."
                },
                "summary": "Solid candidate."
            }
        }
        
        self.invalid_ai_result = {
            "status": "error",
            "error_type": "TIMEOUT",
            "message": "Timed out",
            "data": None
        }

    async def test_successful_ai_path(self):
        result = await process_deterministic(self.extraction_result, self.valid_ai_result)
        
        self.assertEqual(result["status"], "success")
        self.assertFalse(result["used_fallback"])
        
        # Test Scoring
        # Required skills: 2/3 matched = 66.66% * 0.50 = 33.33 -> 33.3
        # Preferred skills: 0/1 matched = 0%
        # Experience: Meets = 100% * 0.25 = 25.0
        # Education: Meets = 100% * 0.15 = 15.0
        # Total: 33.3 + 25.0 + 15.0 = 73.3
        self.assertAlmostEqual(result["overall_score"], 73.3, places=1)
        self.assertEqual(result["score_breakdown"]["required_skills"]["matched"], 2)
        
    async def test_fallback_path(self):
        result = await process_deterministic(self.extraction_result, self.invalid_ai_result)
        
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["used_fallback"])
        
        # Fallback should do a decent job matching Python and SQL, finding the experience and education.
        # Required matched: Python, SQL
        self.assertIn("Python", result["required_skill_match"]["matched"])
        self.assertIn("SQL", result["required_skill_match"]["matched"])
        self.assertIn("AWS", result["required_skill_match"]["missing"])
        
        self.assertTrue(result["experience_match"]["meets_requirement"])
        self.assertTrue(result["education_match"]["meets_requirement"])

    async def test_malformed_ai_data(self):
        malformed_result = {
            "status": "success",
            "data": {
                "summary": "I forgot the other fields"
            }
        }
        result = await process_deterministic(self.extraction_result, malformed_result)
        
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["used_fallback"])
        self.assertIn("[FALLBACK MODE]", result["summary"])

    async def test_zero_skills(self):
        extraction = {
            "resume": self.extraction_result["resume"],
            "job_description": {
                "job_title": "No Skills Needed",
                "required_skills": [],
                "preferred_skills": [],
                "required_experience": "",
                "education": []
            }
        }
        
        # AI Result reflecting empty requirements
        ai_res = {
            "status": "success",
            "data": {
                "required_skill_match": {"matched": [], "missing": []},
                "preferred_skill_match": {"matched": [], "missing": []},
                "experience_match": {"meets_requirement": True, "assessment": "None needed"},
                "education_match": {"meets_requirement": True, "assessment": "None needed"},
                "summary": "Easy"
            }
        }
        
        result = await process_deterministic(extraction, ai_res)
        
        self.assertEqual(result["status"], "success")
        # Since requirements are empty, ratio = 1.0. 
        # required(50) + pref(10) + exp(25) + edu(15) = 100
        self.assertEqual(result["overall_score"], 100.0)

    async def test_scoring_math(self):
        from backend.deterministic.scorer import calculate_match_score
        
        job_profile = {
            "required_skills": ["A", "B", "C", "D"],
            "preferred_skills": ["E", "F"],
            "required_experience": "3 years",
            "education": ["Bachelor's"]
        }
        
        # All perfect
        perfect_match = {
            "required_skill_match": {"matched": ["A", "B", "C", "D"]},
            "preferred_skill_match": {"matched": ["E", "F"]},
            "experience_match": {"meets_requirement": True},
            "education_match": {"meets_requirement": True}
        }
        score = calculate_match_score(perfect_match, job_profile)
        self.assertEqual(score["overall_score"], 100.0)
        
        # Zero perfect
        zero_match = {
            "required_skill_match": {"matched": []},
            "preferred_skill_match": {"matched": []},
            "experience_match": {"meets_requirement": False},
            "education_match": {"meets_requirement": False}
        }
        score = calculate_match_score(zero_match, job_profile)
        self.assertEqual(score["overall_score"], 0.0)
        
        # Partial skills (2/4 req = 50%, 1/2 pref = 50%) -> 25 + 0 + 0 + 5 = 30
        partial_match = {
            "required_skill_match": {"matched": ["A", "B"]},
            "preferred_skill_match": {"matched": ["E"]},
            "experience_match": {"meets_requirement": False},
            "education_match": {"meets_requirement": False}
        }
        score = calculate_match_score(partial_match, job_profile)
        self.assertEqual(score["overall_score"], 30.0)

if __name__ == "__main__":
    unittest.main()
