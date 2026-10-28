import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Stepper } from './components/Stepper';
import { LandingPage } from './modules/landing/LandingPage';
import { JdPage } from './modules/jd/JdPage';
import { ResumePage } from './modules/resume/ResumePage';
import { ProfileForm } from './modules/profile/ProfileForm';
import { TalentPage } from './modules/talent/TalentPage';
import { MatchingPage } from './modules/matching/MatchingPage';
import {
  Compass,
  Sparkles,
  Building,
  FileText,
  Layers,
  Play,
} from 'lucide-react';

const MainLayout: React.FC = () => {
  const { currentStep, setCurrentStep, company, parsedResume, selectedJd } = useApp();

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans selection:bg-brand-500 selection:text-white transition-colors duration-200">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
          {/* Logo & Brand (Clickable -> Returns to Landing Overview) */}
          <button
            onClick={() => setCurrentStep(0)}
            className="flex items-center gap-3 text-left focus:outline-none group cursor-pointer"
            title="Return to Architecture & Overview"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-400 flex items-center justify-center text-white shadow-glow group-hover:scale-105 transition-transform">
              <Compass className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-brand-600 via-brand-500 to-indigo-600 bg-clip-text text-transparent">
                  GapMap
                </h1>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-300 border border-brand-200 dark:border-brand-800">
                  ATS & Skill Gap Engine
                </span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 hidden sm:block">
                Evidence-Based ATS & 3-Layer Skill Gap Analytics
              </p>
            </div>
          </button>

          {/* Nav Controls & Context Pills */}
          <div className="flex items-center gap-3">
            {/* View Switcher: Overview vs Active Pipeline */}
            <div className="flex items-center p-1 rounded-xl bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80">
              <button
                onClick={() => setCurrentStep(0)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                  currentStep === 0
                    ? 'bg-brand-600 text-white shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Overview & Architecture</span>
                <span className="sm:hidden">Overview</span>
              </button>

              <button
                onClick={() => setCurrentStep(currentStep === 0 ? 1 : currentStep)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                  currentStep > 0
                    ? 'bg-brand-600 text-white shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <Play className="w-3.5 h-3.5" />
                <span>Pipeline{currentStep > 0 ? ` (${currentStep}/5)` : ''}</span>
              </button>
            </div>

            {/* Quick Context Pill Indicator (Desktop) */}
            {currentStep > 0 && (
              <div className="hidden lg:flex items-center gap-2 text-xs">
                {selectedJd && (
                  <span className="px-2.5 py-1 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 flex items-center gap-1.5 border border-blue-200 dark:border-blue-800 font-medium text-[11px]">
                    <FileText className="w-3.5 h-3.5 text-blue-500" />
                    JD: {'title' in selectedJd ? selectedJd.title : selectedJd.role || 'Active'}
                  </span>
                )}
                {company && (
                  <span className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 flex items-center gap-1.5 border border-slate-200 dark:border-slate-700 font-medium text-[11px]">
                    <Building className="w-3.5 h-3.5 text-brand-500" />
                    {company.split(' ')[0]}
                  </span>
                )}
                {parsedResume && (
                  <span className="px-2.5 py-1 rounded-lg bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 flex items-center gap-1.5 border border-purple-200 dark:border-purple-800 font-medium text-[11px]">
                    <Sparkles className="w-3.5 h-3.5 text-purple-500" />
                    {parsedResume.skills.length} Skills
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        {currentStep === 0 ? (
          <LandingPage onStartPipeline={() => setCurrentStep(1)} />
        ) : (
          <div className="space-y-8">
            {/* Top Stepper */}
            <Stepper />

            {/* Dynamic Step View */}
            <div className="transition-all duration-300">
              {currentStep === 1 && <JdPage />}
              {currentStep === 2 && <ResumePage />}
              {currentStep === 3 && <ProfileForm />}
              {currentStep === 4 && <TalentPage />}
              {currentStep === 5 && <MatchingPage />}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-slate-200 dark:border-slate-800 py-6 text-center text-xs text-slate-500 dark:text-slate-400">
        <p>GapMap ATS & Skill Gap Engine • Multi-tier Benchmark & Verification Pipeline</p>
        <p className="mt-1 text-[11px] text-slate-400">Connected to FastAPI Backend at http://localhost:8000</p>
      </footer>
    </div>
  );
};

export default function App() {
  return (
    <AppProvider>
      <MainLayout />
    </AppProvider>
  );
}
