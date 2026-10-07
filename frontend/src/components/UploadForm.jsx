import React, { useRef } from 'react';
import { StarDoodle, FlowerDoodle, SparkleDoodle, PlaneDoodle, ResumeDoodle, ErrorDoodle } from './Doodles';

const UploadForm = ({
  resumeFile,
  setResumeFile,
  jobDescription,
  setJobDescription,
  isLoading,
  error,
  onAnalyze,
}) => {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setResumeFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => e.preventDefault();

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (
        file.type === 'application/pdf' ||
        file.name.endsWith('.pdf') ||
        file.name.endsWith('.docx')
      ) {
        setResumeFile(file);
      }
    }
  };

  const isFormValid = resumeFile !== null && jobDescription.trim().length > 0;

  return (
    <div className="p-8 pb-10 relative bg-transparent z-10">
      {/* Background doodles for Upload form */}
      <SparkleDoodle className="absolute top-10 right-10 w-6 h-6 opacity-40 text-[#F9A8D4] animate-twinkle" />
      <FlowerDoodle className="absolute bottom-16 left-6 w-8 h-8 opacity-50 text-[#F472B6] animate-float" />
      <StarDoodle className="absolute bottom-20 right-6 w-5 h-5 opacity-40 text-[#FDBA9A] animate-twinkle delay-500" />
      <SparkleDoodle className="absolute top-20 left-4 w-4 h-4 opacity-50 text-[#FCE7F3] animate-float delay-700" />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 relative z-10">
        
        {/* Resume Upload Area */}
        <div className="flex flex-col">
          <label className="block text-sm font-bold text-[#40334D] mb-3 ml-2" style={{fontFamily: "'Comic Sans MS', 'Chalkboard SE', sans-serif"}}>
            1. Upload Candidate Resume
          </label>
          <div
            className={`flex-1 flex flex-col items-center justify-center px-6 pt-5 pb-6 border-dashed border-[3px] transition-all duration-300 cursor-pointer min-h-[220px] relative overflow-hidden group ${
              resumeFile
                ? 'border-[#F9A8D4] bg-[#FFF1F6]'
                : 'border-[#FCE7F3] bg-[#FFF9F3] hover:border-[#F9A8D4]'
            }`}
            style={{ borderRadius: '40px 30px 45px 35px / 35px 45px 30px 40px' }}
            onClick={() => fileInputRef.current.click()}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            {/* Subtle glow on hover */}
            <div className="absolute inset-0 bg-[#FCE7F3] opacity-0 group-hover:opacity-10 transition-opacity duration-300"></div>
            
            <div className="space-y-2 text-center relative z-10">
              <div className="flex justify-center mb-4 transition-transform hover:scale-110 duration-300 h-20 items-end">
                {resumeFile ? (
                  <div className="relative animate-fade-in-up">
                    <ResumeDoodle className="w-14 h-16 text-[#F472B6]" />
                    <SparkleDoodle className="absolute -top-3 -right-3 w-5 h-5 text-[#FDBA9A] animate-twinkle" />
                  </div>
                ) : (
                  <div className="relative opacity-80 group-hover:opacity-100 transition-opacity duration-300 flex items-end justify-center w-full">
                    <ResumeDoodle className="w-12 h-14 text-[#F9A8D4] -rotate-6" />
                    
                    <div className="absolute -top-4 -right-10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center">
                      <svg className="w-12 h-6 text-[#FCE7F3] absolute right-4 bottom-2" viewBox="0 0 50 20" fill="none">
                        <path d="M0,15 Q20,15 50,5" stroke="currentColor" strokeWidth="2" strokeDasharray="3 3" fill="none" strokeLinecap="round" />
                      </svg>
                      <PlaneDoodle className="w-6 h-6 text-[#F9A8D4] -rotate-12 animate-float" />
                    </div>
                  </div>
                )}
              </div>

              <div className="flex flex-col text-sm text-[#8B7AAE] justify-center gap-1">
                <span className="relative font-bold text-[#F472B6] hover:text-[#F9A8D4] transition-colors" style={{fontFamily: "'Comic Sans MS', 'Chalkboard SE', sans-serif"}}>
                  {resumeFile ? 'Change document' : 'Click to browse'}
                </span>
                <p>or drag and drop</p>
                <p className="text-xs text-[#F9A8D4] mt-1 font-bold">PDF or DOCX</p>
              </div>

              {resumeFile && (
                <div className="mt-4 inline-block px-4 py-2 bg-white border border-[#FCE7F3] rounded-[1rem] shadow-sm animate-fade-in-up">
                  <p className="text-sm font-bold text-[#40334D] truncate max-w-[220px]">
                    {resumeFile.name}
                  </p>
                </div>
              )}
            </div>
            <input
              type="file"
              ref={fileInputRef}
              className="sr-only"
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={handleFileChange}
            />
          </div>
        </div>

        {/* Job Description Area */}
        <div className="flex flex-col">
          <label
            htmlFor="job-description"
            className="block text-sm font-bold text-[#40334D] mb-3 ml-2" style={{fontFamily: "'Comic Sans MS', 'Chalkboard SE', sans-serif"}}
          >
            2. Paste Job Description
          </label>
          <div className="p-1 flex-1 min-h-[220px] bg-[#FFF9F3] doodle-border-3 border-[#FCE7F3] focus-within:border-[#F9A8D4] focus-within:bg-[#fffcf9] transition-all duration-300 relative group overflow-hidden">
            <div className="absolute inset-0 bg-[#FCE7F3] opacity-0 group-focus-within:opacity-10 transition-opacity duration-300"></div>
            <textarea
              id="job-description"
              className="w-full h-full text-sm sm:text-base border-0 p-4 bg-transparent transition-all duration-300 resize-none focus:ring-0 focus:outline-none text-[#40334D] placeholder-[#F9A8D4] relative z-10"
              placeholder="Paste the requirements, qualifications, and responsibilities here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-8 bg-[#fff1f2] border border-[#fecdd3] text-[#be123c] px-5 py-4 rounded-2xl text-sm font-bold flex items-center shadow-sm animate-fade-in-up">
          <ErrorDoodle className="w-6 h-6 mr-3 text-[#be123c]" />
          {error}
        </div>
      )}

      {/* Action Button */}
      <div className="mt-10 relative z-10 flex justify-center">
        <button
          type="button"
          disabled={!isFormValid || isLoading}
          onClick={onAnalyze}
          className={`group relative w-full flex justify-center items-center py-4 px-8 rounded-full shadow-[0_4px_15px_rgba(244,114,182,0.2)] text-lg font-black transition-all duration-300 overflow-hidden border-2 ${
            isFormValid && !isLoading
              ? 'bg-[#FFF1F6] border-[#F9A8D4] text-[#F472B6] hover:bg-[#FCE7F3] hover:border-[#F472B6] hover:shadow-[0_6px_20px_rgba(244,114,182,0.3)] hover:-translate-y-1'
              : 'bg-[#FFF9F3] border-[#FCE7F3] text-[#F9A8D4] cursor-not-allowed shadow-none'
          }`}
          style={{fontFamily: "'Comic Sans MS', 'Chalkboard SE', sans-serif"}}
        >
          {isFormValid && !isLoading && (
            <div className="absolute top-0 -inset-full h-full w-1/2 z-5 block transform -skew-x-12 bg-gradient-to-r from-transparent to-white opacity-40 group-hover:animate-shine" />
          )}

          {isLoading ? (
            <div className="flex items-center gap-3">
              <div className="w-5 h-5 border-3 border-[#FCE7F3] border-t-[#F472B6] rounded-full animate-spin"></div>
              <span>Processing...</span>
            </div>
          ) : (
            <>
              <span className="relative z-10">Analyze Candidate Match</span>
              <div className="ml-3 opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0 transition-all duration-300 flex items-center">
                <svg className="w-8 h-4 text-[#FCE7F3] absolute -left-6 bottom-1" viewBox="0 0 30 10" fill="none">
                  <path d="M0,8 Q15,8 30,2" stroke="currentColor" strokeWidth="2" strokeDasharray="2 2" fill="none" strokeLinecap="round" />
                </svg>
                <PlaneDoodle className="w-6 h-6 text-[#F472B6] -rotate-12 animate-float" />
              </div>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default UploadForm;
