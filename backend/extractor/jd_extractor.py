import re
from backend.observability import cli

def extract_job_description(job_description_text: str) -> dict:
    """
    Deterministically extracts structured information from raw job description text.
    """
    cli.log_stage("EXTRACTOR", "Job description extraction started")
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
        
    cli.log_info("EXTRACTOR", 
        f"Job title: {profile['job_title']}\n"
        f"→ Required skills: {len(profile['required_skills'])}\n"
        f"→ Preferred skills: {len(profile['preferred_skills'])}\n"
        f"→ Experience requirement: {profile['required_experience'] or 'None specified'}\n"
        f"→ Education requirement: {', '.join(profile['education']) or 'None specified'}\n"
        f"→ Certifications: {len(profile['certifications'])}"
    )
        
    return profile
