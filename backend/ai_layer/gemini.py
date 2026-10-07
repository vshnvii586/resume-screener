import os
import json
import asyncio
from google import genai
from backend.observability import cli

def _build_prompt(extraction_result: dict) -> str:
    resume_data = extraction_result.get("resume", {})
    jd_data = extraction_result.get("job_description", {})

    prompt = f"""
    You are an intelligent resume screening and analysis component.
    Your task is to evaluate the provided candidate resume data against the job description data.
    
    You MUST return ONLY a valid JSON object matching the exact structure below.
    Do NOT include Markdown formatting.
    Do NOT include ```json fences.
    Do NOT include any explanations before or after the JSON.
    
    Guidelines:
    - Compare the candidate's skills, experience, and education against the job requirements.
    - Match semantically related skills (e.g., "Adobe Photoshop" matches "Photoshop").
    - Only mark a required or preferred skill as matched if the candidate profile contains evidence.
    - Treat required and preferred skills separately.
    - For experience, determine whether the candidate appears to satisfy the stated experience requirement using the candidate's actual experience information.
    - For education, determine whether the candidate's education satisfies the stated requirement.
    - Provide a short overall summary of the candidate's strengths and missing requirements.
    - Do NOT produce an overall numerical score.
    - Do not invent information. If information is missing or ambiguous, say so.
    
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
    
    Candidate Profile (Structured JSON):
    {json.dumps(resume_data, indent=2)}
    
    Job Profile (Structured JSON):
    {json.dumps(jd_data, indent=2)}
    """
    return prompt

GEMINI_MODEL = "gemini-2.5-flash"

async def call_gemini_analysis(extraction_result: dict) -> dict:
    """
    Executes a single call to Gemini to analyze the candidate against the JD.
    Returns a structured success or failure response.
    """
    cli.log_stage("AI", "Preparing Gemini analysis")
    
    resume_len = len(json.dumps(extraction_result.get('resume', {})))
    jd_len = len(json.dumps(extraction_result.get('job_description', {})))
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        cli.log_error("AI", "GEMINI_API_KEY: missing")
        return {
            "status": "error",
            "error_type": "MISSING_API_KEY",
            "message": "GEMINI_API_KEY is not configured in the environment.",
            "data": None
        }

    cli.log_info("AI", f"GEMINI_API_KEY: detected\n→ Model: {GEMINI_MODEL}\n→ Resume Data: ~{resume_len//1024} KB\n→ JD Data: ~{jd_len//1024} KB")

    client = genai.Client(api_key=api_key)
    prompt = _build_prompt(extraction_result)
    
    cli.log_stage("GEMINI", f"Preparing request #1\n→ Model: {GEMINI_MODEL}\n→ Sending ONE combined resume + JD analysis request\n→ Prompt length: {len(prompt):,} characters")
    cli.start_timer("gemini")
    cli.log_info("GEMINI", "Request sent")

    def _sync_call():
        return client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(_sync_call),
            timeout=60
        )
        dur = cli.stop_timer("gemini")
        response_text = response.text
        
        cli.log_success("GEMINI", f"Response received\n→ Response length: {len(response_text) if response_text else 0:,} characters\n→ Time: {dur:.2f}s")
        cli.log_info("GEMINI", "Parsing JSON response")
        
        if not response_text:
            cli.log_error("GEMINI", "Empty response")
            return {
                "status": "error",
                "error_type": "EMPTY_RESPONSE",
                "message": "Gemini returned an empty response.",
                "data": None
            }

        # Try to parse the JSON
        try:
            # Clean up potential markdown fences just in case Gemini ignored instructions
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            parsed_data = json.loads(clean_text)
            
            # Simple validation of structure
            if "required_skill_match" not in parsed_data:
                raise ValueError("Missing required_skill_match in output")
                
            cli.log_success("GEMINI", "Valid AI response")
            
            # Print a readable summary of AI result
            req_matched = len(parsed_data.get('required_skill_match', {}).get('matched', []))
            req_miss = len(parsed_data.get('required_skill_match', {}).get('missing', []))
            pref_matched = len(parsed_data.get('preferred_skill_match', {}).get('matched', []))
            pref_miss = len(parsed_data.get('preferred_skill_match', {}).get('missing', []))
            
            cli.log_stage("AI RESULT", 
                f"Required skills: {req_matched} ✓, {req_miss} ✗\n"
                f"Preferred skills: {pref_matched} ✓, {pref_miss} ✗\n"
                f"Experience meets requirement: {'✓' if parsed_data.get('experience_match', {}).get('meets_requirement') else '✗'}\n"
                f"Education meets requirement: {'✓' if parsed_data.get('education_match', {}).get('meets_requirement') else '✗'}\n"
                f"Summary: {parsed_data.get('summary')}"
            )
                
            return {
                "status": "success",
                "data": parsed_data
            }
        except (json.JSONDecodeError, ValueError) as json_err:
            cli.log_error("GEMINI", f"Invalid JSON response: {str(json_err)}")
            return {
                "status": "error",
                "error_type": "INVALID_AI_OUTPUT",
                "message": f"Failed to parse or validate Gemini output as JSON: {str(json_err)}",
                "data": None
            }

    except asyncio.TimeoutError:
        cli.log_header("⚠ GEMINI FAILED\nReason: TIMEOUT")
        cli.log_error("GEMINI", "TIMEOUT")
        return {
            "status": "error",
            "error_type": "TIMEOUT",
            "message": "Gemini API call timed out after 60 seconds.",
            "data": None
        }
    except Exception as e:
        # Catch-all for SDK or network errors (authentication, rate limits, etc.)
        cli.log_header(f"⚠ GEMINI FAILED\nReason: {type(e).__name__}")
        cli.log_error("GEMINI", f"API ERROR: {type(e).__name__}")
        return {
            "status": "error",
            "error_type": "API_ERROR",
            "message": f"Gemini API error: {str(e)}",
            "data": None
        }
