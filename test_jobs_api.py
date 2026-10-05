import requests
import json
import time

job_description = """
Business Operations Analyst

We are looking for a Business Operations Analyst to support process improvement, reporting, and cross-functional business initiatives.

Required Qualifications:
- Bachelor's degree in Business Administration, Operations, Analytics, Information Systems, or a related field.
- 3+ years of experience in business operations, operations analysis, or process improvement.
- Strong experience with process improvement and workflow optimization.
- Strong data analysis and reporting skills.
- Experience working with cross-functional stakeholders and communicating with business teams.
- Strong proficiency in Microsoft Excel, including dashboards, reporting, and data analysis.
- Experience with project management and coordinating cross-functional initiatives.

Preferred Qualifications:
- Experience with SQL and querying relational databases.
- Experience with Power BI or Tableau.
- Experience automating recurring reports and business workflows.
- Experience with CRM systems.
- Experience with vendor management and budget tracking.

Responsibilities:
- Analyze operational processes and identify opportunities for improvement.
- Build and maintain KPI dashboards and recurring business reports.
- Coordinate cross-functional projects with finance, sales, and customer support teams.
- Support process optimization and workflow automation initiatives.
- Prepare reports and presentations for leadership.
- Track operational metrics and communicate insights to stakeholders.
- Support vendor coordination and budget-related activities.
"""

res = requests.post("http://127.0.0.1:8000/api/jobs/parse", json={"job_description": job_description})
print(json.dumps(res.json(), indent=2))
