import React from 'react';
import { BooksDoodle, DocumentOutlineDoodle, CheckDoodle, CrossDoodle } from './Doodles';

const ExperienceEducationCard = ({ matchResult }) => {
  return (
    <div className="overflow-hidden h-full flex flex-col relative bg-white doodle-border-3 border-[#FCE7F3]">
      <BooksDoodle className="absolute bottom-6 right-6 w-10 h-10 opacity-30 text-[#8B7AAE] animate-float delay-700" />
      <div className="px-8 py-6 bg-[#FFF1F6] border-b-2 border-[#FCE7F3] flex items-center rounded-t-[2.5rem]">
        <DocumentOutlineDoodle className="w-6 h-6 mr-3 text-[#F472B6]" />
        <h3 className="font-extrabold text-[#40334D] text-lg tracking-tight" style={{fontFamily: "'Comic Sans MS', 'Chalkboard SE', sans-serif"}}>Core Background Check</h3>
      </div>
      
      <div className="p-8 space-y-8 flex-1">
        {/* Experience Check */}
        <div className="flex gap-5">
          <div className="flex-shrink-0 mt-0.5">
            {matchResult.experience_match?.meets_requirement ? (
              <div className="h-12 w-12 rounded-[1rem] bg-[#F0FDF4] flex items-center justify-center shadow-inner border border-[#A7F3D0]">
                <CheckDoodle className="text-[#10B981] w-6 h-6" />
              </div>
            ) : (
              <div className="h-12 w-12 rounded-[1rem] bg-[#FFF1F6] flex items-center justify-center shadow-inner border border-[#FCE7F3]">
                <CrossDoodle className="text-[#F43F5E] w-6 h-6" />
              </div>
            )}
          </div>
          <div>
            <h4 className="font-extrabold text-[#8B7AAE] text-base tracking-tight mb-1">Professional Experience</h4>
            <p className="text-sm text-[#40334D] leading-relaxed font-medium">{matchResult.experience_match?.assessment}</p>
          </div>
        </div>

        <div className="h-[2px] bg-[#FCE7F3] w-full ml-16"></div>

        {/* Education Check */}
        <div className="flex gap-5">
          <div className="flex-shrink-0 mt-0.5">
            {matchResult.education_match?.meets_requirement ? (
              <div className="h-12 w-12 rounded-[1rem] bg-[#F0FDF4] flex items-center justify-center shadow-inner border border-[#A7F3D0]">
                <CheckDoodle className="text-[#10B981] w-6 h-6" />
              </div>
            ) : (
              <div className="h-12 w-12 rounded-[1rem] bg-[#FFF1F6] flex items-center justify-center shadow-inner border border-[#FCE7F3]">
                <CrossDoodle className="text-[#F43F5E] w-6 h-6" />
              </div>
            )}
          </div>
          <div>
            <h4 className="font-extrabold text-[#8B7AAE] text-base tracking-tight mb-1">Education & Credentials</h4>
            <p className="text-sm text-[#40334D] leading-relaxed font-medium">{matchResult.education_match?.assessment}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExperienceEducationCard;
