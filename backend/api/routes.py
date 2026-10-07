import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel

from backend.extractor.gate import process_extraction
from backend.ai_layer.gate import analyze_with_ai
from backend.deterministic.gate import process_deterministic
from backend.deterministic.scorer import calculate_match_score

from backend.engine.gate import process_resume_analysis
from backend.observability import cli

router = APIRouter()

@router.post("/api/resumes/ai-parse")
async def api_parse_resume(file: UploadFile = File(...)):
    """
    Compatibility route for frontend resume parsing.
    Delegates to the modular Extractor Layer.
    """
    filename = file.filename
    file_extension = filename.split(".")[-1].lower() if "." in filename else ""
    
    if file_extension not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX files are supported.")
    
    file_bytes = await file.read()
    
    try:
        extraction_result = process_extraction(file_bytes, file_extension, "")
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract text from {filename}. The file might be corrupted or unreadable. Error: {str(e)}"
        )
        
    return {
        "filename": filename,
        "profile": extraction_result["resume"]
    }


class JobParseRequest(BaseModel):
    job_description: str

@router.post("/api/jobs/parse")
async def api_parse_job(request: JobParseRequest):
    """
    Compatibility route for frontend JD parsing.
    Delegates to the modular Extractor Layer.
    """
    try:
        extraction_result = process_extraction(b"", "", request.job_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {
        "profile": extraction_result["job_description"]
    }


class MatchRequest(BaseModel):
    candidate_profile: dict
    job_profile: dict

@router.post("/api/match")
async def api_match(request: MatchRequest):
    """
    Compatibility route for frontend matching.
    """
    extraction_result = {
        "resume": request.candidate_profile,
        "job_description": request.job_profile
    }
    
    ai_result = await analyze_with_ai(extraction_result)
    final_result = await process_deterministic(extraction_result, ai_result)
    
    if final_result.get("status") == "error":
        raise HTTPException(status_code=500, detail=final_result.get("message", "Matching failed"))
    
    match_obj = {
        "required_skill_match": final_result["required_skill_match"],
        "preferred_skill_match": final_result["preferred_skill_match"],
        "experience_match": final_result["experience_match"],
        "education_match": final_result["education_match"],
        "summary": final_result["summary"]
    }
    
    return {
        "match": match_obj,
        "used_fallback": final_result.get("used_fallback", False)
    }


class ScoreRequest(BaseModel):
    match_result: dict
    job_profile: dict

@router.post("/api/score")
async def api_score(request: ScoreRequest):
    """
    Compatibility route for frontend scoring.
    """
    score_res = calculate_match_score(request.match_result, request.job_profile)
    return score_res

@router.post("/api/analyze")
async def api_analyze_full(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    New unified endpoint that calls the full Engine pipeline.
    Expects both file and JD text in one request.
    """
    filename = file.filename
    file_extension = filename.split(".")[-1].lower() if "." in filename else ""
    if file_extension not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Invalid file type.")
        
    file_bytes = await file.read()
    
    cli.init_request()
    cli.log_header("🚀 ANALYSIS STARTED")
    cli.log_stage("API", f"POST /api/analyze\n→ Resume: {filename}\n→ Type: {file_extension.upper()}\n→ Size: {len(file_bytes)//1024} KB\n→ JD: {len(job_description)} characters")
    cli.start_timer("total_request")
    
    result = await process_resume_analysis(file_bytes, file_extension, job_description)
    if result.get("status") == "error":
        cli.log_error("API", result.get("message"))
        raise HTTPException(status_code=500, detail=result.get("message"))
        
    cli.stop_timer("total_request")
    cli.log_all_timings()
    cli.log_header("✓ ANALYSIS COMPLETE")
    return result
