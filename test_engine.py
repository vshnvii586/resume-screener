import unittest
import asyncio
from unittest.mock import patch, MagicMock

from backend.engine.gate import process_resume_analysis

class TestEngine(unittest.IsolatedAsyncioTestCase):

    @patch("backend.engine.gate.process_extraction")
    @patch("backend.engine.gate.analyze_with_ai")
    @patch("backend.engine.gate.process_deterministic")
    async def test_full_successful_pipeline(self, mock_det, mock_ai, mock_ext):
        # Setup mocks
        mock_ext.return_value = {"mock": "extracted"}
        mock_ai.return_value = {"status": "success", "data": "ai_res"}
        mock_det.return_value = {"status": "success", "overall_score": 100}

        # Call engine
        result = await process_resume_analysis(b"test", "pdf", "job text")

        # Verify ordering and arguments
        mock_ext.assert_called_once_with(b"test", "pdf", "job text")
        mock_ai.assert_called_once_with({"mock": "extracted"})
        mock_det.assert_called_once_with({"mock": "extracted"}, {"status": "success", "data": "ai_res"})
        
        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["overall_score"], 100)

    @patch("backend.engine.gate.process_extraction")
    @patch("backend.engine.gate.analyze_with_ai")
    @patch("backend.engine.gate.process_deterministic")
    async def test_gemini_failure(self, mock_det, mock_ai, mock_ext):
        mock_ext.return_value = {"mock": "extracted"}
        
        # AI fails gracefully
        ai_failure = {"status": "error", "error_type": "TIMEOUT"}
        mock_ai.return_value = ai_failure
        
        # Deterministic successfully falls back
        mock_det.return_value = {"status": "success", "overall_score": 50, "used_fallback": True}

        result = await process_resume_analysis(b"test", "pdf", "job text")

        mock_ext.assert_called_once()
        mock_ai.assert_called_once()
        # Deterministic should STILL be called, receiving the error to handle fallback
        mock_det.assert_called_once_with({"mock": "extracted"}, ai_failure)
        
        # Final result is success because deterministic handled it
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["used_fallback"])

    @patch("backend.engine.gate.process_extraction")
    @patch("backend.engine.gate.analyze_with_ai")
    @patch("backend.engine.gate.process_deterministic")
    async def test_extractor_failure(self, mock_det, mock_ai, mock_ext):
        # Extractor raises an exception
        mock_ext.side_effect = Exception("Corrupt PDF")

        result = await process_resume_analysis(b"bad", "pdf", "job text")

        # Engine handles it
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "EXTRACTOR_ERROR")
        
        # AI and Deterministic MUST NOT be called
        mock_ai.assert_not_called()
        mock_det.assert_not_called()

    @patch("backend.engine.gate.process_extraction")
    @patch("backend.engine.gate.analyze_with_ai")
    @patch("backend.engine.gate.process_deterministic")
    async def test_deterministic_failure(self, mock_det, mock_ai, mock_ext):
        mock_ext.return_value = {"mock": "extracted"}
        mock_ai.return_value = {"status": "success"}
        # Deterministic raises an unexpected exception
        mock_det.side_effect = Exception("Math error")

        result = await process_resume_analysis(b"test", "pdf", "job text")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "DETERMINISTIC_ERROR")

if __name__ == "__main__":
    unittest.main()
