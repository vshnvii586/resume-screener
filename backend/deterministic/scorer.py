from backend.observability import cli

def calculate_match_score(match_result: dict, job_profile: dict) -> dict:
    """
    Deterministically calculates a match score based on AI or fallback match results.
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
    
    result = {
        "overall_score": round(overall_score, 1),
        "breakdown": {
            "required_skills": {
                "matched": len(matched_req),
                "total": len(required),
                "percentage": round(required_ratio * 100, 1),
                "weight": 0.50,
                "weighted_score": round(required_ratio * 50, 1)
            },
            "experience": {
                "percentage": round(experience_ratio * 100, 1),
                "weight": 0.25,
                "weighted_score": round(experience_ratio * 25, 1)
            },
            "education": {
                "percentage": round(education_ratio * 100, 1),
                "weight": 0.15,
                "weighted_score": round(education_ratio * 15, 1)
            },
            "preferred_skills": {
                "matched": len(matched_pref),
                "total": len(preferred),
                "percentage": round(preferred_ratio * 100, 1),
                "weight": 0.10,
                "weighted_score": round(preferred_ratio * 10, 1)
            }
        }
    }
    
    cli.log_data("SCORE", [
        "Required Skills:",
        f"{round(required_ratio * 100, 1)}% × 50% = {round(required_ratio * 50, 1)}\n",
        "Experience:",
        f"{round(experience_ratio * 100, 1)}% × 25% = {round(experience_ratio * 25, 1)}\n",
        "Education:",
        f"{round(education_ratio * 100, 1)}% × 15% = {round(education_ratio * 15, 1)}\n",
        "Preferred Skills:",
        f"{round(preferred_ratio * 100, 1)}% × 10% = {round(preferred_ratio * 10, 1)}\n",
        "────────────────────────",
        f"FINAL SCORE: {round(overall_score, 1)}%",
        "────────────────────────\n"
    ])
    
    return result
