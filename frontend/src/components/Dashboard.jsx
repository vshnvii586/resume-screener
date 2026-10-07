import React from 'react';
import ScoreCard from './ScoreCard';
import SkillsCard from './SkillsCard';
import ExperienceEducationCard from './ExperienceEducationCard';
import { CloudDoodle, SparkleDoodle, FlowerDoodle, PlaneDoodle, StarDoodle, SparkIdeaDoodle, ResetDoodle } from './Doodles';

const Dashboard = ({ candidateProfile, scoreResult, matchResult, onReset }) => {
  return (
    <div className="relative p-6 md:p-10 lg:p-12 overflow-hidden z-10 w-full">
      
      {/* Background Doodles */}
      <CloudDoodle className="absolute top-10 left-10 w-20 h-20 opacity-40 animate-float text-[#F9A8D4]" />
      <CloudDoodle className="absolute top-40 right-20 w-24 h-24 opacity-30 animate-cloud-drift text-[#FCE7F3]" />
      <SparkleDoodle className="absolute bottom-20 left-1/4 w-8 h-8 opacity-50 animate-twinkle text-[#FDBA9A]" />
      <StarDoodle className="absolute top-1/4 left-1/3 w-6 h-6 opacity-40 animate-twinkle text-[#F9A8D4] delay-700" />
      <FlowerDoodle className="absolute bottom-1/3 right-1/4 w-8 h-8 opacity-30 animate-float text-[#F472B6]" />
      <PlaneDoodle className="absolute top-1/2 left-10 w-10 h-10 opacity-20 animate-fly text-[#F472B6]" />
      <SparkleDoodle className="absolute top-20 right-10 w-7 h-7 opacity-40 animate-float text-[#F9A8D4] delay-500" />

      <div className="relative z-10 max-w-5xl mx-auto">
        <div className="stagger-1">
          <ScoreCard 
            candidateProfile={candidateProfile} 
            scoreResult={scoreResult} 
            matchResult={matchResult} 
          />
        </div>

        {/* Recruiter Insight Callout */}
        <div className="stagger-2 p-8 mb-10 flex flex-col md:flex-row gap-5 items-start md:items-center relative bg-[#FFF9F3] doodle-border-2 border-[#FCE7F3]">
          <FlowerDoodle className="absolute -top-3 -left-3 w-8 h-8 text-[#F472B6] animate-float" />
          <div className="flex-shrink-0 bg-white p-3 rounded-[1rem] shadow-sm border border-[#FCE7F3] text-[#F472B6]">
            <SparkIdeaDoodle className="w-8 h-8" />
          </div>
          <div>
            <h3 className="font-extrabold text-[#40334D] text-lg tracking-tight mb-1" style={{fontFamily: "'Comic Sans MS', 'Chalkboard SE', sans-serif"}}>Analysis Insight</h3>
            <p className="text-base text-[#8B7AAE] leading-relaxed font-medium">
              {matchResult.summary}
            </p>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 mb-12">
          <div className="stagger-3">
            <SkillsCard matchResult={matchResult} />
          </div>
          <div className="stagger-5">
            <ExperienceEducationCard matchResult={matchResult} />
          </div>
        </div>

        {/* Reset Action Area */}
        <div className="text-center pt-10 border-t-2 border-[#FCE7F3] mt-10">
          <button 
            onClick={onReset} 
            className="group inline-flex items-center justify-center px-8 py-4 border-2 border-[#FCE7F3] shadow-sm text-base font-black rounded-full text-[#8B7AAE] bg-white hover:bg-[#FFF1F6] hover:border-[#F9A8D4] hover:text-[#F472B6] transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_6px_20px_rgba(244,114,182,0.15)]"
          >
            <ResetDoodle className="w-5 h-5 mr-2 opacity-70 group-hover:opacity-100 transition-opacity" />
            Screen Another Candidate
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
