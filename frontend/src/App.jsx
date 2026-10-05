import React, { useState, useRef } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  
  // Pipeline State
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [candidateProfile, setCandidateProfile] = useState(null);
  const [matchResult, setMatchResult] = useState(null);
  const [scoreResult, setScoreResult] = useState(null);

  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setResumeFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf' || 
          file.name.endsWith('.pdf') || 
          file.name.endsWith('.docx')) {
        setResumeFile(file);
      }
    }
  };

  const handleAnalyzeClick = async () => {
    if (!resumeFile || !jobDescription.trim()) return;

    setIsLoading(true);
    setError(null);
    setScoreResult(null);
    setCandidateProfile(null);
    setMatchResult(null);

    try {
      // 1. Parse Resume
      const formData = new FormData();
      formData.append('file', resumeFile);

      const resumeRes = await fetch(`${API_BASE_URL}/api/resumes/ai-parse`, {
        method: "POST",
        body: formData,
      });
      if (!resumeRes.ok) throw new Error("Failed to extract data from the resume file.");
      const resumeData = await resumeRes.json();
      const parsedCandidateProfile = resumeData.profile;
      
      // 2. Parse Job Description
      const jobRes = await fetch(`${API_BASE_URL}/api/jobs/parse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_description: jobDescription }),
      });
      if (!jobRes.ok) throw new Error("Failed to parse the job description.");
      const jobData = await jobRes.json();
      const parsedJobProfile = jobData.profile;

      // 3. Match
      const matchRes = await fetch(`${API_BASE_URL}/api/match`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_profile: parsedCandidateProfile,
          job_profile: parsedJobProfile,
        }),
      });
      if (!matchRes.ok) throw new Error("Failed to evaluate the candidate against the job description.");
      const matchData = await matchRes.json();
      const parsedMatchResult = matchData.match;

      // 4. Score
      const scoreRes = await fetch(`${API_BASE_URL}/api/score`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          match_result: parsedMatchResult,
          job_profile: parsedJobProfile,
        }),
      });
      if (!scoreRes.ok) throw new Error("Failed to calculate the final match score.");
      const scoreData = await scoreRes.json();
      
      // Store final state to display success
      setCandidateProfile(parsedCandidateProfile);
      setMatchResult(parsedMatchResult);
      setScoreResult(scoreData);

    } catch (err) {
      console.error("Pipeline Error:", err);
      setError(err.message || "An unexpected error occurred during analysis.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResumeFile(null);
    setJobDescription("");
    setCandidateProfile(null);
    setMatchResult(null);
    setScoreResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const isFormValid = resumeFile !== null && jobDescription.trim().length > 0;

  // Render helpers
  const getScoreColor = (score) => {
    if (score >= 80) return "text-green-500";
    if (score >= 60) return "text-yellow-500";
    return "text-red-500";
  };
  
  const getScoreStroke = (score) => {
    if (score >= 80) return "stroke-green-500";
    if (score >= 60) return "stroke-yellow-500";
    return "stroke-red-500";
  };

  const generateQuickSummary = () => {
    if (!matchResult) return "";
    const reqMatched = matchResult.required_skill_match?.matched?.length || 0;
    const reqTotal = reqMatched + (matchResult.required_skill_match?.missing?.length || 0);
    const expMeets = matchResult.experience_match?.meets_requirement;
    const eduMeets = matchResult.education_match?.meets_requirement;
    
    let text = "";
    if (expMeets && eduMeets) text += "Meets education and experience requirements";
    else if (expMeets && !eduMeets) text += "Meets experience requirements but missing education";
    else if (!expMeets && eduMeets) text += "Meets education requirements but missing experience";
    else text += "Missing core experience and education requirements";
    
    if (reqTotal > 0) {
      text += ` and matches ${reqMatched} of ${reqTotal} required skills.`;
    } else {
      text += ".";
    }
    return text;
  };

  const reqMatchedCount = matchResult?.required_skill_match?.matched?.length || 0;
  const reqMissingCount = matchResult?.required_skill_match?.missing?.length || 0;
  const reqTotalCount = reqMatchedCount + reqMissingCount;
  const reqPercent = reqTotalCount > 0 ? Math.round((reqMatchedCount / reqTotalCount) * 100) : 0;

  const prefMatchedCount = matchResult?.preferred_skill_match?.matched?.length || 0;
  const prefMissingCount = matchResult?.preferred_skill_match?.missing?.length || 0;
  const prefTotalCount = prefMatchedCount + prefMissingCount;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="w-full max-w-5xl bg-white shadow-xl rounded-2xl overflow-hidden border border-gray-100 transition-all duration-300">
        
        {/* Header Section */}
        <div className="bg-blue-600 px-8 py-10 text-center relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-full bg-blue-700 opacity-20 transform -skew-y-6 -translate-y-10"></div>
          <h1 className="relative text-4xl font-extrabold text-white mb-3 tracking-tight">
            AI Resume Screener
          </h1>
          <p className="relative text-blue-100 text-lg font-medium">
            Intelligent candidate screening and matching
          </p>
        </div>

        {/* Input Form Section (Hidden when showing results to act as a dashboard) */}
        {!scoreResult && (
          <div className="p-8 pb-10">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Resume Upload Area */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  1. Upload Candidate Resume
                </label>
                <div 
                  className={`flex flex-col items-center justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-xl transition-all cursor-pointer h-52 ${
                    resumeFile 
                      ? 'border-blue-400 bg-blue-50/50 hover:bg-blue-50' 
                      : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                  }`}
                  onClick={() => fileInputRef.current.click()}
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                >
                  <div className="space-y-1 text-center">
                    <div className="flex justify-center mb-3">
                      {resumeFile ? (
                        <div className="h-12 w-12 bg-white rounded-full flex items-center justify-center shadow-sm border border-blue-200 text-2xl">
                          📄
                        </div>
                      ) : (
                        <div className="h-12 w-12 bg-gray-100 rounded-full flex items-center justify-center text-gray-400 text-2xl">
                          📁
                        </div>
                      )}
                    </div>
                    
                    <div className="flex flex-col text-sm text-gray-600 justify-center">
                      <span className="relative rounded-md font-medium text-blue-600 hover:text-blue-500">
                        {resumeFile ? 'Change file' : 'Click to upload'}
                      </span>
                      <p className="pl-1">or drag and drop</p>
                    </div>
                    
                    {resumeFile && (
                      <div className="mt-2 inline-block px-3 py-1 bg-white border border-blue-200 rounded-lg shadow-sm">
                        <p className="text-sm font-bold text-blue-800 truncate max-w-[200px]">
                          {resumeFile.name}
                        </p>
                      </div>
                    )}
                  </div>
                  <input 
                    type="file"
                    ref={fileInputRef}
                    className="sr-only" 
                    accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    onChange={handleFileChange}
                  />
                </div>
              </div>

              {/* Job Description Area */}
              <div>
                <label htmlFor="job-description" className="block text-sm font-semibold text-gray-700 mb-2">
                  2. Paste Job Description
                </label>
                <textarea
                  id="job-description"
                  className="shadow-sm block w-full focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm border border-gray-300 rounded-xl p-4 bg-white transition-shadow h-52 resize-none"
                  placeholder="Paste the full job description here..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                />
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mt-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm font-medium">
                ⚠️ {error}
              </div>
            )}

            {/* Action Button */}
            <div className="mt-8">
              <button
                type="button"
                disabled={!isFormValid || isLoading}
                onClick={handleAnalyzeClick}
                className={`w-full flex justify-center items-center py-4 px-4 rounded-xl shadow-sm text-lg font-bold text-white transition-all duration-200 ${
                  isFormValid && !isLoading
                    ? 'bg-blue-600 hover:bg-blue-700 hover:shadow-md transform hover:-translate-y-0.5' 
                    : 'bg-gray-300 cursor-not-allowed opacity-70'
                }`}
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing Data...
                  </>
                ) : (
                  "Analyze Candidate Match"
                )}
              </button>
              {isLoading && (
                <p className="text-center text-sm text-blue-600 mt-3 font-medium animate-pulse">
                  Please wait while the AI parses and matches the profile...
                </p>
              )}
            </div>
          </div>
        )}

        {/* DASHBOARD RESULT SECTION */}
        {scoreResult && candidateProfile && matchResult && (
          <div className="bg-gray-50 border-t border-gray-200 p-6 md:p-10 animate-fade-in-up">
            
            {/* Top Identity & Score Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 md:p-8 mb-8 flex flex-col md:flex-row justify-between items-center md:items-start gap-8">
              <div className="flex-1 text-center md:text-left flex flex-col justify-center">
                <span className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-1">Candidate Profile</span>
                <h2 className="text-3xl font-black text-gray-900 tracking-tight">{candidateProfile.name || "Unknown Candidate"}</h2>
                {(candidateProfile.email || candidateProfile.phone) && (
                  <p className="text-gray-500 text-base mt-1 mb-5">
                    {candidateProfile.email} {candidateProfile.email && candidateProfile.phone ? '•' : ''} {candidateProfile.phone}
                  </p>
                )}
                
                <div className="inline-block bg-blue-50 text-blue-800 px-4 py-2.5 rounded-lg text-sm font-semibold border border-blue-100 self-start">
                  {generateQuickSummary()}
                </div>
              </div>
              
              {/* Circular Score Indicator */}
              <div className="flex flex-col items-center justify-center bg-gray-50 rounded-2xl p-5 border border-gray-100 min-w-[180px]">
                <div className="relative w-28 h-28 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="42" stroke="currentColor" strokeWidth="10" fill="transparent" className="text-gray-200" />
                    <circle 
                      cx="50" cy="50" r="42" 
                      stroke="currentColor" 
                      strokeWidth="10" 
                      fill="transparent" 
                      strokeDasharray="263.89"
                      strokeDashoffset={263.89 - (scoreResult.overall_score / 100) * 263.89}
                      className={`transition-all duration-1000 ease-out ${getScoreStroke(scoreResult.overall_score)}`} 
                      strokeLinecap="round" 
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`text-2xl font-black tracking-tight ${getScoreColor(scoreResult.overall_score)}`}>
                      {scoreResult.overall_score}%
                    </span>
                  </div>
                </div>
                <span className="text-sm font-bold uppercase text-gray-500 mt-3 tracking-wider">Overall Match</span>
              </div>
            </div>

            {/* Recruiter Insight Callout */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl shadow-sm border border-blue-100 p-6 mb-8">
              <div className="flex items-center mb-3">
                <svg className="h-6 w-6 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <h3 className="font-bold text-blue-900 text-lg">Analysis Insight</h3>
              </div>
              <p className="text-base text-blue-800 leading-relaxed font-medium">
                {matchResult.summary}
              </p>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              
              {/* Left Column: Skills */}
              <div className="space-y-6">
                
                {/* Required Skills Card */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                  <div className="flex justify-between items-end mb-3">
                    <h3 className="font-bold text-gray-900 text-xl">Required Skills</h3>
                    <span className="text-sm font-bold text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                      {reqMatchedCount} / {reqTotalCount}
                    </span>
                  </div>
                  
                  {/* Visual Progress Bar */}
                  {reqTotalCount > 0 && (
                    <div className="w-full bg-gray-100 rounded-full h-2.5 mb-6 overflow-hidden">
                      <div 
                        className={`h-2.5 rounded-full transition-all duration-1000 ease-out ${reqPercent >= 80 ? 'bg-green-500' : reqPercent >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`} 
                        style={{ width: `${reqPercent}%` }}
                      ></div>
                    </div>
                  )}
                  
                  <div className="flex flex-wrap gap-2 mt-2">
                    {matchResult.required_skill_match?.matched?.map((skill, i) => (
                      <span key={`req-match-${i}`} className="inline-flex items-center px-3 py-1.5 rounded-md text-sm font-semibold bg-green-50 text-green-700 border border-green-200">
                        <svg className="mr-1.5 h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/></svg>
                        {skill}
                      </span>
                    ))}
                    {matchResult.required_skill_match?.missing?.map((skill, i) => (
                      <span key={`req-miss-${i}`} className="inline-flex items-center px-3 py-1.5 rounded-md text-sm font-semibold bg-red-50 text-red-700 border border-red-200">
                        <svg className="mr-1.5 h-4 w-4 text-red-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"/></svg>
                        {skill}
                      </span>
                    ))}
                    {reqTotalCount === 0 && (
                      <span className="text-gray-500 text-sm italic">No required skills specified.</span>
                    )}
                  </div>
                </div>

                {/* Preferred Skills Card */}
                {prefTotalCount > 0 && (
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 opacity-95">
                    <div className="flex justify-between items-end mb-4">
                      <h3 className="font-semibold text-gray-700 text-lg">Preferred Skills</h3>
                      <span className="text-xs font-bold text-gray-500 bg-gray-100 px-2.5 py-1 rounded-full">
                        {prefMatchedCount} / {prefTotalCount}
                      </span>
                    </div>
                    
                    <div className="flex flex-wrap gap-2">
                      {matchResult.preferred_skill_match?.matched?.map((skill, i) => (
                        <span key={`pref-match-${i}`} className="inline-flex items-center px-3 py-1.5 rounded-md text-sm font-medium bg-green-50 text-green-700 border border-green-200">
                          <svg className="mr-1.5 h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/></svg>
                          {skill}
                        </span>
                      ))}
                      {matchResult.preferred_skill_match?.missing?.map((skill, i) => (
                        <span key={`pref-miss-${i}`} className="inline-flex items-center px-3 py-1.5 rounded-md text-sm font-medium bg-gray-100 text-gray-600 border border-gray-200">
                          <span className="mr-2 h-1.5 w-1.5 bg-gray-400 rounded-full"></span>
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Right Column: Experience, Education */}
              <div className="space-y-6">
                
                <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden h-full">
                  <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex items-center">
                    <svg className="h-5 w-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <h3 className="font-bold text-gray-900 text-lg">Core Background Check</h3>
                  </div>
                  
                  <div className="p-6 space-y-6">
                    {/* Experience Check */}
                    <div className="flex gap-4">
                      <div className="flex-shrink-0 mt-0.5">
                        {matchResult.experience_match?.meets_requirement ? (
                          <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                            <svg className="h-5 w-5 text-green-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/></svg>
                          </div>
                        ) : (
                          <div className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center">
                            <svg className="h-5 w-5 text-red-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"/></svg>
                          </div>
                        )}
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-900 text-base">Professional Experience</h4>
                        <p className="text-sm text-gray-600 mt-1.5 leading-relaxed">{matchResult.experience_match?.assessment}</p>
                      </div>
                    </div>

                    <div className="h-px bg-gray-100 w-full"></div>

                    {/* Education Check */}
                    <div className="flex gap-4">
                      <div className="flex-shrink-0 mt-0.5">
                        {matchResult.education_match?.meets_requirement ? (
                          <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                            <svg className="h-5 w-5 text-green-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/></svg>
                          </div>
                        ) : (
                          <div className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center">
                            <svg className="h-5 w-5 text-red-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"/></svg>
                          </div>
                        )}
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-900 text-base">Education & Credentials</h4>
                        <p className="text-sm text-gray-600 mt-1.5 leading-relaxed">{matchResult.education_match?.assessment}</p>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            </div>

            {/* Reset Action Area */}
            <div className="text-center pt-8 pb-2 border-t border-gray-200 mt-4">
              <button 
                onClick={handleReset} 
                className="inline-flex items-center justify-center px-8 py-3 border border-gray-300 shadow-sm text-base font-bold rounded-xl text-gray-700 bg-white hover:bg-gray-50 hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
              >
                <svg className="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                Screen Another Candidate
              </button>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}

export default App;
