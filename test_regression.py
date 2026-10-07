import asyncio
import io
import docx
from backend.extractor.gate import process_extraction
from backend.deterministic.fallback import generate_fallback_match
from backend.deterministic.scorer import calculate_match_score

def test_regression():
    # Construct a dummy JD
    jd_text = """
    We need a Python Developer.
    Required:
    - 3+ years experience
    - Python
    - SQL
    - AWS
    - Bachelor's degree
    """
    
    # Construct a dummy Resume
    resume_text = """
    John Doe
    Python Developer
    
    EXPERIENCE
    Python Developer
    Google
    Jan 2018 - Present
    - Wrote Python and SQL code.
    
    EDUCATION
    Bachelor of Science in Computer Science
    
    SKILLS
    Python, SQL
    """
    
    # Create docx bytes
    doc = docx.Document()
    for line in resume_text.split("\n"):
        doc.add_paragraph(line)
    doc_stream = io.BytesIO()
    doc.save(doc_stream)
    doc_bytes = doc_stream.getvalue()
    
    # NEW MODULAR PIPELINE (Fallback path)
    new_extraction = process_extraction(doc_bytes, "docx", jd_text)
    new_match = generate_fallback_match(new_extraction["resume"], new_extraction["job_description"])
    new_score = calculate_match_score(new_match, new_extraction["job_description"])
    
    # OLD EXPECTED RESULT
    # (Previously extracted directly from main.py before it was deleted)
    expected_score = 58.3
    expected_matched_req = ['Python', 'SQL']
    
    # COMPARISON
    assert new_score["overall_score"] == expected_score, f"Score mismatch: {new_score['overall_score']} vs {expected_score}"
    assert new_match["required_skill_match"]["matched"] == expected_matched_req
    print("Regression Test Passed! New modular behavior exactly matches expected legacy behavior.")

if __name__ == "__main__":
    test_regression()
