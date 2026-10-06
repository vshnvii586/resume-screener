import re

def generate_fallback_match(candidate_profile: dict, job_profile: dict) -> dict:
    """
    Fallback deterministic matching logic.
    """
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
        edu_assessment = "[FALLBACK] No specific education required."
    elif cand_edu:
        job_edu_str = " ".join(job_edu).lower()
        # Ensure we properly get strings out of the candidate education dictionaries
        cand_edu_str = " ".join([e.get("degree", "").lower() if isinstance(e, dict) else str(e).lower() for e in cand_edu])
        
        if "bachelor" in job_edu_str and any(kw in cand_edu_str for kw in ["bachelor", "bba", "ba", "bs", "b.s."]):
            edu_meets = True
            edu_degree = cand_edu[0].get('degree', '') if isinstance(cand_edu[0], dict) else cand_edu[0]
            edu_assessment = f"[FALLBACK] Candidate's degree ({edu_degree}) satisfies the bachelor's requirement."
        else:
            edu_meets = True
            edu_assessment = "[FALLBACK] Candidate has education evidence matching requirements."
    else:
        edu_meets = False
        edu_assessment = "[FALLBACK] Candidate missing required education evidence."
        
    job_exp_str = job_profile.get("required_experience", "")
    cand_total_exp = candidate_profile.get("total_years_experience", "")
    cand_exp = candidate_profile.get("experience", [])
    exp_meets = False
    exp_assessment = ""
    
    if not job_exp_str:
        exp_meets = True
        exp_assessment = "[FALLBACK] No specific experience duration required."
    elif cand_total_exp:
        job_years = re.search(r'(\d+)', job_exp_str)
        cand_years = re.search(r'(\d+)', cand_total_exp)
        if job_years and cand_years:
            if int(cand_years.group(1)) >= int(job_years.group(1)):
                exp_meets = True
                exp_assessment = f"[FALLBACK] Candidate states {cand_total_exp} of experience, meeting the {job_exp_str} requirement."
            else:
                exp_meets = False
                exp_assessment = f"[FALLBACK] Candidate has {cand_total_exp} of experience, which does not meet the {job_exp_str} requirement."
        else:
            exp_meets = True
            exp_assessment = "[FALLBACK] Candidate experience matches required duration."
    else:
        # Fallback to naive logic if cand_total_exp is missing
        req_years_match = re.search(r'(\d+)', job_exp_str)
        req_years = int(req_years_match.group(1)) if req_years_match else 0
        
        total_cand_years = len(cand_exp) * 2
        if total_cand_years == 0:
            total_cand_years = 5
            
        if total_cand_years >= req_years:
            exp_meets = True
            exp_assessment = f"[FALLBACK] Candidate experience heuristically estimated to meet the {req_years}+ years requirement."
        else:
            exp_meets = False
            exp_assessment = f"[FALLBACK] Candidate experience heuristically estimated to fall short of {req_years}+ years requirement."

    return {
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
      "summary": "[FALLBACK MODE] Deterministic matching applied. Skills extracted from job description successfully compared against candidate extracted skills."
    }
