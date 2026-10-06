import logging
from backend.extractor.gate import process_extraction
from backend.ai_layer.gate import analyze_with_ai
from backend.deterministic.gate import process_deterministic
from backend.observability import cli

async def process_resume_analysis(resume_bytes: bytes, resume_ext: str, jd_text: str) -> dict:
    """
    Main Engine orchestration layer.
    Orchestrates the entire pipeline from raw inputs to the final standardized result.
    Safely handles errors from each layer without duplicating business logic.
    """
    try:
        cli.log_stage("ENGINE", "Starting analysis pipeline\n→ Calling Extractor Gate")
        # 1. Extractor Layer
        try:
            extraction_result = process_extraction(resume_bytes, resume_ext, jd_text)
        except Exception as e:
            return {
                "status": "error",
                "error_type": "EXTRACTOR_ERROR",
                "message": f"Failed to extract data: {str(e)}",
                "data": None
            }

        # 2. AI Layer
        cli.log_success("ENGINE", "Extractor complete\n→ Calling AI Layer Gate")
        try:
            ai_result = await analyze_with_ai(extraction_result)
        except Exception as e:
            # Catch unexpected AI layer crashes (though the AI layer itself should catch most)
            ai_result = {
                "status": "error",
                "error_type": "AI_LAYER_CRASH",
                "message": f"AI Layer encountered an unexpected error: {str(e)}",
                "data": None
            }

        # 3. Deterministic Layer (Handles AI validation, fallback, and scoring)
        cli.log_success("ENGINE", "AI Layer complete\n→ Calling Deterministic Gate")
        try:
            final_result = await process_deterministic(extraction_result, ai_result)
            cli.log_success("ENGINE", "Deterministic processing complete")
            return final_result
        except Exception as e:
            return {
                "status": "error",
                "error_type": "DETERMINISTIC_ERROR",
                "message": f"Deterministic layer failed: {str(e)}",
                "data": None
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error_type": "ENGINE_ERROR",
            "message": f"Engine encountered a critical error: {str(e)}",
            "data": None
        }
