import os
import io
import re
import json
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import PyPDF2
import docx

# Load environment variables from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

app = FastAPI(title="AI Resume Screening API")

# Configure CORS so the React frontend can communicate with this API
origins = [
    "http://localhost:5173",  # React frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


def analyze_resume_with_gemini(resume_text: str) -> str:
    """
    Helper function to send resume text to the Gemini API and ask it to extract key details.
    Returns the raw text response from the model.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured in the .env file."
        )
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Please analyze the following resume text and extract the candidate's details.
    
    You MUST return ONLY a valid JSON object matching the exact structure below.
    Do NOT include Markdown formatting.
    Do NOT include ```json fences.
    Do NOT include any explanations before or after the JSON.
    Use empty strings or empty arrays when information is not present.
    Do NOT invent information that is not present in the resume.
    Preserve useful details from the resume rather than summarizing them away.

    JSON Structure:
    {{
      "name": "",
      "email": "",
      "phone": "",
      "education": [
        {{
          "degree": "",
          "institution": "",
          "start_date": "",
          "end_date": ""
        }}
      ],
      "skills": {{
        "technical": [],
        "soft": []
      }},
      "experience": [
        {{
          "title": "",
          "company": "",
          "location": "",
          "start_date": "",
          "end_date": "",
          "details": []
        }}
      ],
      "projects": [
        {{
          "name": "",
          "description": "",
          "technologies": []
        }}
      ],
      "certifications": [
        {{
          "name": "",
          "issuer": "",
          "date": ""
        }}
      ]
    }}
    
    Resume Text:
    {resume_text}
    """
    
    try:
        interaction = client.interactions.create(
            model='gemini-3.8-flash',
            input=prompt,
        )
        return interaction.output_text
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to communicate with Gemini API: {str(e)}"
        )


def analyze_job_description_with_gemini(job_description_text: str) -> str:
    """
    Helper function to send job description text to the Gemini API and extract requirements.
    Returns the raw text response from the model.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured in the .env file."
        )
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Please analyze the following job description text and extract the core requirements.
    
    You MUST return ONLY a valid JSON object matching the exact structure below.
    Do NOT include Markdown formatting.
    Do NOT include ```json fences.
    Do NOT include any explanations before or after the JSON.
    Use empty strings or empty arrays when information is not present.
    Do NOT invent requirements that are not present.
    Distinguish required skills from preferred/nice-to-have skills when the JD makes that distinction.
    
    JSON Structure:
    {{
      "job_title": "",
      "required_skills": [],
      "preferred_skills": [],
      "required_experience": "",
      "education": [],
      "responsibilities": [],
      "certifications": []
    }}
    
    Job Description Text:
    {job_description_text}
    """
    
    try:
        interaction = client.interactions.create(
            model='gemini-3.8-flash',
            input=prompt,
        )
        return interaction.output_text
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to communicate with Gemini API: {str(e)}"
        )


def analyze_candidate_match_with_gemini(candidate_profile: dict, job_profile: dict) -> str:
    """
    Helper function to compare a candidate profile against a job profile using Gemini.
    Returns the raw text response from the model.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured in the .env file."
        )
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Please compare the following candidate profile against the job profile.
    
    You MUST return ONLY a valid JSON object matching the exact structure below.
    Do NOT include Markdown formatting.
    Do NOT include ```json fences.
    Do NOT include any explanations before or after the JSON.

    Guidelines:
    - Compare the candidate's evidence against the job requirements.
    - Match semantically related skills when the evidence supports that relationship. For example, "Adobe Photoshop" should match "Photoshop", but do not assume unrelated skills are equivalent.
    - Only mark a required or preferred skill as matched when the candidate profile contains reasonable evidence for it.
    - Do not invent candidate experience, skills, education, or certifications.
    - Treat required and preferred skills separately.
    - For experience, determine whether the candidate appears to satisfy the stated experience requirement using the candidate's actual experience information.
    - For education, determine whether the candidate's education satisfies the stated requirement.
    - Keep assessments concise and evidence-based.
    - If information is missing or ambiguous, say so rather than inventing it.
    - Do not produce an overall numerical score. Python will calculate that separately.
    
    JSON Structure:
    {{
      "required_skill_match": {{
        "matched": [],
        "missing": []
      }},
      "preferred_skill_match": {{
        "matched": [],
        "missing": []
      }},
      "experience_match": {{
        "meets_requirement": false,
        "assessment": ""
      }},
      "education_match": {{
        "meets_requirement": false,
        "assessment": ""
      }},
      "summary": ""
    }}
    
    Candidate Profile (JSON):
    {json.dumps(candidate_profile, indent=2)}
    
    Job Profile (JSON):
    {json.dumps(job_profile, indent=2)}
    """
    
    try:
        interaction = client.interactions.create(
            model='gemini-3.8-flash',
            input=prompt,
        )
        return interaction.output_text
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to communicate with Gemini API: {str(e)}"
        )


def extract_text_from_file_bytes(file_bytes: bytes, file_extension: str) -> str:
    """Helper function to extract text from PDF or DOCX bytes. Uses PyMuPDF for PDF, falling back to PyPDF2."""
    extracted_text = ""
    if file_extension == "pdf":
        try:
            import pymupdf
            pdf_document = pymupdf.open(stream=file_bytes, filetype="pdf")
            
            header_name = ""
            if len(pdf_document) > 0:
                first_page = pdf_document[0]
                blocks = first_page.get_text("blocks")
                # Sort blocks vertically
                sorted_blocks = sorted([b for b in blocks if len(b) >= 5], key=lambda b: b[1])
                
                reject_words = ["SUMMARY", "PROFILE", "EXPERIENCE", "EDUCATION", "SKILLS", "PROJECTS", "CERTIFICATIONS", 
                                "RESUME", "CV", "CURRICULUM", "VITAE", "OBJECTIVE", "PORTFOLIO", "GITHUB", "LINKEDIN",
                                "MANAGER", "ANALYST", "DEVELOPER", "ENGINEER", "SPECIALIST", "DIRECTOR", "CONSULTANT",
                                "BACHELOR", "MASTER", "BBA", "BS", "BA", "DEGREE"]
                
                for b in sorted_blocks:
                    # Look at blocks in top ~half of page ideally, but we rely on sorts
                    b_text = b[4].strip()
                    lines = [l.strip() for l in b_text.split('\n') if l.strip()]
                    found = False
                    for line in lines:
                        cleaned = re.sub(r'[^A-Za-z]', '', line).upper()
                        if not cleaned: continue
                        if "@" in line or line.startswith("(") or re.search(r'\d', line) or "http" in line.lower() or "www." in line.lower():
                            continue
                        if any(rw in line.upper() for rw in reject_words):
                            continue
                        words = line.split()
                        if 1 <= len(words) <= 4:
                            header_name = line
                            found = True
                            break
                    if found:
                        break
            
            for page in pdf_document:
                page_text = page.get_text()
                if page_text:
                    extracted_text += page_text + "\n"
            
            if extracted_text.strip():
                final_text = extracted_text.strip()
                if header_name and header_name not in final_text[:300]:
                    final_text = header_name + "\n" + final_text
                elif header_name:
                    # ensure it's at the very top for the parser
                    final_text = header_name + "\n" + final_text
                return final_text

        except Exception as e:
            print(f"[EXTRACT] PyMuPDF extraction failed: {e}. Falling back to PyPDF2.", flush=True)
            
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
        except Exception as e:
            raise Exception(f"PDF extraction failed on both PyMuPDF and PyPDF2: {str(e)}")
    elif file_extension == "docx":
        doc = docx.Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            extracted_text += para.text + "\n"
    return extracted_text.strip()


def parse_resume_text(text: str) -> dict:
    """
    Heuristically parses raw resume text into a structured candidate profile.
    """
    profile = {
        "name": "",
        "email": "",
        "phone": "",
        "education": [],
        "skills": {
            "technical": [],
            "soft": []
        },
        "experience": [],
        "projects": [],
        "certifications": []
    }
    
    # 1. Extract Email using Regex
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        profile["email"] = email_match.group(0)
        
    # 2. Extract Phone Number using improved Regex to handle spaces/hyphens
    # Matches: (212) 256 -1414, 212-256-1414, +1 212 256 1414, etc.
    phone_match = re.search(r'(?:\+?\d{1,3}[\s-]*)?\(?\d{3}\)?[\s-]*\d{3}[\s-]*\d{4}', text)
    if phone_match:
        profile["phone"] = phone_match.group(0).strip()
        
    # Split the text into lines, ignoring completely empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # 3. Filter out template boilerplate (e.g. "Dear Job Seeker")
    filtered_lines = []
    for line in lines:
        cleaned_line = re.sub(r'\s+', '', line).upper()
        if cleaned_line.startswith("DEARJOBSEEKER"):
            # Cut off the rest of the parsing to avoid pulling in template text
            break
        filtered_lines.append(line)
    lines = filtered_lines
    
    # 4. Generalized Name Extraction
    section_keywords = ["SUMMARY", "EXPERIENCE", "EDUCATION", "SKILL", "PROJECT", "CERTIFICATION", "OBJECTIVE", "PROFILE", "EMPLOYMENT", "WORK"]
    job_titles = ["ANALYST", "MANAGER", "ENGINEER", "SPECIALIST", "DEVELOPER", "DIRECTOR", "LEAD", "SENIOR", "JUNIOR", "COORDINATOR", "ASSOCIATE", "CONSULTANT"]
    
    # Scan early lines for a plausible person name
    for i in range(min(30, len(lines))):
        line = lines[i]
        line_upper = line.upper()
        
        # Skip obvious non-names
        if line == profile.get("email") or line == profile.get("phone"): continue
        if "@" in line or "HTTP" in line_upper or "WWW." in line_upper or "LINKEDIN" in line_upper or "GITHUB" in line_upper: continue
        
        # Skip section headings
        if any(kw in line_upper for kw in section_keywords): continue
        
        # Skip common job titles or generic header phrases
        if any(title in line_upper for title in job_titles): continue
        
        # Must be mostly letters and 1-4 words
        words = line.split()
        if 1 <= len(words) <= 4 and 0 < len(line) < 50:
            # Check if it contains mostly letters (allow spaces, hyphens, periods)
            if all(c.isalpha() or c in " \t-.'" for c in line) and any(c.isalpha() for c in line):
                profile["name"] = line
                break

    # 5. Identify Sections and Routes
    current_section = None
    
    # Map of compressed/cleaned keywords to their internal routing target
    # We add "CONTACT" and "SUMMARY" to prevent them from spilling into real sections
    section_map = {
        "EDUCATION": "education",
        "ACADEMICBACKGROUND": "education",
        "EDUCATIONANDTRAINING": "education",
        "SKILLS": "technical_skills",
        "TECHNICALSKILLS": "technical_skills",
        "CORECOMPETENCIES": "technical_skills",
        "SOFTSKILLS": "soft_skills",
        "EXPERIENCE": "experience",
        "WORKEXPERIENCE": "experience",
        "PROFESSIONALEXPERIENCE": "experience",
        "EMPLOYMENT": "experience",
        "WORKHISTORY": "experience",
        "PROJECTS": "projects",
        "CERTIFICATIONS": "certifications",
        "CONTACT": "contact",
        "SUMMARY": "summary",
        "PROFILE": "summary"
    }
    
    raw_experience_lines = []
    
    for line in lines:
        cleaned_line = re.sub(r'\s+', '', line).upper()
        
        is_header = False
        if len(cleaned_line) < 40:
            for keyword, section_name in section_map.items():
                if cleaned_line == keyword or cleaned_line.startswith(keyword + ":"):
                    current_section = section_name
                    is_header = True
                    break
        
        if is_header:
            continue
            
        # Append line to the active section
        if current_section == "education":
            # Protect against swallowing unrelated text
            edu_kws = ["bachelor", "master", "phd", "university", "college", "institute", "school", "b.a", "b.s", "degree", "diploma", "academy"]
            line_l = line.lower()
            if any(kw in line_l for kw in edu_kws) or any(c.isdigit() for c in line):
                profile["education"].append(line)
        elif current_section == "technical_skills":
            if line == profile.get("name") or line == profile.get("email") or line == profile.get("phone") or line.startswith("(") or "@" in line:
                continue
            # Handle comma, pipe, bullet separated skills
            split_chars = re.split(r'[,|•\-]', line)
            if len(split_chars) > 1:
                profile["skills"]["technical"].extend([s.strip() for s in split_chars if s.strip()])
            else:
                profile["skills"]["technical"].append(line)
        elif current_section == "soft_skills":
            if line == profile.get("name") or line == profile.get("email") or line == profile.get("phone") or line.startswith("(") or "@" in line:
                continue
            split_chars = re.split(r'[,|•\-]', line)
            if len(split_chars) > 1:
                profile["skills"]["soft"].extend([s.strip() for s in split_chars if s.strip()])
            else:
                profile["skills"]["soft"].append(line)
        elif current_section == "projects":
            profile["projects"].append(line)
        elif current_section == "certifications":
            profile["certifications"].append(line)
        elif current_section == "experience":
            raw_experience_lines.append(line)
            
    # 6. Post-process Experience into structured objects
    # Matches common date ranges like "May 2019 - Present", "2015 - 2019", "Aug 2017 – Apr 2019", "20XX - Present"
    date_range_pattern = re.compile(
        r'((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+)?(?:\d{4}|20XX))\s*[-–to]+\s*((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+)?(?:\d{4}|20XX)|Present|Current)', 
        re.IGNORECASE
    )
    
    exp_list = []
    current_job = None
    buffer_lines = []
    
    for line in raw_experience_lines:
        date_match = date_range_pattern.search(line)
        is_bullet = line.strip().startswith(('-', '•', '*', '▪'))
        
        if date_match:
            # We found a date range! This finalizes the header block for a job.
            title = buffer_lines[0] if len(buffer_lines) > 0 else "Role Unknown"
            comp_loc = buffer_lines[1] if len(buffer_lines) > 1 else ""
            
            company = comp_loc
            location = buffer_lines[2] if len(buffer_lines) > 2 else ""
            
            if not location and " - " in comp_loc:
                parts = comp_loc.split(" - ", 1)
                company = parts[0].strip()
                location = parts[1].strip()
            elif not location and ", " in comp_loc:
                parts = comp_loc.split(", ", 1)
                company = parts[0].strip()
                location = parts[1].strip()
                
            job = {
                "job_title": title,
                "company": company,
                "location": location,
                "start_date": date_match.group(1).strip(),
                "end_date": date_match.group(2).strip(),
                "details": []
            }
            exp_list.append(job)
            current_job = job
            buffer_lines = []
        elif is_bullet:
            if current_job:
                cleaned_bullet = re.sub(r'^[-•*▪]+\s*', '', line.strip())
                current_job["details"].append(cleaned_bullet)
            else:
                buffer_lines.append(line)
        else:
            if current_job:
                # Check for wrapped bullet text vs new job title
                # If it starts with a lowercase letter, it's almost certainly a wrapped sentence
                if len(line) > 0 and line[0].islower():
                    if current_job["details"]:
                        current_job["details"][-1] += " " + line.strip()
                    else:
                        current_job["details"].append(line.strip())
                else:
                    # Capitalized line without bullet - likely the start of the NEXT job title.
                    current_job = None
                    buffer_lines.append(line)
            else:
                buffer_lines.append(line)
                
    profile["experience"] = exp_list
            
    return profile


@app.get("/api/health")
def health_check():
    """
    A simple health check endpoint to confirm the backend is running.
    """
    return {"status": "ok", "message": "Backend is running successfully!"}


@app.post("/api/resumes/extract-text")
async def extract_resume_text(file: UploadFile = File(...)):
    """
    Accepts a PDF or DOCX file, extracts its text in memory, and returns it.
    """
    filename = file.filename
    file_extension = filename.split(".")[-1].lower() if "." in filename else ""
    
    if file_extension not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX files are supported.")
    
    file_bytes = await file.read()
    
    try:
        extracted_text = extract_text_from_file_bytes(file_bytes, file_extension)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract text from {filename}. The file might be corrupted or unreadable. Error: {str(e)}"
        )
        
    return {
        "filename": filename,
        "file_type": file_extension,
        "extracted_text": extracted_text,
        "character_count": len(extracted_text)
    }


@app.post("/api/resumes/parse")
async def parse_resume(file: UploadFile = File(...)):
    """
    Accepts a PDF or DOCX file, extracts its text, and parses it into a structured profile.
    """
    filename = file.filename
    file_extension = filename.split(".")[-1].lower() if "." in filename else ""
    
    if file_extension not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX files are supported.")
    
    file_bytes = await file.read()
    
    try:
        extracted_text = extract_text_from_file_bytes(file_bytes, file_extension)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract text from {filename}. The file might be corrupted or unreadable. Error: {str(e)}"
        )
        
    profile = parse_resume_text(extracted_text)
    
    return {
        "filename": filename,
        "profile": profile
    }



@app.post("/api/resumes/ai-parse")
async def ai_parse_resume(file: UploadFile = File(...)):
    """
    Accepts a PDF or DOCX file, extracts text, and uses Gemini to parse it into structured JSON.
    """
    filename = file.filename
    file_extension = filename.split(".")[-1].lower() if "." in filename else ""
    
    if file_extension not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX files are supported.")
    
    file_bytes = await file.read()
    

    
    try:
        extracted_text = extract_text_from_file_bytes(file_bytes, file_extension)
        
                
    except Exception as e:
        print(f"Extraction failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract text from {filename}. Error: {str(e)}"
        )
        
    if DEMO_MODE:
        raw_ai_response = create_demo_resume_analysis(extracted_text)
    else:
        # Send text to Gemini
        try:
            raw_ai_response = await asyncio.wait_for(
                asyncio.to_thread(
                    analyze_resume_with_gemini,
                    extracted_text
                ),
                timeout=60
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Gemini AI processing timed out after 60 seconds."
            )
    
    try:
        parsed_profile = json.loads(raw_ai_response)
        parsed_profile["raw_text"] = extracted_text
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="The AI returned invalid structured data that could not be parsed as JSON."
        )
        
    response_obj = {
        "filename": filename,
        "profile": parsed_profile
    }
    return response_obj


class JobDescriptionRequest(BaseModel):
    job_description: str

@app.post("/api/jobs/parse")
async def parse_job_description(request: JobDescriptionRequest):
    """
    Accepts raw job description text and uses Gemini to parse it into structured JSON.
    """
    raw_text = request.job_description.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")
        
    if DEMO_MODE:
        raw_ai_response = create_demo_job_analysis(raw_text)
    else:
        # Send text to Gemini
        raw_ai_response = analyze_job_description_with_gemini(raw_text)
    
    try:
        # Parse Gemini's JSON string into a Python dictionary
        parsed_profile = json.loads(raw_ai_response)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="The AI returned invalid structured data that could not be parsed as JSON."
        )
        
    
    return {
        "job_description": raw_text,
        "profile": parsed_profile
    }


class MatchRequest(BaseModel):
    candidate_profile: dict
    job_profile: dict

@app.post("/api/match")
async def match_candidate_to_job(request: MatchRequest):
    """
    Accepts a structured candidate profile and job profile, and uses Gemini to evaluate the match.
    """

    if DEMO_MODE:
        raw_ai_response = create_demo_match_result(request.candidate_profile, request.job_profile)
    else:
        raw_ai_response = analyze_candidate_match_with_gemini(
            candidate_profile=request.candidate_profile,
            job_profile=request.job_profile
        )
    
    try:
        parsed_match = json.loads(raw_ai_response)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="The AI returned invalid structured data that could not be parsed as JSON."
        )
        
    
    return {
        "candidate_profile": request.candidate_profile,
        "job_profile": request.job_profile,
        "match": parsed_match
    }


def calculate_match_score(match_result: dict, job_profile: dict) -> dict:
    """
    Deterministically calculates a match score based on AI match results.
    """
    required = job_profile.get("required_skills", [])
    matched_req = match_result.get("required_skill_match", {}).get("matched", [])
    
    if len(required) > 0:
        required_ratio = len(matched_req) / len(required)
    else:
        required_ratio = 1.0
        
    preferred = job_profile.get("preferred_skills", [])
    matched_pref = match_result.get("preferred_skill_match", {}).get("matched", [])
    
    if len(preferred) > 0:
        preferred_ratio = len(matched_pref) / len(preferred)
    else:
        preferred_ratio = 1.0
        
    experience_meets = match_result.get("experience_match", {}).get("meets_requirement", False)
    experience_ratio = 1.0 if experience_meets else 0.0
    
    education_meets = match_result.get("education_match", {}).get("meets_requirement", False)
    education_ratio = 1.0 if education_meets else 0.0
    
    overall_score = (
        (required_ratio * 0.50) +
        (experience_ratio * 0.25) +
        (education_ratio * 0.15) +
        (preferred_ratio * 0.10)
    ) * 100
    
    return {
        "overall_score": round(overall_score, 1),
        "breakdown": {
            "required_skills": {
                "score": round(required_ratio * 100, 1),
                "weight": 50
            },
            "experience": {
                "score": round(experience_ratio * 100, 1),
                "weight": 25
            },
            "education": {
                "score": round(education_ratio * 100, 1),
                "weight": 15
            },
            "preferred_skills": {
                "score": round(preferred_ratio * 100, 1),
                "weight": 10
            }
        }
    }


class ScoreRequest(BaseModel):
    match_result: dict
    job_profile: dict

@app.post("/api/score")
async def calculate_score_endpoint(request: ScoreRequest):
    """
    Calculates a deterministic numerical score based on the structured AI match.
    """
    print("========== BROWSER SCORE DEBUG START ==========")
    print(f"Match Result Incoming:\n{json.dumps(request.match_result, indent=2)}")
    score_res = calculate_match_score(request.match_result, request.job_profile)
    print(f"Final Score Result:\n{json.dumps(score_res, indent=2)}")
    print("========== BROWSER SCORE DEBUG END ==========")
    return score_res


@app.post("/api/debug/gemini")
async def debug_gemini_connection():
    """
    Temporary endpoint to diagnose Gemini API connectivity issues via FastAPI.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured in the .env file."
        )
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    def test_call():
        return client.interactions.create(
            model='gemini-3.8-flash',
            input="Reply with exactly the word: PONG"
        )
        
    print("[GEMINI-DEBUG] CALL START", flush=True)
    try:
        interaction = await asyncio.wait_for(
            asyncio.to_thread(test_call),
            timeout=30
        )
        response_text = interaction.output_text
    except asyncio.TimeoutError:
        print("[GEMINI-DEBUG] TIMEOUT", flush=True)
        raise HTTPException(
            status_code=504,
            detail="Gemini AI debug call timed out after 30 seconds."
        )
    except Exception as e:
        print(f"[GEMINI-DEBUG] ERROR: {str(e)}", flush=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to communicate with Gemini API: {str(e)}"
        )
        
    print("[GEMINI-DEBUG] CALL COMPLETE", flush=True)
    
    return {"response": response_text}


def create_demo_job_analysis(job_description_text: str) -> str:
    """
    Demo fallback for job description parsing without calling Gemini.
    Uses vocabulary matching and section heuristics.
    """
    import re
    import json
    
    profile = {
      "job_title": "",
      "required_skills": [],
      "preferred_skills": [],
      "required_experience": "",
      "education": [],
      "responsibilities": [],
      "certifications": []
    }
    
    lines = [line.strip() for line in job_description_text.split('\n') if line.strip()]
    if lines:
        profile["job_title"] = lines[0]
        
    vocab = [
        "Python", "Java", "JavaScript", "TypeScript", "React", "Node.js", "Node", 
        "HTML", "CSS", "SQL", "MongoDB", "PostgreSQL", "Docker", "AWS", "Git", 
        "Figma", "Photoshop", "Illustrator", "Adobe After Effects", "After Effects", 
        "Blender", "3D design", "Agile", "communication", "collaboration", 
        "branding", "visual communication", "motion graphics", "Adobe Certified Professional",
        "process improvement", "workflow optimization", "data analysis", "reporting", 
        "cross-functional stakeholder communication", "Microsoft Excel", "project management", 
        "Power BI", "Tableau", "report automation", "workflow automation", "CRM", 
        "vendor management", "budget tracking", "Excel"
    ]
    
    req_text = ""
    pref_text = ""
    other_text = ""
    
    current_section = "req"
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        is_bullet = line_clean.startswith(("-", "*", "•", "·", ""))
        lower_line = line_clean.lower()
        clean_lower = lower_line.rstrip(':').strip()
        
        new_section = None
        if not is_bullet and len(line_clean) <= 60:
            pref_exact = ["preferred qualifications", "preferred skills", "nice to have", "bonus", "preferred", "preferred experience"]
            req_exact = ["required qualifications", "required skills", "requirements", "qualifications", "skills", "experience", "education", "must have", "basic qualifications"]
            other_exact = ["responsibilities", "duties", "what you'll do", "what you will do"]
            
            if clean_lower in pref_exact:
                new_section = "pref"
            elif clean_lower in req_exact:
                new_section = "req"
            elif clean_lower in other_exact:
                new_section = "other"
            elif line_clean.endswith(":"):
                if any(kw in lower_line for kw in ["preferred", "nice to have", "bonus"]):
                    new_section = "pref"
                elif any(kw in lower_line for kw in ["require", "must have", "qualifications", "skills", "experience", "education"]):
                    new_section = "req"
                elif any(kw in lower_line for kw in ["responsibilit", "duties"]):
                    new_section = "other"
                    
        if new_section:
            current_section = new_section
            continue
            
        if current_section == "req":
            req_text += line + " "
        elif current_section == "pref":
            pref_text += line + " "
        else:
            other_text += line + " "
            
    if not req_text.strip() and not pref_text.strip():
        req_text = job_description_text

    skill_variants = {
        "communication": [r"\bcommunication\b", r"\bcommunicating\b", r"\bcommunicates\b", r"\bcommunicated\b"],
        "data analysis": [r"\bdata analysis\b", r"\bdata analytics\b", r"\banalyzing data\b", r"\banalyze data\b"],
        "reporting": [r"\breporting\b", r"\breports\b", r"\breport preparation\b", r"\bbusiness reporting\b"],
        "workflow optimization": [r"\bworkflow optimization\b", r"\bworkflow improvement\b", r"\bprocess/workflow optimization\b", r"\bprocess optimization\b"],
        "project management": [r"\bproject management\b", r"\bproject coordination\b", r"\bmanaging projects\b"],
        "cross-functional stakeholder communication": [
            r"\bcross-functional stakeholder communication\b",
            r"\bcross-functional[\w\s,-]+communicat\w*\b",
            r"\bcommunicat\w*[\w\s,-]+cross-functional\b"
        ],
        "workflow automation": [
            r"\bworkflow automation\b",
            r"\bautomat\w*[\w\s,-]+workflows\b",
            r"\bworkflow[\w\s,-]+automat\w*\b"
        ]
    }

    found_skills = set()
    for skill in vocab:
        skill_l = skill.lower()
        variants = skill_variants.get(skill_l, [r'\b' + re.escape(skill) + r'\b'])
        
        # Check required text
        matched_req = False
        for variant in variants:
            if re.search(variant, req_text, re.IGNORECASE):
                matched_req = True
                break
                
        if matched_req:
            profile["required_skills"].append(skill)
            found_skills.add(skill_l)
            continue
            
        # Check preferred text
        matched_pref = False
        for variant in variants:
            if re.search(variant, pref_text, re.IGNORECASE):
                matched_pref = True
                break
                
        if matched_pref:
            profile["preferred_skills"].append(skill)
            found_skills.add(skill_l)
            
    # Normalize skill lists to remove duplicates (like "Microsoft Excel" and "Excel")
    norm_map = {"excel": "Microsoft Excel", "ms excel": "Microsoft Excel", "after effects": "Adobe After Effects", "node": "Node.js"}
    def normalize_list(skill_list):
        res = []
        for s in skill_list:
            norm = norm_map.get(s.lower(), s)
            if norm not in res:
                res.append(norm)
        return res
        
    profile["required_skills"] = normalize_list(profile["required_skills"])
    profile["preferred_skills"] = normalize_list(profile["preferred_skills"])
            
    # Extract experience
    exp_match = re.search(r'((?:\d+)\+?\s*(?:years?|yrs?))', job_description_text, re.IGNORECASE)
    if exp_match:
        # Just use the matched text, cleaned up slightly, e.g. "3+ years"
        val = exp_match.group(1).replace("yrs", "years").strip()
        if "+" not in val and "years" in val:
            val = val.replace(" years", "+ years")
        profile["required_experience"] = val
        
    # Extract education
    edu_match = re.search(r"(Bachelor's degree[^.\n]*|Bachelor of [^.\n]*|Master's degree[^.\n]*|MBA|B\.Tech|M\.Tech|Degree in [^.\n]*)", job_description_text, re.IGNORECASE)
    if edu_match:
        profile["education"].append(edu_match.group(0).strip())
    cert_match = re.search(r"([\w\s]+Certification|Certified[\w\s]+|Adobe Certified[\w\s]+)", job_description_text, re.IGNORECASE)
    if cert_match:
        profile["certifications"].append(cert_match.group(0).strip())
        
    return json.dumps(profile)


def create_demo_resume_analysis(extracted_text: str) -> str:
    """
    Demo fallback for resume parsing without calling Gemini.
    Uses robust regex for education and experience.
    """
    import re
    import json
    
    # Start with the baseline deterministic parser we already wrote
    profile = parse_resume_text(extracted_text)
    
    # Extract total years of experience from summary if present
    exp_match = re.search(r'((?:\d+)\+?\s*(?:years?|yrs?))', extracted_text[:1000], re.IGNORECASE)
    if exp_match:
        val = exp_match.group(1).replace("yrs", "years").strip()
        profile["total_years_experience"] = val
    
    # 1. Remap 'job_title' to 'title' to match Gemini schema perfectly
    for exp in profile.get("experience", []):
        if "job_title" in exp:
            exp["title"] = exp.pop("job_title")
            
    # 2. Extract robust education if empty or unformatted
    lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
    
    has_edu = bool(profile.get("education"))
    is_string_format = has_edu and isinstance(profile["education"][0], str)
    
    if not has_edu or is_string_format:
        new_edu = []
        edu_keywords = r"\b(BFA|BA|BS|B\.S\.|B\.A\.|BBA|B\.Tech|M\.Tech|MBA|MS|MSc|MA|PhD|Bachelor's|Master's|Degree|Bachelor|Master)\b"
        
        for i, line in enumerate(lines):
            if re.search(edu_keywords, line, re.IGNORECASE):
                degree = line
                # Institution is usually the next line
                institution = lines[i+1] if i + 1 < len(lines) else ""
                new_edu.append({
                    "degree": degree,
                    "institution": institution,
                    "start_date": "",
                    "end_date": ""
                })
        
        if new_edu:
            profile["education"] = new_edu
        elif is_string_format:
            profile["education"] = [{"degree": e, "institution": "", "start_date": "", "end_date": ""} for e in profile["education"]]
        else:
            profile["education"] = []

    # 3. Robust Experience Extraction if parse_resume_text failed to find sections
    if not profile.get("experience"):
        date_range_pattern = re.compile(
            r'((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+)?(?:\d{4}|20XX))\s*[-–to]+\s*((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+)?(?:\d{4}|20XX)|Present|Current)', 
            re.IGNORECASE
        )
        for i, line in enumerate(lines):
            date_match = date_range_pattern.search(line)
            if date_match:
                title = lines[i-2] if i-2 >= 0 else ""
                company_loc = lines[i-1] if i-1 >= 0 else ""
                parts = company_loc.split(' - ') if ' - ' in company_loc else company_loc.split(',')
                company = parts[0].strip() if len(parts) > 0 else company_loc
                location = parts[1].strip() if len(parts) > 1 else ""
                
                profile["experience"].append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "start_date": date_match.group(1).strip(),
                    "end_date": date_match.group(2).strip(),
                    "details": []
                })

    
    # Final Deduplication step for candidate skills just in case
    for category in ["technical", "soft"]:
        if category in profile.get("skills", {}):
            unique_skills = []
            for s in profile["skills"][category]:
                if s not in unique_skills:
                    unique_skills.append(s)
            profile["skills"][category] = unique_skills

    profile["raw_text"] = extracted_text

    return json.dumps(profile)


def create_demo_match_result(candidate_profile: dict, job_profile: dict) -> str:
    """
    Demo fallback for candidate-to-job matching without calling Gemini.
    """
    import json
    import re
    
    job_req_skills = job_profile.get("required_skills", [])
    job_pref_skills = job_profile.get("preferred_skills", [])
    
    cand_tech = candidate_profile.get("skills", {}).get("technical", [])
    cand_soft = candidate_profile.get("skills", {}).get("soft", [])
    cand_all_skills = [s.lower() for s in cand_tech + cand_soft]
    exp_details_text = " ".join([detail.lower() for exp in candidate_profile.get("experience", []) for detail in exp.get("details", [])])
    raw_fallback = candidate_profile.get("raw_text", exp_details_text)
    normalized_resume_text = " ".join(raw_fallback.lower().split())
    
    # Semantic mapping for the matcher
    semantic_map = {
        "workflow optimization": ["process improvement", "workflow system", "workflow optimization"],
        "cross-functional stakeholder communication": ["cross-functional", "stakeholder"],
        "vendor management": ["vendor coordination", "vendor relationships", "vendor management"],
        "reporting": ["reporting", "reports"],
        "data analysis": ["data analysis", "kpi dashboards", "analysis"],
        "communication": ["stakeholder communication", "stakeholder", "communication"]
    }

    def is_matched(skill):
        normalized_skill = " ".join(skill.lower().split())
        if normalized_skill in normalized_resume_text:
            return True
            
        skill_l = skill.lower()
        if any(skill_l in c for c in cand_all_skills) or skill_l in cand_all_skills:
            return True
        if skill_l in semantic_map:
            for syn in semantic_map[skill_l]:
                if any(syn in c for c in cand_all_skills) or syn in exp_details_text:
                    return True
        return False


    req_matched = []
    req_missing = []
    for skill in job_req_skills:
        if is_matched(skill):
            req_matched.append(skill)
        else:
            req_missing.append(skill)
            
    pref_matched = []
    pref_missing = []
    for skill in job_pref_skills:
        if is_matched(skill):
            pref_matched.append(skill)
        else:
            pref_missing.append(skill)
            
    job_edu = job_profile.get("education", [])
    cand_edu = candidate_profile.get("education", [])
    edu_meets = False
    edu_assessment = ""
    
    if not job_edu:
        edu_meets = True
        edu_assessment = "[DEMO] No specific education required."
    elif cand_edu:
        job_edu_str = " ".join(job_edu).lower()
        # Ensure we properly get strings out of the candidate education dictionaries
        cand_edu_str = " ".join([e.get("degree", "").lower() if isinstance(e, dict) else str(e).lower() for e in cand_edu])
        
        if "bachelor" in job_edu_str and any(kw in cand_edu_str for kw in ["bachelor", "bba", "ba", "bs", "b.s."]):
            edu_meets = True
            edu_degree = cand_edu[0].get('degree', '') if isinstance(cand_edu[0], dict) else cand_edu[0]
            edu_assessment = f"[DEMO] Candidate's degree ({edu_degree}) satisfies the bachelor's requirement."
        else:
            edu_meets = True
            edu_assessment = f"[DEMO] Candidate has education evidence matching requirements."
    else:
        edu_meets = False
        edu_assessment = "[DEMO] Candidate missing required education evidence."
        
    job_exp_str = job_profile.get("required_experience", "")
    cand_total_exp = candidate_profile.get("total_years_experience", "")
    cand_exp = candidate_profile.get("experience", [])
    exp_meets = False
    exp_assessment = ""
    
    if not job_exp_str:
        exp_meets = True
        exp_assessment = "[DEMO] No specific experience duration required."
    elif cand_total_exp:
        import re
        job_years = re.search(r'(\d+)', job_exp_str)
        cand_years = re.search(r'(\d+)', cand_total_exp)
        if job_years and cand_years:
            if int(cand_years.group(1)) >= int(job_years.group(1)):
                exp_meets = True
                exp_assessment = f"[DEMO] Candidate states {cand_total_exp} of experience, meeting the {job_exp_str} requirement."
            else:
                exp_meets = False
                exp_assessment = f"[DEMO] Candidate has {cand_total_exp} of experience, which does not meet the {job_exp_str} requirement."
        else:
            exp_meets = True
            exp_assessment = f"[DEMO] Candidate experience matches required duration."
    else:
        # Fallback to naive logic if cand_total_exp is missing
        req_years_match = re.search(r'(\d+)', job_exp_str)
        req_years = int(req_years_match.group(1)) if req_years_match else 0
        
        total_cand_years = len(cand_exp) * 2
        if total_cand_years == 0:
            total_cand_years = 5
            
        if total_cand_years >= req_years:
            exp_meets = True
            exp_assessment = f"[DEMO] Candidate experience heuristically estimated to meet the {req_years}+ years requirement."
        else:
            exp_meets = False
            exp_assessment = f"[DEMO] Candidate experience heuristically estimated to fall short of {req_years}+ years requirement."

    result = {
      "required_skill_match": {
        "matched": req_matched,
        "missing": req_missing
      },
      "preferred_skill_match": {
        "matched": pref_matched,
        "missing": pref_missing
      },
      "experience_match": {
        "meets_requirement": exp_meets,
        "assessment": exp_assessment
      },
      "education_match": {
        "meets_requirement": edu_meets,
        "assessment": edu_assessment
      },
      "summary": "[DEMO MODE] Deterministic matching applied. Skills extracted from job description successfully compared against candidate extracted skills."
    }
    
    return json.dumps(result)
