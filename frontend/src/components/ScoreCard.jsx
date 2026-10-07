import React from 'react';
import { SparkleDoodle, EnvelopeDoodle, PhoneDoodle, FlowerDoodle } from './Doodles';

const ScoreCard = ({ candidateProfile, scoreResult, matchResult }) => {
  const getScoreColor = (score) => {
    if (score >= 80) return "text-[#34d399]";
    if (score >= 60) return "text-[#fbbf24]";
    return "text-[#f43f5e]";
  };
  
  const getScoreStroke = (score) => {
    if (score >= 80) return "stroke-[#34d399]";
    if (score >= 60) return "stroke-[#fbbf24]";
    return "stroke-[#f43f5e]";
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
    <div className="p-8 md:p-10 mb-8 flex flex-col md:flex-row justify-between items-center md:items-start gap-10 relative bg-[#FFF9F3] doodle-border doodle-border-double border-[#FCE7F3]">
      <SparkleDoodle className="absolute top-4 right-6 w-8 h-8 opacity-60 text-[#FDBA9A] animate-float delay-300" />
      <div className="flex-1 text-center md:text-left flex flex-col justify-center">
        <span className="text-sm font-extrabold text-[#F472B6] uppercase tracking-widest mb-2" style={{fontFamily: "'Comic Sans MS', 'Chalkboard SE', sans-serif"}}>Candidate Profile</span>
        <h2 className="text-4xl font-black text-[#40334D] tracking-tight">{candidateProfile.name || "Unknown Candidate"}</h2>
        {(candidateProfile.email || candidateProfile.phone) && (
          <div className="flex items-center justify-center md:justify-start gap-3 text-[#8B7AAE] text-sm font-medium mt-3 mb-6">
            {candidateProfile.email && (
              <span className="flex items-center gap-2 bg-[#FFF1F6] px-4 py-1.5 rounded-full border border-[#FCE7F3]">
                <EnvelopeDoodle className="w-4 h-4 text-[#F472B6]" /> {candidateProfile.email}
              </span>
            )}
            {candidateProfile.phone && (
              <span className="flex items-center gap-2 bg-[#FFF1F6] px-4 py-1.5 rounded-full border border-[#FCE7F3]">
                <PhoneDoodle className="w-4 h-4 text-[#F472B6]" /> {candidateProfile.phone}
              </span>
            )}
          </div>
        )}
        
        <div className="inline-block bg-[#FFF1F6] text-[#F472B6] px-5 py-3 rounded-[1rem] text-sm font-bold border border-[#FCE7F3] shadow-sm self-center md:self-start">
          {generateQuickSummary()}
        </div>
      </div>
      
      {/* Circular Score Indicator */}
      <div className="flex flex-col items-center justify-center bg-white p-6 doodle-border-3 border-[#FFF1F6] min-w-[200px] shadow-[0_4px_15px_rgba(244,114,182,0.08)] relative">
        <FlowerDoodle className="absolute -bottom-3 -left-3 w-10 h-10 text-[#F9A8D4] animate-float delay-150" />
        <div className="relative w-32 h-32 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90 drop-shadow-sm" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="42" stroke="currentColor" strokeWidth="10" fill="transparent" className="text-[#FCE7F3]" />
            <circle 
              cx="50" cy="50" r="42" 
              stroke="currentColor" 
              strokeWidth="10" 
              fill="transparent" 
              strokeDasharray="263.89"
              strokeDashoffset={263.89 - (scoreResult.overall_score / 100) * 263.89}
              className={`animate-score-ring ${getScoreStroke(scoreResult.overall_score)}`} 
              strokeLinecap="round" 
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-black tracking-tighter ${getScoreColor(scoreResult.overall_score)}`}>
              {scoreResult.overall_score}<span className="text-lg text-[#F9A8D4] font-bold">%</span>
            </span>
          </div>
        </div>
        <span className="text-xs font-black uppercase text-[#F9A8D4] mt-4 tracking-widest" style={{fontFamily: "'Comic Sans MS', 'Chalkboard SE', sans-serif"}}>Overall Match</span>
      </div>
    </div>
  );
};

export default ScoreCard;
