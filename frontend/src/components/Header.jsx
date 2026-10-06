import React from 'react';

const Header = () => {
  return (
    <div className="bg-gradient-to-r from-slate-900 to-indigo-950 px-8 py-10 text-center relative overflow-hidden rounded-t-2xl">
      <div className="absolute top-0 left-0 w-full h-full bg-blue-500 opacity-10 transform -skew-y-6 -translate-y-10"></div>
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[200%] h-[200%] bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-500/20 via-transparent to-transparent opacity-60"></div>
      
      <h1 className="relative text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-200 to-indigo-100 mb-3 tracking-tight drop-shadow-md">
        AI Resume Screener
      </h1>
      <p className="relative text-indigo-200/90 text-lg font-medium drop-shadow-sm">
        Intelligent candidate screening and matching
      </p>
    </div>
  );
};

export default Header;
