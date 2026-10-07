import React, { useRef } from 'react';

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
    <div className="p-8 pb-10 bg-slate-50/50 backdrop-blur-sm">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Resume Upload Area */}
        <div className="flex flex-col">
          <label className="block text-sm font-semibold text-slate-700 mb-3 ml-1">
            1. Upload Candidate Resume
          </label>
          <div
            className={`flex-1 flex flex-col items-center justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-2xl transition-all duration-300 cursor-pointer min-h-[220px] shadow-sm hover:shadow-md ${
              resumeFile
                ? 'border-indigo-400 bg-indigo-50/60'
                : 'border-slate-300 bg-white hover:border-indigo-400'
            }`}
            onClick={() => fileInputRef.current.click()}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <div className="space-y-2 text-center">
              <div className="flex justify-center mb-4 transition-transform hover:scale-110 duration-300">
                {resumeFile ? (
                  <div className="h-14 w-14 bg-white rounded-full flex items-center justify-center shadow-md border border-indigo-100 text-3xl">
                    📄
                  </div>
                ) : (
                  <div className="h-14 w-14 bg-slate-50 rounded-full flex items-center justify-center shadow-inner border border-slate-100 text-slate-400 text-3xl">
                    📁
                  </div>
                )}
              </div>

              <div className="flex flex-col text-sm text-slate-500 justify-center gap-1">
                <span className="relative font-bold text-indigo-600 hover:text-indigo-700 transition-colors">
                  {resumeFile ? 'Change document' : 'Click to browse'}
                </span>
                <p>or drag and drop</p>
                <p className="text-xs text-slate-400 mt-1">PDF or DOCX</p>
              </div>

              {resumeFile && (
                <div className="mt-4 inline-block px-4 py-2 bg-white border border-indigo-100 rounded-xl shadow-sm">
                  <p className="text-sm font-bold text-indigo-900 truncate max-w-[220px]">
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
            className="block text-sm font-semibold text-slate-700 mb-3 ml-1"
          >
            2. Paste Job Description
          </label>
          <textarea
            id="job-description"
            className="flex-1 block w-full text-sm sm:text-base border-slate-200 rounded-2xl p-5 bg-white transition-all duration-300 min-h-[220px] resize-none focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 shadow-sm hover:shadow-md"
            placeholder="Paste the requirements, qualifications, and responsibilities here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-8 bg-rose-50/80 backdrop-blur-md border border-rose-200 text-rose-800 px-5 py-4 rounded-xl text-sm font-semibold flex items-center shadow-sm">
          <span className="text-xl mr-3">⚠️</span>
          {error}
        </div>
      )}

      {/* Action Button */}
      <div className="mt-10">
        <button
          type="button"
          disabled={!isFormValid || isLoading}
          onClick={onAnalyze}
          className={`group relative w-full flex justify-center items-center py-4 px-4 rounded-2xl shadow-lg text-lg font-extrabold text-white transition-all duration-300 overflow-hidden ${
            isFormValid && !isLoading
              ? 'bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 hover:shadow-xl hover:-translate-y-1'
              : 'bg-slate-300 cursor-not-allowed opacity-80 shadow-none'
          }`}
        >
          {/* Glassmorphism shine effect */}
          {isFormValid && !isLoading && (
            <div className="absolute top-0 -inset-full h-full w-1/2 z-5 block transform -skew-x-12 bg-gradient-to-r from-transparent to-white opacity-20 group-hover:animate-shine" />
          )}

          {isLoading ? (
            <div className="flex items-center gap-3">
              <div className="w-5 h-5 border-3 border-white/30 border-t-white rounded-full animate-spin"></div>
              <span>Processing Intelligence...</span>
            </div>
          ) : (
            "Analyze Candidate Match"
          )}
        </button>
        {isLoading && (
          <p className="text-center text-sm text-indigo-600 mt-4 font-semibold animate-pulse tracking-wide">
            Extracting semantic context and matching requirements...
          </p>
        )}
      </div>
    </div>
  );
};

export default UploadForm;
