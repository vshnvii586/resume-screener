import React from 'react';

const ScoreCard = ({ candidateProfile, scoreResult, matchResult }) => {
  const getScoreColor = (score) => {
    if (score >= 80) return "text-emerald-500";
    if (score >= 60) return "text-amber-500";
    return "text-rose-500";
  };
  
  const getScoreStroke = (score) => {
    if (score >= 80) return "stroke-emerald-500";
    if (score >= 60) return "stroke-amber-500";
    return "stroke-rose-500";
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

  return (
    <div className="bg-white rounded-3xl shadow-sm border border-slate-200 p-8 md:p-10 mb-8 flex flex-col md:flex-row justify-between items-center md:items-start gap-10 hover:shadow-md transition-shadow duration-300">
      <div className="flex-1 text-center md:text-left flex flex-col justify-center">
        <span className="text-sm font-extrabold text-indigo-500 uppercase tracking-widest mb-2">Candidate Profile</span>
        <h2 className="text-4xl font-black text-slate-900 tracking-tight">{candidateProfile.name || "Unknown Candidate"}</h2>
        {(candidateProfile.email || candidateProfile.phone) && (
          <div className="flex items-center justify-center md:justify-start gap-3 text-slate-500 text-sm font-medium mt-3 mb-6">
            {candidateProfile.email && (
              <span className="flex items-center gap-1.5 bg-slate-100 px-3 py-1 rounded-full">
                ✉️ {candidateProfile.email}
              </span>
            )}
            {candidateProfile.phone && (
              <span className="flex items-center gap-1.5 bg-slate-100 px-3 py-1 rounded-full">
                📞 {candidateProfile.phone}
              </span>
            )}
          </div>
        )}
        
        <div className="inline-block bg-indigo-50 text-indigo-800 px-5 py-3 rounded-xl text-sm font-semibold border border-indigo-100 shadow-sm self-center md:self-start">
          {generateQuickSummary()}
        </div>
      </div>
      
      {/* Circular Score Indicator */}
      <div className="flex flex-col items-center justify-center bg-slate-50/50 rounded-3xl p-6 border border-slate-100 min-w-[200px] shadow-inner">
        <div className="relative w-32 h-32 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90 drop-shadow-sm" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="42" stroke="currentColor" strokeWidth="10" fill="transparent" className="text-slate-200" />
            <circle 
              cx="50" cy="50" r="42" 
              stroke="currentColor" 
              strokeWidth="10" 
              fill="transparent" 
              strokeDasharray="263.89"
              strokeDashoffset={263.89 - (scoreResult.overall_score / 100) * 263.89}
              className={`transition-all duration-1500 ease-out ${getScoreStroke(scoreResult.overall_score)}`} 
              strokeLinecap="round" 
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-black tracking-tighter ${getScoreColor(scoreResult.overall_score)}`}>
              {scoreResult.overall_score}<span className="text-lg text-slate-400 font-bold">%</span>
            </span>
          </div>
        </div>
        <span className="text-xs font-black uppercase text-slate-400 mt-4 tracking-widest">Overall Match</span>
      </div>
    </div>
  );
};

export default ScoreCard;
