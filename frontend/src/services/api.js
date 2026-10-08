const API_BASE_URL = import.meta.env.VITE_API_URL;

export const analyzeApplication = async (resumeFile, jobDescription) => {
  const formData = new FormData();
  formData.append('file', resumeFile);
  formData.append('job_description', jobDescription);

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) {
    let errText = "Failed to analyze the application.";
    try {
      const errJson = await response.json();
      errText = errJson.detail || errText;
    } catch (e) {
      const text = await response.text();
      errText = text || errText;
    }
    throw new Error(errText);
  }
  
  return await response.json();
};
