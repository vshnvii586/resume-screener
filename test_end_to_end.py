import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import docx
import io
import json

from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

class DummyInteraction:
    def __init__(self, text):
        self.text = text

class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.jd_text = """
        Job Title: Senior Python Developer
        Requirements:
        - 5+ years of experience
        - Python
        - SQL
        - Docker
        - Bachelor's degree
        """
        
        resume_text = """
        Alice Smith
        Senior Python Developer
        
        EXPERIENCE
        Senior Python Developer
        Tech Corp
        Jan 2018 - Present
        - Wrote Python and SQL code. Managed Docker containers.
        
        EDUCATION
        Bachelor of Science in Computer Science
        
        SKILLS
        Python, SQL, Docker
        """
        doc = docx.Document()
        for line in resume_text.split("\n"):
            doc.add_paragraph(line)
        doc_stream = io.BytesIO()
        doc.save(doc_stream)
        self.valid_docx_bytes = doc_stream.getvalue()

    @patch("backend.ai_layer.gemini.os.getenv")
    @patch("backend.ai_layer.gemini.genai.Client")
    def test_e2e_successful_gemini_path(self, mock_client_class, mock_getenv):
        mock_getenv.return_value = "fake_key"
        mock_client = MagicMock()
        mock_models = MagicMock()
        
        # Valid AI semantic response
        valid_json = '''
        {
          "required_skill_match": {"matched": ["Python", "SQL", "Docker"], "missing": []},
          "preferred_skill_match": {"matched": [], "missing": []},
          "experience_match": {"meets_requirement": true, "assessment": "Has 6 years of experience"},
          "education_match": {"meets_requirement": true, "assessment": "Has Bachelor's degree"},
          "summary": "Excellent candidate."
        }
        '''
        mock_models.generate_content.return_value = DummyInteraction(valid_json)
        mock_client.models = mock_models
        mock_client_class.return_value = mock_client
        
        response = client.post(
            "/api/analyze",
            data={"job_description": self.jd_text},
            files={"file": ("resume.docx", self.valid_docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertFalse(data["used_fallback"])
        self.assertEqual(data["overall_score"], 100.0)
        self.assertEqual(data["summary"], "Excellent candidate.")
        
        # Verify exactly ONE Gemini call
        mock_models.generate_content.assert_called_once()
        call_kwargs = mock_models.generate_content.call_args[1]
        self.assertIn("Alice Smith", call_kwargs["contents"])
        self.assertIn("Senior Python Developer", call_kwargs["contents"])

    @patch("backend.ai_layer.gemini.os.getenv")
    @patch("backend.ai_layer.gemini.genai.Client")
    def test_e2e_gemini_timeout_fallback_path(self, mock_client_class, mock_getenv):
        mock_getenv.return_value = "fake_key"
        mock_client = MagicMock()
        mock_models = MagicMock()
        import asyncio
        mock_models.generate_content.side_effect = asyncio.TimeoutError("Timeout!")
        mock_client.models = mock_models
        mock_client_class.return_value = mock_client
        
        response = client.post(
            "/api/analyze",
            data={"job_description": self.jd_text},
            files={"file": ("resume.docx", self.valid_docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        # Should gracefully fall back
        self.assertTrue(data["used_fallback"])
        self.assertIn("[FALLBACK MODE]", data["summary"])
        # Should still score highly due to deterministic parsing
        self.assertEqual(data["overall_score"], 75.0)
        
        mock_models.generate_content.assert_called_once()

    def test_e2e_extractor_failure(self):
        # Invalid file format
        response = client.post(
            "/api/analyze",
            data={"job_description": self.jd_text},
            files={"file": ("resume.txt", b"just text", "text/plain")}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid file type", response.json()["detail"])

    @patch("backend.engine.gate.process_deterministic")
    @patch("backend.ai_layer.gemini.os.getenv")
    @patch("backend.ai_layer.gemini.genai.Client")
    def test_e2e_deterministic_failure(self, mock_client_class, mock_getenv, mock_det):
        # Mock successful AI
        mock_getenv.return_value = "fake_key"
        mock_client = MagicMock()
        mock_models = MagicMock()
        mock_models.generate_content.return_value = DummyInteraction('{"required_skill_match": {"matched": [], "missing": []}, "preferred_skill_match": {"matched": [], "missing": []}, "experience_match": {"meets_requirement": true, "assessment": ""}, "education_match": {"meets_requirement": true, "assessment": ""}, "summary": ""}')
        mock_client.models = mock_models
        mock_client_class.return_value = mock_client
        
        # Force deterministic layer to crash
        mock_det.side_effect = Exception("Math Error!")
        
        response = client.post(
            "/api/analyze",
            data={"job_description": self.jd_text},
            files={"file": ("resume.docx", self.valid_docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        
        self.assertEqual(response.status_code, 500)
        self.assertIn("Math Error!", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
