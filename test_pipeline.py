import json
import sys
import os

sys.path.insert(0, os.path.abspath('backend'))
from main import create_demo_resume_analysis, create_demo_job_analysis, create_demo_match_result

extracted_resume = """
Jordan Lee
your.name@gmail.com
(206) 555-0184

SUMMARY
Operations Analyst with 6+ years of experience optimizing processes and leading cross-functional projects.

EDUCATION
Bachelor of Business Administration
University of Washington

PROFESSIONAL EXPERIENCE
Senior Operations Analyst
NovaBridge Solutions - Seattle, WA
20XX - Present
- Led implementation of a new internal workflow system that reduced manual processing time by 28%
- Built monthly KPI dashboards for leadership, improving visibility into sales and service performance
- Coordinated cross-functional projects involving finance, sales, and customer support teams
- Managed vendor relationships and contract renewals valued at over $250K annually
- Trained 12 new hires on reporting tools, internal systems, and operating procedures

Business Operations Specialist
Harbor Peak Group - Portland, OR
20XX - 20XX
- Redesigned scheduling and resource planning process, increasing team utilization by 18%
- Created automated Excel reports that saved approximately 10 hours of manual work each week
- Supported launch of two regional service locations by managing logistics and onboarding plans
- Prepared executive presentations summarizing quarterly trends, risks, and opportunities
- Maintained CRM data accuracy above 97% through regular audits and process controls

SKILLS
Project Management, Stakeholder management, Process improvement, Budget tracking, Data analysis, Vendor coordination
"""

job_description = """
Job Title: Business Operations Analyst

Requirements:
- Bachelor's degree in Business Administration, Operations, Analytics, Information Systems, or a related field.
- 3+ years of experience in business operations, operations analysis, or process improvement.
- Strong process improvement and workflow optimization skills
- Deep experience in data analysis and reporting
- Excellent cross-functional stakeholder communication
- Advanced Microsoft Excel skills
- Demonstrated project management ability

Preferred Qualifications:
- Experience with SQL
- Familiarity with Power BI or Tableau
- Background in report/workflow automation
- Experience maintaining CRM systems
- Knowledge of vendor management and budget tracking
"""

def test():
    resume_json = create_demo_resume_analysis(extracted_resume)
    resume_profile = json.loads(resume_json)
    
    job_json = create_demo_job_analysis(job_description)
    job_profile = json.loads(job_json)
    
    match_json = create_demo_match_result(resume_profile, job_profile)
    match_result = json.loads(match_json)
    
    print("=== RESUME PROFILE ===")
    print(json.dumps(resume_profile, indent=2))
    
    print("\n=== JOB PROFILE ===")
    print(json.dumps(job_profile, indent=2))
    
    print("\n=== MATCH RESULT ===")
    print(json.dumps(match_result, indent=2))

if __name__ == "__main__":
    test()
