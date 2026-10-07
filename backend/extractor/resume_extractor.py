import io
import re
from backend.observability import cli

def extract_text_from_file_bytes(file_bytes: bytes, file_extension: str) -> str:
    """Helper function to extract text from PDF or DOCX bytes. Uses PyMuPDF for PDF, falling back to PyPDF2."""
    extracted_text = ""
    if file_extension == "pdf":
        cli.log_info("EXTRACTOR", "Format: PDF\n→ Primary extractor: PyMuPDF")
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
            cli.log_warning("EXTRACTOR", f"PyMuPDF extraction failed: {e}\n→ Switching to PyPDF2 fallback")
            
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
        except Exception as e:
            raise Exception(f"PDF extraction failed on both PyMuPDF and PyPDF2: {str(e)}")
    elif file_extension == "docx":
        import docx
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


def extract_resume(file_bytes: bytes, file_extension: str) -> dict:
    """
    Extracts text from a resume file and parses it into a structured dictionary.
    """
    cli.start_timer("extraction")
    cli.log_stage("EXTRACTOR", "Resume extraction started")
    extracted_text = extract_text_from_file_bytes(file_bytes, file_extension)
    cli.log_success("EXTRACTOR", f"Text extracted: {len(extracted_text):,} characters")
    profile = parse_resume_text(extracted_text)
    
    # Extract total years of experience from summary if present
    exp_match = re.search(r'((?:\d+)\+?\s*(?:years?|yrs?))', extracted_text[:1000], re.IGNORECASE)
    if exp_match:
        val = exp_match.group(1).replace("yrs", "years").strip()
        profile["total_years_experience"] = val
    
    # 1. Remap 'job_title' to 'title'
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

    # Final Deduplication step for candidate skills
    for category in ["technical", "soft"]:
        if category in profile.get("skills", {}):
            unique_skills = []
            for s in profile["skills"][category]:
                if s not in unique_skills:
                    unique_skills.append(s)
            profile["skills"][category] = unique_skills

    profile["raw_text"] = extracted_text

    # Generate summary stats
    name = profile.get("name") or "Unknown"
    email = "detected" if profile.get("email") else "missing"
    phone = "detected" if profile.get("phone") else "missing"
    skills = sum(len(v) for v in profile.get("skills", {}).values())
    exp = len(profile.get("experience", []))
    edu = len(profile.get("education", []))
    
    cli.log_info("EXTRACTOR", 
        f"Candidate: {name}\n"
        f"→ Email: {email}\n"
        f"→ Phone: {phone}\n"
        f"→ Skills: {skills}\n"
        f"→ Experience entries: {exp}\n"
        f"→ Education entries: {edu}"
    )
    
    dur = cli.stop_timer("extraction")
    cli.log_success("EXTRACTOR", f"Resume extraction complete ({dur*1000:.0f} ms)")

    return profile
