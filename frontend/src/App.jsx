import React, { useState } from 'react';
import Header from './components/Header';
import UploadForm from './components/UploadForm';
import Dashboard from './components/Dashboard';
import { analyzeApplication } from './services/api';
import './index.css';

function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  
  // Pipeline State
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Result State
  const [candidateProfile, setCandidateProfile] = useState(null);
  const [matchResult, setMatchResult] = useState(null);
  const [scoreResult, setScoreResult] = useState(null);

  const handleAnalyzeClick = async () => {
    if (!resumeFile || !jobDescription.trim()) return;

    setIsLoading(true);
    setError(null);
    setScoreResult(null);
    setCandidateProfile(null);
    setMatchResult(null);

    try {
      const data = await analyzeApplication(resumeFile, jobDescription);
      
      setCandidateProfile(data.candidate_profile);
      
      setMatchResult({
        required_skill_match: data.required_skill_match,
        preferred_skill_match: data.preferred_skill_match,
        experience_match: data.experience_match,
        education_match: data.education_match,
        summary: data.summary,
        used_fallback: data.used_fallback
      });
      
      setScoreResult({
        overall_score: data.overall_score,
        breakdown: data.score_breakdown
      });

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
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8 font-sans selection:bg-indigo-200">
      <div className="w-full max-w-6xl bg-white shadow-2xl shadow-indigo-900/5 rounded-2xl overflow-hidden border border-slate-100 transition-all duration-300">
        <Header />

        {!scoreResult ? (
          <UploadForm 
            resumeFile={resumeFile}
            setResumeFile={setResumeFile}
            jobDescription={jobDescription}
            setJobDescription={setJobDescription}
            isLoading={isLoading}
            error={error}
            onAnalyze={handleAnalyzeClick}
          />
        ) : (
          <Dashboard 
            candidateProfile={candidateProfile}
            matchResult={matchResult}
            scoreResult={scoreResult}
            onReset={handleReset}
          />
        )}
      </div>
    </div>
  );
}

export default App;
