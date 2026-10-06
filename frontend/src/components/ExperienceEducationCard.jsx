import React from 'react';

const ExperienceEducationCard = ({ matchResult }) => {
  return (
    <div className="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden h-full hover:shadow-md transition-shadow duration-300 flex flex-col">
      <div className="px-8 py-5 bg-slate-50 border-b border-slate-200 flex items-center">
        <span className="text-xl mr-3 opacity-70">📋</span>
        <h3 className="font-extrabold text-slate-900 text-lg tracking-tight">Core Background Check</h3>
      </div>
      
      <div className="p-8 space-y-8 flex-1">
        {/* Experience Check */}
        <div className="flex gap-5">
          <div className="flex-shrink-0 mt-0.5">
            {matchResult.experience_match?.meets_requirement ? (
              <div className="h-10 w-10 rounded-2xl bg-emerald-100 flex items-center justify-center shadow-inner border border-emerald-50">
                <span className="text-emerald-600 text-lg font-bold">✓</span>
              </div>
            ) : (
              <div className="h-10 w-10 rounded-2xl bg-rose-100 flex items-center justify-center shadow-inner border border-rose-50">
                <span className="text-rose-600 text-lg font-bold">✗</span>
              </div>
            )}
          </div>
          <div>
            <h4 className="font-extrabold text-slate-900 text-base tracking-tight mb-1">Professional Experience</h4>
            <p className="text-sm text-slate-600 leading-relaxed font-medium">{matchResult.experience_match?.assessment}</p>
          </div>
        </div>

        <div className="h-px bg-slate-100 w-full ml-14"></div>

        {/* Education Check */}
        <div className="flex gap-5">
          <div className="flex-shrink-0 mt-0.5">
            {matchResult.education_match?.meets_requirement ? (
              <div className="h-10 w-10 rounded-2xl bg-emerald-100 flex items-center justify-center shadow-inner border border-emerald-50">
                <span className="text-emerald-600 text-lg font-bold">✓</span>
              </div>
            ) : (
              <div className="h-10 w-10 rounded-2xl bg-rose-100 flex items-center justify-center shadow-inner border border-rose-50">
                <span className="text-rose-600 text-lg font-bold">✗</span>
              </div>
            )}
          </div>
          <div>
            <h4 className="font-extrabold text-slate-900 text-base tracking-tight mb-1">Education & Credentials</h4>
            <p className="text-sm text-slate-600 leading-relaxed font-medium">{matchResult.education_match?.assessment}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExperienceEducationCard;
