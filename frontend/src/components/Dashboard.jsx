import React from 'react';
import ScoreCard from './ScoreCard';
import SkillsCard from './SkillsCard';
import ExperienceEducationCard from './ExperienceEducationCard';

const Dashboard = ({ candidateProfile, scoreResult, matchResult, onReset }) => {
  return (
    <div className="bg-slate-50 border-t border-slate-200 p-6 md:p-10 lg:p-12 animate-fade-in-up">
      <ScoreCard 
        candidateProfile={candidateProfile} 
        scoreResult={scoreResult} 
        matchResult={matchResult} 
      />

      {/* Recruiter Insight Callout */}
      <div className="bg-gradient-to-br from-indigo-50 to-blue-50/50 rounded-3xl shadow-sm border border-indigo-100 p-8 mb-10 flex flex-col md:flex-row gap-5 items-start md:items-center">
        <div className="flex-shrink-0 bg-white p-3 rounded-2xl shadow-sm border border-indigo-100 text-indigo-500 text-2xl">
          💡
        </div>
        <div>
          <h3 className="font-extrabold text-indigo-950 text-lg tracking-tight mb-1">Analysis Insight</h3>
          <p className="text-base text-indigo-800/90 leading-relaxed font-medium">
            {matchResult.summary}
          </p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 mb-12">
        <SkillsCard matchResult={matchResult} />
        <ExperienceEducationCard matchResult={matchResult} />
      </div>

      {/* Reset Action Area */}
      <div className="text-center pt-10 border-t border-slate-200">
        <button 
          onClick={onReset} 
          className="group inline-flex items-center justify-center px-8 py-3.5 border-2 border-slate-200 shadow-sm text-base font-black rounded-2xl text-slate-700 bg-white hover:bg-slate-50 hover:border-indigo-200 hover:text-indigo-600 focus:outline-none focus:ring-4 focus:ring-indigo-500/10 transition-all duration-300"
        >
          <span className="mr-2 opacity-70 group-hover:opacity-100 transition-opacity">↺</span>
          Screen Another Candidate
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
