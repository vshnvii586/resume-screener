const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const parseResume = async (resumeFile) => {
  const formData = new FormData();
  formData.append('file', resumeFile);

  const response = await fetch(`${API_BASE_URL}/api/resumes/ai-parse`, {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error("Failed to extract data from the resume file.");
  }
  
  const data = await response.json();
  return data.profile;
};

export const parseJobDescription = async (jobDescription) => {
  const response = await fetch(`${API_BASE_URL}/api/jobs/parse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_description: jobDescription }),
  });

  if (!response.ok) {
    throw new Error("Failed to parse the job description.");
  }
  
  const data = await response.json();
  return data.profile;
};

export const matchCandidate = async (candidateProfile, jobProfile) => {
  const response = await fetch(`${API_BASE_URL}/api/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      candidate_profile: candidateProfile,
      job_profile: jobProfile,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to evaluate the candidate against the job description.");
  }
  
  const data = await response.json();
  return data.match;
};

export const calculateScore = async (matchResult, jobProfile) => {
  const response = await fetch(`${API_BASE_URL}/api/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      match_result: matchResult,
      job_profile: jobProfile,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to calculate the final match score.");
  }
  
  return await response.json();
};
