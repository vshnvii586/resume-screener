import unittest
from unittest.mock import patch, MagicMock
import asyncio
import os
import json

from backend.ai_layer.gate import analyze_with_ai

class DummyInteraction:
    def __init__(self, text):
        self.text = text

class TestAILayer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.extraction_result = {
            "resume": {"name": "Test User"},
            "job_description": {"job_title": "Tester"}
        }

    @patch("backend.ai_layer.gemini.os.getenv")
    async def test_missing_api_key(self, mock_getenv):
        mock_getenv.return_value = None
        result = await analyze_with_ai(self.extraction_result)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "MISSING_API_KEY")

    @patch("backend.ai_layer.gemini.os.getenv")
    @patch("backend.ai_layer.gemini.genai.Client")
    async def test_successful_gemini_response(self, mock_client_class, mock_getenv):
        mock_getenv.return_value = "fake_key"
        
        mock_client = MagicMock()
        mock_interactions = MagicMock()
        
        # Valid JSON response from Gemini
        valid_json = '''
        {
          "required_skill_match": {"matched": ["Python"], "missing": []},
          "preferred_skill_match": {"matched": [], "missing": []},
          "experience_match": {"meets_requirement": true, "assessment": "Good"},
          "education_match": {"meets_requirement": true, "assessment": "Good"},
          "summary": "Great match"
        }
        '''
        mock_models = MagicMock()
        mock_models.generate_content.return_value = DummyInteraction(valid_json)
        mock_client.models = mock_models
        mock_client_class.return_value = mock_client
        
        result = await analyze_with_ai(self.extraction_result)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["summary"], "Great match")
        self.assertEqual(result["data"]["required_skill_match"]["matched"][0], "Python")
        
        # Exactly ONE Gemini call is made
        mock_models.generate_content.assert_called_once()
        
        # Verify the prompt passed to Gemini contains both resume and JD info
        call_args = mock_models.generate_content.call_args[1]
        self.assertIn("Test User", call_args["contents"])
        self.assertIn("Tester", call_args["contents"])

    @patch("backend.ai_layer.gemini.os.getenv")
    @patch("backend.ai_layer.gemini.genai.Client")
    async def test_api_exception(self, mock_client_class, mock_getenv):
        mock_getenv.return_value = "fake_key"
        mock_client = MagicMock()
        mock_models = MagicMock()
        mock_models.generate_content.side_effect = Exception("API overloaded")
        mock_client.models = mock_models
        mock_client_class.return_value = mock_client
        
        result = await analyze_with_ai(self.extraction_result)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "API_ERROR")
        self.assertIn("API overloaded", result["message"])
        
    @patch("backend.ai_layer.gemini.os.getenv")
    @patch("backend.ai_layer.gemini.asyncio.wait_for")
    async def test_timeout(self, mock_wait_for, mock_getenv):
        mock_getenv.return_value = "fake_key"
        mock_wait_for.side_effect = asyncio.TimeoutError()
        
        result = await analyze_with_ai(self.extraction_result)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "TIMEOUT")

    @patch("backend.ai_layer.gemini.os.getenv")
    @patch("backend.ai_layer.gemini.genai.Client")
    async def test_empty_response(self, mock_client_class, mock_getenv):
        mock_getenv.return_value = "fake_key"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = DummyInteraction("")
        mock_client_class.return_value = mock_client
        
        result = await analyze_with_ai(self.extraction_result)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "EMPTY_RESPONSE")

    @patch("backend.ai_layer.gemini.os.getenv")
    @patch("backend.ai_layer.gemini.genai.Client")
    async def test_malformed_json_response(self, mock_client_class, mock_getenv):
        mock_getenv.return_value = "fake_key"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = DummyInteraction("Here is the result: { invalid json")
        mock_client_class.return_value = mock_client
        
        result = await analyze_with_ai(self.extraction_result)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "INVALID_AI_OUTPUT")

    @patch("backend.ai_layer.gemini.os.getenv")
    @patch("backend.ai_layer.gemini.genai.Client")
    async def test_truncated_json_response(self, mock_client_class, mock_getenv):
        mock_getenv.return_value = "fake_key"
        mock_client = MagicMock()
        # Missing closing brace
        truncated_json = '{"required_skill_match": {"matched": ["Python"]}'
        mock_client.models.generate_content.return_value = DummyInteraction(truncated_json)
        mock_client_class.return_value = mock_client
        
        result = await analyze_with_ai(self.extraction_result)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "INVALID_AI_OUTPUT")
        self.assertIn("Failed to parse", result["message"])

if __name__ == "__main__":
    unittest.main()
