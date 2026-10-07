import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import UploadForm from './components/UploadForm';
import Dashboard from './components/Dashboard';
import { parseResume, parseJobDescription, matchCandidate, calculateScore } from './services/api';
import { CloudDoodle, PlaneDoodle, ResumeDoodle, SparkleDoodle } from './components/Doodles';
import './index.css';

const InitialLoadTransition = ({ onReveal, onComplete }) => {
  const planeRef = useRef(null);
  const overlayRef = useRef(null);
  const resumeRef = useRef(null);
  
  // Use refs for callbacks to avoid re-triggering useEffect when parent re-renders
  const onRevealRef = useRef(onReveal);
  const onCompleteRef = useRef(onComplete);
  
  useEffect(() => {
    onRevealRef.current = onReveal;
    onCompleteRef.current = onComplete;
  }, [onReveal, onComplete]);

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      onRevealRef.current();
      const timer = setTimeout(() => onCompleteRef.current(), 500);
      return () => clearTimeout(timer);
    }

    // Randomized Orbit Parameters
    const orbitRadiusX = 80 + Math.random() * 40; // 80 to 120
    const orbitRadiusY = 60 + Math.random() * 30; // 60 to 90
    const startAngle = Math.random() * Math.PI * 2;
    const direction = Math.random() > 0.5 ? 1 : -1;
    
    // Ensure exit is completely offscreen (upper-right)
    const exitX = (window.innerWidth / 2) + 200 + Math.random() * 300;
    const exitY = -(window.innerHeight / 2) - 200 - Math.random() * 200;
    
    // Timing
    const duration = 2600;
    const orbitDuration = 1300; 
    let startTime = null;
    let animationFrame;
    let revealTriggered = false;

    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Trigger reveal of the underlying page smoothly
      if (elapsed > 1500 && !revealTriggered) {
        revealTriggered = true;
        onRevealRef.current();
      }

      if (planeRef.current) {
        let x, y, angle;
        
        if (elapsed <= orbitDuration) {
          // --- ORBIT PHASE ---
          const orbitProgress = elapsed / orbitDuration;
          // Smooth ease in/out for the orbit speed
          const easedOrbitProgress = orbitProgress < 0.5 ? 2 * orbitProgress * orbitProgress : 1 - Math.pow(-2 * orbitProgress + 2, 2) / 2;
          
          const currentAngle = startAngle + (easedOrbitProgress * Math.PI * 2 * direction);
          
          x = Math.cos(currentAngle) * orbitRadiusX;
          y = Math.sin(currentAngle) * orbitRadiusY;
          
          // Calculate tangent for rotation
          const dx = -Math.sin(currentAngle) * orbitRadiusX * direction;
          const dy = Math.cos(currentAngle) * orbitRadiusY * direction;
          angle = Math.atan2(dy, dx) * (180 / Math.PI) + 90; // +90 for SVG orientation
        } else {
          // --- DEPARTURE PHASE ---
          const endOrbitAngle = startAngle + (Math.PI * 2 * direction);
          const startX = Math.cos(endOrbitAngle) * orbitRadiusX;
          const startY = Math.sin(endOrbitAngle) * orbitRadiusY;
          
          const dxOrbit = -Math.sin(endOrbitAngle) * orbitRadiusX * direction;
          const dyOrbit = Math.cos(endOrbitAngle) * orbitRadiusY * direction;
          const mag = Math.sqrt(dxOrbit * dxOrbit + dyOrbit * dyOrbit);
          
          const depProgress = (elapsed - orbitDuration) / (duration - orbitDuration);
          const easeProgress = depProgress * depProgress * depProgress; // Stronger cubic ease for departure acceleration
          
          // Control point follows the tangent of the orbit to make the breakout smooth
          const cpDistance = 300;
          const cpX = startX + (dxOrbit / mag) * cpDistance;
          const cpY = startY + (dyOrbit / mag) * cpDistance;
          
          // Quadratic Bezier interpolation
          const t = easeProgress;
          const mt = 1 - t;
          
          x = mt * mt * startX + 2 * mt * t * cpX + t * t * exitX;
          y = mt * mt * startY + 2 * mt * t * cpY + t * t * exitY;
          
          // Tangent of Bezier for rotation
          const dx = 2 * mt * (cpX - startX) + 2 * t * (exitX - cpX);
          const dy = 2 * mt * (cpY - startY) + 2 * t * (exitY - cpY);
          angle = Math.atan2(dy, dx) * (180 / Math.PI) + 90;
        }
        
        planeRef.current.style.transform = `translate(${x}px, ${y}px) rotate(${angle}deg)`;
      }

      // Smoothly fade out the resume and the overlay background
      if (elapsed > 1600 && resumeRef.current && overlayRef.current) {
        const fadeProgress = Math.min((elapsed - 1600) / 800, 1);
        resumeRef.current.style.opacity = 1 - fadeProgress;
        overlayRef.current.style.opacity = 1 - fadeProgress;
      }

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      } else {
        onCompleteRef.current();
      }
    };

    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, []);

  return (
    <div ref={overlayRef} className="fixed inset-0 z-50 flex items-center justify-center overflow-hidden bg-[#FFF9F3]/90 backdrop-blur-[4px] pointer-events-auto">
      <div className="relative w-32 h-32 flex items-center justify-center">
        <div ref={resumeRef} className="relative">
          <ResumeDoodle className="w-20 h-24 text-[#F9A8D4] animate-float" />
          <SparkleDoodle className="absolute -top-2 -right-4 w-6 h-6 text-[#FDBA9A] animate-twinkle" />
        </div>
        <div ref={planeRef} className="absolute w-12 h-12 flex items-center justify-center" style={{ transformOrigin: 'center' }}>
          <PlaneDoodle className="w-full h-full text-[#F472B6] drop-shadow-md" />
        </div>
      </div>
    </div>
  );
};

const LoadingTransition = ({ statusText }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-hidden bg-[#fffaf5]/90 backdrop-blur-sm animate-fade-in pointer-events-auto">
      {/* Moving clouds overlay */}
      <div className="absolute inset-0 opacity-80 flex flex-col justify-between py-10 pointer-events-none">
        <div className="flex animate-cloud-drift whitespace-nowrap opacity-60 text-[#FCE7F3] space-x-10">
           <CloudDoodle className="w-32 h-20" /><CloudDoodle className="w-40 h-24" /><CloudDoodle className="w-32 h-20" />
        </div>
        <div className="flex animate-cloud-drift whitespace-nowrap opacity-50 text-[#F9A8D4] space-x-20" style={{animationDirection: 'reverse', animationDuration: '25s'}}>
           <CloudDoodle className="w-48 h-32" /><CloudDoodle className="w-32 h-20" />
        </div>
        <div className="flex animate-cloud-drift whitespace-nowrap opacity-40 text-[#FCE7F3] space-x-12">
           <CloudDoodle className="w-40 h-28" /><CloudDoodle className="w-48 h-32" /><CloudDoodle className="w-32 h-24" />
        </div>
      </div>
      
      {/* Center content */}
      <div className="relative z-10 flex flex-col items-center bg-[#fffaf5] p-12 rounded-[3rem] border-2 border-[#FCE7F3] shadow-[0_10px_40px_rgba(244,114,182,0.15)] animate-scale-up" style={{borderRadius: '255px 15px 225px 15px/15px 225px 15px 255px'}}>
        <div className="relative w-32 h-32 flex items-center justify-center mb-6">
          <ResumeDoodle className="absolute w-16 h-20 text-[#F9A8D4] animate-float" />
          <PlaneDoodle className="absolute w-8 h-8 text-[#F472B6] animate-fly" />
          <SparkleDoodle className="absolute top-0 right-0 w-6 h-6 text-[#FDBA9A] animate-twinkle" />
          <SparkleDoodle className="absolute bottom-0 left-0 w-5 h-5 text-[#F9A8D4] animate-twinkle delay-500" />
          <div className="absolute w-28 h-28 border-[3px] border-dashed border-[#FCE7F3] rounded-full animate-spin" style={{animationDuration: '4s'}}></div>
        </div>
        
        <h2 className="text-2xl font-black text-[#40334D] mb-2" style={{fontFamily: "'Comic Sans MS', 'Chalkboard SE', sans-serif"}}>Analyzing Candidate Match</h2>
        <p className="text-[#F472B6] font-bold animate-pulse">{statusText || "Processing..."}</p>
      </div>
    </div>
  );
};

function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  
  // Pipeline State
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [isRevealing, setIsRevealing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState("");
  const [error, setError] = useState(null);
  
  // Result State
  const [candidateProfile, setCandidateProfile] = useState(null);
  const [matchResult, setMatchResult] = useState(null);
  const [scoreResult, setScoreResult] = useState(null);

  const handleAnalyzeClick = async () => {
    if (!resumeFile || !jobDescription.trim()) return;

    setIsLoading(true);
    setError(null);
    setScoreResult(null);
    setCandidateProfile(null);
    setMatchResult(null);

    try {
      setLoadingStatus("Extracting resume information...");
      const parsedCandidateProfile = await parseResume(resumeFile);
      
      setLoadingStatus("Processing job description...");
      const parsedJobProfile = await parseJobDescription(jobDescription);

      setLoadingStatus("Analyzing skills and experience...");
      const parsedMatchResult = await matchCandidate(parsedCandidateProfile, parsedJobProfile);

      setLoadingStatus("Generating insights...");
      const scoreData = await calculateScore(parsedMatchResult, parsedJobProfile);
      
      // Store final state to display success
      setCandidateProfile(parsedCandidateProfile);
      setMatchResult(parsedMatchResult);
      setScoreResult(scoreData);

    } catch (err) {
      console.error("Pipeline Error:", err);
      setError(err.message || "An unexpected error occurred during analysis.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResumeFile(null);
    setJobDescription("");
    setCandidateProfile(null);
    setMatchResult(null);
    setScoreResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-[#FFF9F3] flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8 font-sans selection:bg-[#FCE7F3] overflow-hidden relative">
      
      {isInitialLoad && (
        <InitialLoadTransition 
          onReveal={() => setIsRevealing(true)} 
          onComplete={() => setIsInitialLoad(false)} 
        />
      )}
      
      {isLoading && <LoadingTransition statusText={loadingStatus} />}
      
      <div className={`w-full max-w-6xl bg-white shadow-[0_8px_30px_rgb(244,114,182,0.12)] doodle-border-1 border-[#FFF1F6] transition-all duration-1000 relative z-10 
        ${isLoading ? 'scale-95 opacity-0 blur-sm pointer-events-none' : 'scale-100 opacity-100 blur-0'} 
        ${isInitialLoad && !isRevealing ? 'opacity-40 blur-md scale-[0.98]' : 'opacity-100 blur-0 scale-100'}`}>
        <Header />

        {!scoreResult ? (
          <UploadForm 
            resumeFile={resumeFile}
            setResumeFile={setResumeFile}
            jobDescription={jobDescription}
            setJobDescription={setJobDescription}
            isLoading={isLoading}
            error={error}
            onAnalyze={handleAnalyzeClick}
          />
        ) : (
          <Dashboard 
            candidateProfile={candidateProfile}
            matchResult={matchResult}
            scoreResult={scoreResult}
            onReset={handleReset}
          />
        )}
      </div>
    </div>
  );
}

export default App;
