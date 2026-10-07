import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# We need a minimal app to test the router
from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

class TestApiIntegration(unittest.TestCase):

    @patch("backend.api.routes.process_extraction")
    def test_api_parse_resume(self, mock_extract):
        mock_extract.return_value = {"resume": {"name": "Mocked Profile"}}
        
        # FastAPI TestClient requires files dict for UploadFile
        response = client.post(
            "/api/resumes/ai-parse", 
            files={"file": ("test.pdf", b"fake_pdf_content", "application/pdf")}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["filename"], "test.pdf")
        self.assertEqual(data["profile"]["name"], "Mocked Profile")
        mock_extract.assert_called_once_with(b"fake_pdf_content", "pdf", "")

    @patch("backend.api.routes.process_extraction")
    def test_api_parse_job(self, mock_extract):
        mock_extract.return_value = {"job_description": {"job_title": "Mocked Job"}}
        
        response = client.post(
            "/api/jobs/parse",
            json={"job_description": "We need a Python developer."}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["profile"]["job_title"], "Mocked Job")
        mock_extract.assert_called_once_with(b"", "", "We need a Python developer.")

    @patch("backend.api.routes.analyze_with_ai")
    @patch("backend.api.routes.process_deterministic")
    def test_api_match(self, mock_det, mock_ai):
        mock_ai.return_value = {"status": "success"}
        mock_det.return_value = {
            "status": "success",
            "required_skill_match": {"matched": ["Python"], "missing": []},
            "preferred_skill_match": {"matched": [], "missing": []},
            "experience_match": {"meets_requirement": True, "assessment": "Good"},
            "education_match": {"meets_requirement": True, "assessment": "Good"},
            "summary": "Great match",
            "used_fallback": False
        }
        
        response = client.post(
            "/api/match",
            json={
                "candidate_profile": {"name": "Test"},
                "job_profile": {"job_title": "Test Job"}
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify it exactly matches the structure expected by frontend match.match
        self.assertIn("match", data)
        self.assertEqual(data["match"]["required_skill_match"]["matched"][0], "Python")
        self.assertEqual(data["match"]["summary"], "Great match")
        self.assertFalse(data["used_fallback"])

    @patch("backend.api.routes.calculate_match_score")
    def test_api_score(self, mock_score):
        mock_score.return_value = {"overall_score": 85.5, "breakdown": {}}
        
        response = client.post(
            "/api/score",
            json={
                "match_result": {"summary": "dummy"},
                "job_profile": {"title": "dummy"}
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["overall_score"], 85.5)

if __name__ == "__main__":
    unittest.main()
