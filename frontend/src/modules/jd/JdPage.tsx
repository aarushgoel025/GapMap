import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { getJds, analyzeJd } from '../../api';
import type { SampleJd, ExtractionResult } from '../../types';
import { ArrowRight, Sparkles, Building2, CheckCircle, RefreshCw } from 'lucide-react';

export const JdPage: React.FC = () => {
  const { selectedJd, setSelectedJd, setCurrentStep, setCompany } = useApp();
  const [jds, setJds] = useState<SampleJd[]>([]);
  const [customJdText, setCustomJdText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [analyzedResult, setAnalyzedResult] = useState<ExtractionResult | null>(null);

  useEffect(() => {
    getJds().then(setJds);
  }, []);

  const handleSelect = async (jd: SampleJd) => {
    setIsLoading(true);
    setSelectedJd(jd);
    setCompany(jd.company);
    try {
      const res = await analyzeJd(jd.filename);
      setAnalyzedResult(res);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeCustom = async () => {
    if (!customJdText.trim()) return;
    setIsLoading(true);
    try {
      const res = await analyzeJd(customJdText);
      setAnalyzedResult(res);
      setSelectedJd(res);
      if (res.company) setCompany(res.company);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300">
          Module 1: JD Analytics (Samiksha)
        </span>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">Select or Analyze Job Description</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Pick a target benchmark role to extract required technical competencies, soft skills, and experience criteria.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {jds.map((jd) => {
          const isSelected = selectedJd && 'id' in selectedJd && selectedJd.id === jd.id;
          return (
            <div
              key={jd.id}
              onClick={() => handleSelect(jd)}
              className={`p-5 rounded-2xl border cursor-pointer transition-all ${
                isSelected
                  ? 'border-brand-500 bg-brand-50/40 dark:bg-brand-950/20 ring-2 ring-brand-500/30'
                  : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-brand-300'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-brand-600">
                  <Building2 className="w-5 h-5" />
                </span>
                {isSelected && <CheckCircle className="w-5 h-5 text-brand-600" />}
              </div>
              <h4 className="font-bold text-slate-900 dark:text-white text-base">{jd.title}</h4>
              <p className="text-xs font-semibold text-brand-600 dark:text-brand-400 mt-0.5">{jd.company}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 line-clamp-2">{jd.snippet}</p>
            </div>
          );
        })}
      </div>

      {/* Or Paste Raw Text */}
      <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-2">Or Paste Custom Job Description</h4>
        <textarea
          rows={3}
          value={customJdText}
          onChange={(e) => setCustomJdText(e.target.value)}
          placeholder="Paste Job Description requirements, qualifications, and role specifics..."
          className="w-full p-3 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        <div className="flex justify-end mt-3">
          <button
            onClick={handleAnalyzeCustom}
            disabled={isLoading || !customJdText.trim()}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold bg-brand-600 text-white rounded-xl hover:bg-brand-500 disabled:opacity-40"
          >
            {isLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
            Analyze Custom JD
          </button>
        </div>
      </div>

      {/* Analysis Results Preview */}
      {analyzedResult && (
        <div className="bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800 p-5 rounded-2xl animate-fadeIn">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="w-4 h-4 text-emerald-600" />
            <h4 className="text-sm font-bold text-emerald-900 dark:text-emerald-300">
              Extracted {analyzedResult.skills.length} Required Competencies for {analyzedResult.company || 'Role'}
            </h4>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-3">
            {analyzedResult.skills.map((s, i) => (
              <span
                key={i}
                className="text-xs px-2.5 py-1 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-emerald-200 dark:border-emerald-800 font-medium"
              >
                {s.skill_name} ({s.category_code})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Stepper Forward */}
      <div className="flex justify-end pt-4 border-t border-slate-200 dark:border-slate-800">
        <button
          onClick={() => setCurrentStep(2)}
          className="flex items-center gap-2 px-6 py-2.5 text-sm font-semibold text-white bg-slate-900 dark:bg-white dark:text-slate-900 rounded-xl hover:opacity-90 transition-all shadow-md"
        >
          Proceed to Step 2: Resume
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
