import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { getResumes, parseResume } from '../../api';
import type { SampleResume } from '../../types';
import { FileCode, ArrowRight, ArrowLeft, Sparkles, CheckCircle, RefreshCw, UploadCloud } from 'lucide-react';

export const ResumePage: React.FC = () => {
  const { parsedResume, setParsedResume, setCurrentStep } = useApp();
  const [resumes, setResumes] = useState<SampleResume[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string>('res-1');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    getResumes().then(setResumes);
  }, []);

  const handleParse = async (resume: SampleResume) => {
    setIsLoading(true);
    setSelectedResumeId(resume.id);
    try {
      const result = await parseResume(resume.filename);
      setParsedResume(result);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300">
          Module 2: Resume Parsing (Arushi)
        </span>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">Extract & Parse Candidate Resume</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Parses candidate resume PDFs, extracting verified skills, education, project deliverables, and work experience.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {resumes.map((res) => {
          const isSelected = selectedResumeId === res.id;
          return (
            <div
              key={res.id}
              onClick={() => handleParse(res)}
              className={`p-5 rounded-2xl border cursor-pointer transition-all ${
                isSelected
                  ? 'border-brand-500 bg-brand-50/40 dark:bg-brand-950/20 ring-2 ring-brand-500/30'
                  : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-brand-300'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-brand-600">
                  <FileCode className="w-5 h-5" />
                </span>
                {isSelected && parsedResume && <CheckCircle className="w-5 h-5 text-brand-600" />}
              </div>
              <h4 className="font-bold text-slate-900 dark:text-white text-base">{res.candidate_name}</h4>
              <p className="text-xs font-semibold text-brand-600 dark:text-brand-400 mt-0.5">{res.role}</p>
              <p className="text-xs text-slate-400 mt-2 font-mono">{res.filename}</p>
            </div>
          );
        })}
      </div>

      {/* Parse Action Banner */}
      <div className="p-6 rounded-2xl border border-brand-200 dark:border-brand-900 bg-gradient-to-r from-brand-50/80 to-indigo-50/60 dark:from-brand-950/30 dark:to-indigo-950/30 flex flex-col sm:flex-row justify-between items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-brand-600 text-white rounded-xl shadow-glow">
            <UploadCloud className="w-6 h-6" />
          </div>
          <div>
            <h4 className="font-bold text-slate-900 dark:text-white text-sm">
              {parsedResume ? 'Resume Parsed & Ready to Populate Profile' : 'Select a Resume to Parse'}
            </h4>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              {parsedResume
                ? `Extracted ${parsedResume.skills.length} skills, education, and credentials.`
                : 'Click any sample above to trigger LLM parsing.'}
            </p>
          </div>
        </div>

        <button
          onClick={() => {
            const first = resumes[0];
            if (first) handleParse(first);
          }}
          disabled={isLoading}
          className="flex items-center gap-2 px-5 py-2 text-xs font-semibold bg-brand-600 text-white hover:bg-brand-500 rounded-xl transition-all shadow-sm"
        >
          {isLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          Re-Parse Sample Resume
        </button>
      </div>

      {/* Stepper Navigation */}
      <div className="flex justify-between items-center pt-4 border-t border-slate-200 dark:border-slate-800">
        <button
          onClick={() => setCurrentStep(1)}
          className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
        >
          <ArrowLeft className="w-4 h-4" /> Back to JD
        </button>

        <button
          onClick={() => setCurrentStep(3)}
          className="flex items-center gap-2 px-6 py-2.5 text-sm font-semibold text-white bg-slate-900 dark:bg-white dark:text-slate-900 rounded-xl hover:opacity-90 transition-all shadow-md"
        >
          Proceed to Step 3: Candidate Profile Form
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
