import React from 'react';

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
      <div className="bg-white rounded-3xl shadow-sm border border-slate-200 p-8 hover:shadow-md transition-shadow duration-300">
        <div className="flex justify-between items-end mb-4">
          <h3 className="font-extrabold text-slate-900 text-xl tracking-tight">Required Skills</h3>
          <span className="text-sm font-black text-slate-600 bg-slate-100 px-4 py-1.5 rounded-full shadow-inner">
            {reqMatchedCount} / {reqTotalCount}
          </span>
        </div>
        
        {/* Visual Progress Bar */}
        {reqTotalCount > 0 && (
          <div className="w-full bg-slate-100 rounded-full h-3 mb-8 overflow-hidden shadow-inner">
            <div 
              className={`h-full rounded-full transition-all duration-1000 ease-out ${reqPercent >= 80 ? 'bg-emerald-500' : reqPercent >= 50 ? 'bg-amber-500' : 'bg-rose-500'}`} 
              style={{ width: `${reqPercent}%` }}
            ></div>
          </div>
        )}
        
        <div className="flex flex-wrap gap-2.5 mt-2">
          {matchResult.required_skill_match?.matched?.map((skill, i) => (
            <span key={`req-match-${i}`} className="inline-flex items-center px-3.5 py-1.5 rounded-lg text-sm font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-sm">
              <span className="mr-1.5 text-emerald-500 text-base leading-none">✓</span>
              {skill}
            </span>
          ))}
          {matchResult.required_skill_match?.missing?.map((skill, i) => (
            <span key={`req-miss-${i}`} className="inline-flex items-center px-3.5 py-1.5 rounded-lg text-sm font-bold bg-rose-50 text-rose-700 border border-rose-200 shadow-sm opacity-90">
              <span className="mr-1.5 text-rose-500 text-base leading-none">✗</span>
              {skill}
            </span>
          ))}
          {reqTotalCount === 0 && (
            <span className="text-slate-400 text-sm italic font-medium">No required skills specified.</span>
          )}
        </div>
      </div>

      {/* Preferred Skills Card */}
      {prefTotalCount > 0 && (
        <div className="bg-slate-50/50 rounded-3xl shadow-sm border border-slate-200 p-8 hover:shadow-md transition-shadow duration-300">
          <div className="flex justify-between items-end mb-5">
            <h3 className="font-bold text-slate-700 text-lg tracking-tight">Preferred Skills</h3>
            <span className="text-xs font-black text-slate-500 bg-white border border-slate-200 px-3 py-1 rounded-full shadow-sm">
              {prefMatchedCount} / {prefTotalCount}
            </span>
          </div>
          
          <div className="flex flex-wrap gap-2.5">
            {matchResult.preferred_skill_match?.matched?.map((skill, i) => (
              <span key={`pref-match-${i}`} className="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-bold bg-indigo-50 text-indigo-700 border border-indigo-100 shadow-sm">
                <span className="mr-1.5 text-indigo-400 text-base leading-none">+</span>
                {skill}
              </span>
            ))}
            {matchResult.preferred_skill_match?.missing?.map((skill, i) => (
              <span key={`pref-miss-${i}`} className="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium bg-white text-slate-500 border border-slate-200 shadow-sm opacity-80">
                <span className="mr-2 h-1.5 w-1.5 bg-slate-300 rounded-full"></span>
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
