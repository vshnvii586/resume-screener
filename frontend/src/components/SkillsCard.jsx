import React from 'react';
import { PencilDoodle, StarDoodle, CheckDoodle, CrossDoodle } from './Doodles';

const SkillsCard = ({ matchResult }) => {
  const reqMatchedCount = matchResult?.required_skill_match?.matched?.length || 0;
  const reqMissingCount = matchResult?.required_skill_match?.missing?.length || 0;
  const reqTotalCount = reqMatchedCount + reqMissingCount;
  const reqPercent = reqTotalCount > 0 ? Math.round((reqMatchedCount / reqTotalCount) * 100) : 0;

  const prefMatchedCount = matchResult?.preferred_skill_match?.matched?.length || 0;
  const prefMissingCount = matchResult?.preferred_skill_match?.missing?.length || 0;
  const prefTotalCount = prefMatchedCount + prefMissingCount;

  return (
    <div className="space-y-6">
      
      {/* Required Skills Card */}
      <div className="p-8 relative bg-[#FFF9F3] doodle-border-1 border-[#FCE7F3]">
        <PencilDoodle className="absolute top-6 right-6 w-8 h-8 opacity-50 text-[#F9A8D4] animate-float delay-100" />
        <div className="flex justify-between items-end mb-4">
          <h3 className="font-extrabold text-[#40334D] text-xl tracking-tight" style={{fontFamily: "'Comic Sans MS', 'Chalkboard SE', sans-serif"}}>Required Skills</h3>
          <span className="text-sm font-black text-[#F472B6] bg-[#FFF1F6] px-4 py-1.5 rounded-[1rem] shadow-sm border border-[#FCE7F3]">
            {reqMatchedCount} / {reqTotalCount}
          </span>
        </div>
        
        {/* Visual Progress Bar */}
        {reqTotalCount > 0 && (
          <div className="w-full bg-[#FFF1F6] rounded-full h-3 mb-8 overflow-hidden shadow-inner border border-[#FCE7F3]">
            <div 
              className={`h-full rounded-full transition-all duration-1000 ease-out ${reqPercent >= 80 ? 'bg-[#6EE7B7]' : reqPercent >= 50 ? 'bg-[#FDE047]' : 'bg-[#FDA4AF]'}`} 
              style={{ width: `${reqPercent}%` }}
            ></div>
          </div>
        )}
        
        <div className="flex flex-wrap gap-3 mt-2">
          {matchResult.required_skill_match?.matched?.map((skill, i) => (
            <span key={`req-match-${i}`} className="inline-flex items-center px-4 py-2 rounded-[1rem] text-sm font-bold bg-white text-[#10B981] border-2 border-[#A7F3D0] shadow-sm hover:scale-105 hover:-translate-y-0.5 transition-transform stagger-1" style={{animationDelay: `${i * 0.05}s`}}>
              <CheckDoodle className="mr-1.5 w-4 h-4 text-[#34D399]" />
              {skill}
            </span>
          ))}
          {matchResult.required_skill_match?.missing?.map((skill, i) => (
            <span key={`req-miss-${i}`} className="inline-flex items-center px-4 py-2 rounded-[1rem] text-sm font-bold bg-[#FFF1F6] text-[#F43F5E] border-2 border-[#FCE7F3] shadow-sm opacity-90 hover:scale-105 hover:-translate-y-0.5 transition-transform stagger-2" style={{animationDelay: `${i * 0.05}s`}}>
              <CrossDoodle className="mr-1.5 w-4 h-4 text-[#FB7185]" />
              {skill}
            </span>
          ))}
          {reqTotalCount === 0 && (
            <span className="text-[#8B7AAE] text-sm italic font-medium">No required skills specified.</span>
          )}
        </div>
      </div>

      {/* Preferred Skills Card */}
      {prefTotalCount > 0 && (
        <div className="p-8 relative bg-white doodle-border-2 border-[#FCE7F3]">
          <StarDoodle className="absolute top-6 right-6 w-6 h-6 opacity-40 text-[#FDBA9A] animate-twinkle" />
          <div className="flex justify-between items-end mb-5">
            <h3 className="font-bold text-[#8B7AAE] text-lg tracking-tight" style={{fontFamily: "'Comic Sans MS', 'Chalkboard SE', sans-serif"}}>Preferred Skills</h3>
            <span className="text-xs font-black text-[#8B7AAE] bg-[#FFF9F3] border border-[#FCE7F3] px-3 py-1.5 rounded-[1rem] shadow-sm">
              {prefMatchedCount} / {prefTotalCount}
            </span>
          </div>
          
          <div className="flex flex-wrap gap-3">
            {matchResult.preferred_skill_match?.matched?.map((skill, i) => (
              <span key={`pref-match-${i}`} className="inline-flex items-center px-4 py-2 rounded-[1rem] text-sm font-bold bg-[#F0FDF4] text-[#059669] border border-[#A7F3D0] shadow-sm hover:scale-105 hover:-translate-y-0.5 transition-transform stagger-3" style={{animationDelay: `${i * 0.05}s`}}>
                <CheckDoodle className="mr-1.5 w-3 h-3 text-[#34D399]" />
                {skill}
              </span>
            ))}
            {matchResult.preferred_skill_match?.missing?.map((skill, i) => (
              <span key={`pref-miss-${i}`} className="inline-flex items-center px-4 py-2 rounded-[1rem] text-sm font-medium bg-[#FFF9F3] text-[#8B7AAE] border border-[#FCE7F3] shadow-sm opacity-80 hover:scale-105 hover:-translate-y-0.5 transition-transform stagger-4" style={{animationDelay: `${i * 0.05}s`}}>
                <span className="mr-2 h-1.5 w-1.5 bg-[#F9A8D4] rounded-full"></span>
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SkillsCard;
