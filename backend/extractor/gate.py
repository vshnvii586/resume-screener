from .resume_extractor import extract_resume
from .jd_extractor import extract_job_description

def process_extraction(resume_bytes: bytes, resume_ext: str, jd_text: str) -> dict:
    """
    Public entry point for the Extractor Module.
    Accepts resume file bytes, resume file extension, and raw job description text.
    Returns a dictionary containing structured JSON-like dicts for both the resume and the job description.
    """
    resume_profile = {}
    if resume_bytes and resume_ext:
        resume_profile = extract_resume(resume_bytes, resume_ext)
        
    jd_profile = {}
    if jd_text:
        jd_profile = extract_job_description(jd_text)
        
    return {
        "resume": resume_profile,
        "job_description": jd_profile
    }
