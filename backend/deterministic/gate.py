from .fallback import generate_fallback_match
from .scorer import calculate_match_score
from backend.observability import cli

def _validate_ai_result(ai_result: dict) -> bool:
    if not ai_result or not isinstance(ai_result, dict):
        return False
    if ai_result.get("status") != "success":
        return False
        
    data = ai_result.get("data")
    if not data or not isinstance(data, dict):
        return False
        
    # Check core structure
    required_keys = ["required_skill_match", "preferred_skill_match", "experience_match", "education_match", "summary"]
    for k in required_keys:
        if k not in data:
            return False
            
    if not isinstance(data["required_skill_match"], dict) or "matched" not in data["required_skill_match"]:
        return False
    if not isinstance(data["preferred_skill_match"], dict) or "matched" not in data["preferred_skill_match"]:
        return False
    if not isinstance(data["experience_match"], dict) or "meets_requirement" not in data["experience_match"]:
        return False
    if not isinstance(data["education_match"], dict) or "meets_requirement" not in data["education_match"]:
        return False
        
    return True

async def process_deterministic(extraction_result: dict, ai_result: dict) -> dict:
    """
    Public entry point for the Deterministic Layer.
    Orchestrates validation, fallback, and scoring.
    """
    try:
        resume_data = extraction_result.get("resume", {})
        jd_data = extraction_result.get("job_description", {})
        cli.log_stage("DETERMINISTIC", "Validating AI result")
        
        # Decide between AI and Fallback
        if _validate_ai_result(ai_result):
            cli.log_success("DETERMINISTIC", "AI result valid")
            semantic_result = ai_result["data"]
            used_fallback = False
        else:
            cli.log_warning("DETERMINISTIC", "AI result unavailable/invalid\n→ Activating deterministic fallback")
            cli.log_stage("FALLBACK", "Normalizing candidate skills\n→ Matching required skills\n→ Matching preferred skills\n→ Evaluating experience\n→ Evaluating education")
            
            semantic_result = generate_fallback_match(resume_data, jd_data)
            cli.log_success("FALLBACK", "Fallback analysis complete")
            used_fallback = True
            
        # Calculate scores
        score_data = calculate_match_score(semantic_result, jd_data)
        
        # Build the final standardized result
        final_result = {
            "status": "success",
            "overall_score": score_data["overall_score"],
            "score_breakdown": score_data["breakdown"],
            "required_skill_match": semantic_result["required_skill_match"],
            "preferred_skill_match": semantic_result["preferred_skill_match"],
            "experience_match": semantic_result["experience_match"],
            "education_match": semantic_result["education_match"],
            "summary": semantic_result["summary"],
            "candidate_profile": resume_data,
            "job_profile": jd_data,
            "used_fallback": used_fallback
        }
        cli.log_stage("RESULT", 
            f"Candidate:\n{resume_data.get('name') or 'Unknown'}\n\n"
            f"Job:\n{jd_data.get('job_title') or 'Unknown'}\n\n"
            f"Overall match:\n{score_data['overall_score']}%\n\n"
            f"Required:\n{len(semantic_result['required_skill_match']['matched'])}/{len(semantic_result['required_skill_match']['matched']) + len(semantic_result['required_skill_match']['missing'])}\n\n"
            f"Preferred:\n{len(semantic_result['preferred_skill_match']['matched'])}/{len(semantic_result['preferred_skill_match']['matched']) + len(semantic_result['preferred_skill_match']['missing'])}\n\n"
            f"Experience:\n{'PASS' if semantic_result['experience_match']['meets_requirement'] else 'FAIL'}\n\n"
            f"Education:\n{'PASS' if semantic_result['education_match']['meets_requirement'] else 'FAIL'}\n\n"
            f"Fallback:\n{'YES' if used_fallback else 'NO'}"
        )
        
        return final_result
    except Exception as e:
        return {
            "status": "error",
            "error_type": "DETERMINISTIC_PROCESSING_ERROR",
            "message": f"An error occurred during deterministic processing: {str(e)}",
            "data": None
        }
