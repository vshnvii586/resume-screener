import React from 'react';
import { CloudDoodle, StarDoodle, SparkleDoodle, FlowerDoodle, PlaneDoodle, ResumeDoodle, HeartDoodle } from './Doodles';

const Header = () => {
  return (
    <div className="bg-[#fff4f8] px-8 py-12 text-center relative overflow-hidden rounded-t-[2rem] border-b border-pink-100 flex flex-col items-center justify-center min-h-[200px]">
      {/* Doodle Decorations */}
      <CloudDoodle className="absolute top-2 left-4 w-24 h-24 opacity-60 text-[#F9A8D4] animate-float" />
      <CloudDoodle className="absolute bottom-[-10px] right-2 w-32 h-32 opacity-50 text-[#FCE7F3] animate-cloud-drift" />
      <StarDoodle className="absolute top-1/2 left-[15%] w-6 h-6 opacity-60 text-[#FDBA9A] animate-twinkle" />
      <FlowerDoodle className="absolute bottom-4 left-[20%] w-8 h-8 opacity-50 text-[#F472B6] animate-float delay-500" />
      <SparkleDoodle className="absolute top-6 right-[20%] w-5 h-5 opacity-70 text-[#F9A8D4] animate-twinkle delay-300" />
      <HeartDoodle className="absolute top-1/2 right-[10%] w-6 h-6 opacity-40 text-[#F472B6] animate-float delay-1000" />
      
      {/* Central Illustration Area */}
      <div className="relative flex items-center justify-center mb-6 w-full max-w-md h-24">
        <ResumeDoodle className="w-16 h-20 text-[#8B7AAE] -rotate-6 transform hover:rotate-0 transition-transform duration-500 absolute left-1/3 -translate-x-full" />
        
        {/* Plane with dashed flight path */}
        <div className="absolute right-1/3 translate-x-full flex items-center">
          <svg className="w-24 h-8 opacity-40 text-[#F9A8D4] absolute right-8 -bottom-4" viewBox="0 0 100 30" fill="none">
            <path d="M0,25 Q40,30 100,5" stroke="currentColor" strokeWidth="2" strokeDasharray="4 4" fill="none" strokeLinecap="round" />
          </svg>
          <PlaneDoodle className="w-10 h-10 text-[#F472B6] -rotate-12 animate-float relative z-10" />
        </div>
      </div>
      
      <h1 className="relative text-4xl font-black text-[#40334D] mb-3 tracking-tight drop-shadow-sm" style={{fontFamily: "'Comic Sans MS', 'Chalkboard SE', sans-serif"}}>
        AI Resume Screener
      </h1>
      <p className="relative text-[#8B7AAE] text-lg font-medium drop-shadow-sm">
        Intelligent candidate screening and matching
      </p>
    </div>
  );
};

export default Header;
