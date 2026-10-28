import React, { useState, useEffect, useRef } from 'react';
import { useApp } from '../../context/AppContext';
import { getJds, analyzeJd, uploadJdFile } from '../../api';
import type { SampleJd, ExtractionResult, Skill } from '../../types';
import {
  ArrowRight,
  Sparkles,
  Building2,
  CheckCircle,
  RefreshCw,
  UploadCloud,
  AlertTriangle,
  ShieldCheck,
  Check,
  Info,
  RotateCcw,
  Briefcase,
  X,
} from 'lucide-react';

export const JdPage: React.FC = () => {
  const { selectedJd, setSelectedJd, setCurrentStep, setCompany } = useApp();
  const [jds, setJds] = useState<SampleJd[]>([]);
  const [selectedJdId, setSelectedJdId] = useState<string>('jd-1');
  const [customJdText, setCustomJdText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [analyzedResult, setAnalyzedResult] = useState<ExtractionResult | null>(
    selectedJd && 'skills' in selectedJd ? (selectedJd as ExtractionResult) : null
  );

  // When a JD is selected/analyzed, the picker collapses so the screen stays clean
  const [isPickerOpen, setIsPickerOpen] = useState<boolean>(!selectedJd);

  const [inputMode, setInputMode] = useState<'sample' | 'upload' | 'text'>('sample');
  const [skillFilter, setSkillFilter] = useState<'all' | 'must_have' | 'nice_to_have' | 'disagreements'>('all');

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    getJds().then((list) => {
      setJds(list);
    });
  }, []);

  const handleSelect = async (jd: SampleJd) => {
    setIsLoading(true);
    setErrorMessage(null);
    setSelectedJd(jd);
    setSelectedJdId(jd.id);
    setCompany(jd.company);
    try {
      const res = await analyzeJd(jd.filename);
      setAnalyzedResult(res);
      setSelectedJd(res);
      if (res.company) setCompany(res.company);
      setIsPickerOpen(false); // Hide demo cards once selected!
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to analyze selected sample JD.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'pdf' && ext !== 'docx') {
      setErrorMessage('Unsupported file format. Please upload a .pdf or .docx Job Description.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    try {
      const res = await uploadJdFile(file);
      setAnalyzedResult(res);
      setSelectedJd(res);
      if (res.company) setCompany(res.company);
      setIsPickerOpen(false); // Hide upload card once uploaded!
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to extract skills from uploaded file. Please verify backend connection.');
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleAnalyzeCustom = async () => {
    if (!customJdText.trim()) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const res = await analyzeJd(customJdText);
      setAnalyzedResult(res);
      setSelectedJd(res);
      if (res.company) setCompany(res.company);
      setIsPickerOpen(false); // Hide custom text once analyzed!
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to analyze custom JD text.');
    } finally {
      setIsLoading(false);
    }
  };

  const skills = analyzedResult?.skills || [];
  const disagreements = (analyzedResult?.extras?.disagreements as any[]) || [];
  const mustHaves = skills.filter((s) => s.importance === 'must_have');
  const niceToHaves = skills.filter((s) => s.importance === 'nice_to_have');
  const agreedCount = skills.filter((s) => s.models_agree === true).length;
  const agreementRate = skills.length > 0 ? Math.round((agreedCount / skills.length) * 100) : 100;

  const filteredSkills = skills.filter((s) => {
    if (skillFilter === 'must_have') return s.importance === 'must_have';
    if (skillFilter === 'nice_to_have') return s.importance === 'nice_to_have';
    return true;
  });

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Header Banner */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300">
            Module 1: JD Analytics
          </span>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
            Job Description & Target Role Analytics
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Extract competencies, importance levels, and evidence quotes via parallel Gemini & Mistral LLM analysis.
          </p>
        </div>

        {/* Input Mode Selector (Visible when picker is open) */}
        {isPickerOpen && (
          <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-xl self-start md:self-auto border border-slate-200 dark:border-slate-700">
            <button
              onClick={() => setInputMode('sample')}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                inputMode === 'sample'
                  ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              Demo Roles ({jds.length})
            </button>
            <button
              onClick={() => setInputMode('upload')}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                inputMode === 'upload'
                  ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              Upload Real File
            </button>
            <button
              onClick={() => setInputMode('text')}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                inputMode === 'text'
                  ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              Paste Text
            </button>
          </div>
        )}
      </div>

      {/* Error Banner */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/50 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-xs font-semibold text-rose-800 dark:text-rose-200">Processing Notice</p>
            <p className="text-xs text-rose-700 dark:text-rose-300 mt-0.5">{errorMessage}</p>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-rose-400 hover:text-rose-600 dark:hover:text-rose-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Active Selected JD Banner (Shows when a JD is active, with button to switch/browse demos) */}
      {analyzedResult && !isPickerOpen && (
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-brand-200 dark:border-brand-900/60 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white flex items-center justify-center shadow-md shrink-0">
              <Briefcase className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  {analyzedResult.role || 'Job Description Analysis'}
                </h3>
                {analyzedResult.company && (
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-brand-50 dark:bg-brand-950 text-brand-700 dark:text-brand-300 border border-brand-200 dark:border-brand-800">
                    {analyzedResult.company}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-2">
                <span>
                  Source: <strong className="font-mono text-slate-700 dark:text-slate-300">{analyzedResult.source_file}</strong>
                </span>
                <span>•</span>
                <span className="text-emerald-600 dark:text-emerald-400 font-semibold">{skills.length} skills extracted</span>
              </p>
            </div>
          </div>

          <button
            onClick={() => setIsPickerOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all self-start sm:self-auto cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Switch JD / Browse Demos</span>
          </button>
        </div>
      )}

      {/* JD Picker Section: Demo Roles, Upload, or Text (Hides when a JD is active unless opened) */}
      {isPickerOpen && (
        <div className="space-y-4 animate-fadeIn">
          {analyzedResult && (
            <div className="flex justify-between items-center px-1">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Choose a demo JD or upload your custom job description:
              </span>
              <button
                onClick={() => setIsPickerOpen(false)}
                className="text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 flex items-center gap-1 cursor-pointer"
              >
                <span>Close (Keep Current JD)</span>
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* 1. Demo JDs Grid */}
          {inputMode === 'sample' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {jds.map((jd) => {
                const isSelected =
                  selectedJdId === jd.id ||
                  (analyzedResult && analyzedResult.source_file === jd.filename);
                return (
                  <div
                    key={jd.id}
                    onClick={() => handleSelect(jd)}
                    className={`p-5 rounded-2xl border cursor-pointer transition-all relative ${
                      isSelected
                        ? 'border-brand-500 bg-brand-50/40 dark:bg-brand-950/20 ring-2 ring-brand-500/30'
                        : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-brand-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="p-2 rounded-xl bg-brand-100 dark:bg-brand-950 text-brand-600">
                        <Building2 className="w-5 h-5" />
                      </span>
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
                          Pre-cached
                        </span>
                        {isSelected && <CheckCircle className="w-5 h-5 text-brand-600" />}
                      </div>
                    </div>
                    <h4 className="font-bold text-slate-900 dark:text-white text-base">{jd.title}</h4>
                    <p className="text-xs font-semibold text-brand-600 dark:text-brand-400 mt-0.5">{jd.company}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 line-clamp-2">{jd.snippet}</p>
                    <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-3 font-mono">
                      {jd.filename}
                    </p>
                  </div>
                );
              })}
            </div>
          )}

          {/* 2. File Upload Mode */}
          {inputMode === 'upload' && (
            <div className="bg-white dark:bg-slate-900 p-8 rounded-2xl border border-dashed border-slate-300 dark:border-slate-700 text-center">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept=".pdf,.docx"
                className="hidden"
              />
              <div className="max-w-md mx-auto space-y-3">
                <div className="w-12 h-12 rounded-2xl bg-brand-50 dark:bg-brand-950 text-brand-600 mx-auto flex items-center justify-center">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Upload Benchmark Job Description
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Drag and drop any official role description in <code className="text-brand-600">.pdf</code> or{' '}
                  <code className="text-brand-600">.docx</code> format. Our document reader parses tables & text orders cleanly.
                </p>
                <div className="pt-2">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isLoading}
                    className="px-5 py-2.5 text-xs font-semibold text-white bg-brand-600 rounded-xl hover:bg-brand-500 transition-all shadow-sm disabled:opacity-50 cursor-pointer"
                  >
                    {isLoading ? 'Extracting Text & Skills...' : 'Select File from Device'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* 3. Paste Custom Text Mode */}
          {inputMode === 'text' && (
            <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">
                  Paste Raw Job Description Content
                </h4>
                <span className="text-xs text-slate-400">Max 30,000 chars</span>
              </div>
              <textarea
                rows={5}
                value={customJdText}
                onChange={(e) => setCustomJdText(e.target.value)}
                placeholder="Paste raw JD responsibilities, requirements, minimum qualifications, and nice-to-haves..."
                className="w-full p-3.5 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <div className="flex justify-end">
                <button
                  onClick={handleAnalyzeCustom}
                  disabled={isLoading || !customJdText.trim()}
                  className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold bg-brand-600 text-white rounded-xl hover:bg-brand-500 disabled:opacity-40 transition-all shadow-sm cursor-pointer"
                >
                  {isLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                  Analyze Custom JD
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Loading Animation */}
      {isLoading && (
        <div className="p-8 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center animate-pulse">
          <RefreshCw className="w-8 h-8 text-brand-600 mx-auto animate-spin mb-3" />
          <h4 className="text-sm font-bold text-slate-900 dark:text-white">
            Running Dual-Model AI Extraction
          </h4>
          <p className="text-xs text-slate-500 mt-1">
            Querying Gemini & Mistral in parallel, normalizing categories, and cross-validating requirements...
          </p>
        </div>
      )}

      {/* Extraction Results Preview */}
      {analyzedResult && !isLoading && (
        <div className="space-y-4 animate-fadeIn">
          {/* Metadata & Confidence Metrics Bar */}
          <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  {analyzedResult.role || 'Job Description Analysis'}{' '}
                  {analyzedResult.company && (
                    <span className="text-slate-400 font-normal">at {analyzedResult.company}</span>
                  )}
                </h3>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Source: <span className="font-mono">{analyzedResult.source_file}</span>
              </p>
            </div>

            <div className="flex items-center gap-4 text-xs">
              <div className="text-right">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Total Skills</span>
                <span className="font-bold text-slate-900 dark:text-white text-sm">{skills.length}</span>
              </div>
              <div className="h-6 w-px bg-slate-200 dark:bg-slate-800" />
              <div className="text-right">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Must Have</span>
                <span className="font-bold text-emerald-600 text-sm">{mustHaves.length}</span>
              </div>
              <div className="h-6 w-px bg-slate-200 dark:bg-slate-800" />
              <div className="text-right">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Nice to Have</span>
                <span className="font-bold text-blue-600 text-sm">{niceToHaves.length}</span>
              </div>
              <div className="h-6 w-px bg-slate-200 dark:bg-slate-800" />
              <div className="text-right">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Dual-AI Agreement</span>
                <span className="font-bold text-brand-600 text-sm">{agreementRate}%</span>
              </div>
            </div>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center justify-between gap-2">
            <div className="flex gap-2">
              <button
                onClick={() => setSkillFilter('all')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-xl border transition-all ${
                  skillFilter === 'all'
                    ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 border-transparent shadow-sm'
                    : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-800'
                }`}
              >
                All Skills ({skills.length})
              </button>
              <button
                onClick={() => setSkillFilter('must_have')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-xl border transition-all ${
                  skillFilter === 'must_have'
                    ? 'bg-emerald-600 text-white border-transparent shadow-sm'
                    : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-800'
                }`}
              >
                Must-Have ({mustHaves.length})
              </button>
              <button
                onClick={() => setSkillFilter('nice_to_have')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-xl border transition-all ${
                  skillFilter === 'nice_to_have'
                    ? 'bg-blue-600 text-white border-transparent shadow-sm'
                    : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-800'
                }`}
              >
                Nice-to-Have ({niceToHaves.length})
              </button>
              {disagreements.length > 0 && (
                <button
                  onClick={() => setSkillFilter('disagreements')}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-xl border transition-all ${
                    skillFilter === 'disagreements'
                      ? 'bg-amber-600 text-white border-transparent shadow-sm'
                      : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-800'
                  }`}
                >
                  Model Disagreements ({disagreements.length})
                </button>
              )}
            </div>
            <span className="text-xs text-slate-400 hidden sm:inline">
              12 Category Taxonomies Standardized
            </span>
          </div>

          {/* Disagreements Card if selected */}
          {skillFilter === 'disagreements' && disagreements.length > 0 && (
            <div className="bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/40 p-4 rounded-2xl space-y-2">
              <h5 className="text-xs font-bold text-amber-900 dark:text-amber-300 flex items-center gap-1.5">
                <Info className="w-4 h-4 text-amber-600" />
                Category Disagreements Resolved
              </h5>
              <p className="text-xs text-amber-800 dark:text-amber-400">
                Gemini and Mistral categorized the following skills under different codes. The pipeline preserved Gemini&apos;s category and adjusted confidence accordingly:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                {disagreements.map((d, i) => (
                  <div key={i} className="text-xs bg-white dark:bg-slate-900 p-2.5 rounded-xl border border-amber-200 dark:border-amber-900/40">
                    <span className="font-semibold text-slate-900 dark:text-white">{d.skill}</span>:
                    <span className="text-slate-500 ml-1">
                      Gemini categorized as <span className="font-bold text-emerald-600">{d.gemini_category}</span> vs Mistral <span className="font-bold text-blue-600">{d.mistral_category}</span>
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Skills Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {filteredSkills.map((s: Skill, i: number) => {
              const isMust = s.importance === 'must_have';
              return (
                <div
                  key={i}
                  className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm hover:border-brand-300 transition-all flex flex-col justify-between space-y-2"
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-bold text-slate-900 dark:text-white text-sm">
                      {s.skill_name}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 shrink-0">
                      {s.category_code}
                    </span>
                  </div>

                  {s.evidence && (
                    <p className="text-xs text-slate-500 dark:text-slate-400 italic line-clamp-2">
                      &quot;{s.evidence}&quot;
                    </p>
                  )}

                  <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800 text-[10px]">
                    <span
                      className={`px-2 py-0.5 rounded-full font-semibold ${
                        isMust
                          ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300'
                          : 'bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300'
                      }`}
                    >
                      {isMust ? 'Must-Have' : 'Nice-to-Have'}
                    </span>

                    <div className="flex items-center gap-1.5 text-slate-400">
                      <span className="capitalize">{s.confidence} conf</span>
                      {s.models_agree === true && (
                        <span className="text-emerald-600 flex items-center gap-0.5 font-medium" title="Dual-Model Agreement">
                          <Check className="w-3 h-3" /> Both AI
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Stepper Forward Navigation */}
      <div className="flex justify-between items-center pt-6 border-t border-slate-200 dark:border-slate-800">
        <span className="text-xs text-slate-500">
          Selected Target:{' '}
          <span className="font-semibold text-slate-900 dark:text-white">
            {analyzedResult?.company || (selectedJd && 'company' in selectedJd ? selectedJd.company : 'Company')}{' '}
            - {analyzedResult?.role || (selectedJd && 'title' in selectedJd ? selectedJd.title : 'Role')}
          </span>
        </span>
        <button
          onClick={() => setCurrentStep(2)}
          className="flex items-center gap-2 px-6 py-2.5 text-sm font-semibold text-white bg-slate-900 dark:bg-white dark:text-slate-900 rounded-xl hover:opacity-90 transition-all shadow-md cursor-pointer"
        >
          Proceed to Step 2: Resume
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
