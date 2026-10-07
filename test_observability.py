import unittest
import os
import io
import sys
from unittest.mock import patch, MagicMock

from backend.observability import cli
from backend.api.routes import router
from fastapi.testclient import TestClient
from fastapi import FastAPI
from backend.engine.gate import process_resume_analysis

app = FastAPI()
app.include_router(router)
client = TestClient(app)

class TestObservability(unittest.TestCase):
    def setUp(self):
        self.held, sys.stdout = sys.stdout, io.StringIO()
        cli._req_id.set(None)
        
    def tearDown(self):
        sys.stdout = self.held

    def test_logging_can_be_disabled(self):
        with patch.dict(os.environ, {"CLI_DEBUG": "false"}):
            cli.init_request()
            cli.log_stage("TEST", "Should not print")
            output = sys.stdout.getvalue()
            self.assertEqual(output, "")

    def test_logging_can_be_enabled(self):
        with patch.dict(os.environ, {"CLI_DEBUG": "true"}):
            cli.init_request()
            cli.log_stage("TEST", "Should print")
            output = sys.stdout.getvalue()
            self.assertIn("[TEST]", output)
            self.assertIn("Should print", output)
            self.assertIn("[REQ ", output)

    def test_request_ids_appear(self):
        with patch.dict(os.environ, {"CLI_DEBUG": "true"}):
            req_id = cli.init_request()
            cli.log_info("TEST", "Message")
            output = sys.stdout.getvalue()
            self.assertIn(f"[REQ {req_id}]", output)

    def test_api_key_is_never_printed(self):
        with patch.dict(os.environ, {"CLI_DEBUG": "true", "GEMINI_API_KEY": "secret_key_123"}):
            cli.init_request()
            # If the API key is passed directly to log_info it will print, but we want to ensure
            # the business logic doesn't do it.
            # We can't perfectly test the absence of secrets in all future logs here, but we can verify our logger itself doesn't auto-log env vars.
            cli.log_info("TEST", "Safe message")
            output = sys.stdout.getvalue()
            self.assertNotIn("secret_key_123", output)
            
    def test_timing_information_is_logged(self):
        with patch.dict(os.environ, {"CLI_DEBUG": "true"}):
            cli.init_request()
            cli.start_timer("test_op")
            cli.stop_timer("test_op")
            cli.log_all_timings()
            output = sys.stdout.getvalue()
            self.assertIn("[PERFORMANCE]", output)
            self.assertIn("Test_op", output)
            self.assertIn("Total", output)

