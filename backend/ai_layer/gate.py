from .gemini import call_gemini_analysis

async def analyze_with_ai(extraction_result: dict) -> dict:
    """
    Public entry point for the AI Layer.
    Accepts structured extraction results (resume and JD JSON) and coordinates the AI analysis.
    
    Returns a standardized dictionary indicating SUCCESS or FAILURE:
    SUCCESS:
        {
            "status": "success",
            "data": { ... }
        }
    FAILURE:
        {
            "status": "error",
            "error_type": "...",
            "message": "...",
            "data": None
        }
    """
    return await call_gemini_analysis(extraction_result)
