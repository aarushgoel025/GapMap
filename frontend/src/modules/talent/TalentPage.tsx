import React, { useCallback, useState, useEffect, useRef, useMemo } from 'react';
import { useApp } from '../../context/AppContext';
import { getCompanies, checkTalent, checkTalentWhatIf } from '../../api';
import type { TalentCheckResult, CompanyInfo, Profile } from '../../types';
import {
  Target,
  ArrowRight,
  ArrowLeft,
  Building,
  Zap,
  Search,
  X,
  RotateCcw,
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  Sliders,
  User,
  Sparkles,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

const CATEGORY_NAMES: Record<string, string> = {
  COD: 'Coding & Programming',
  DSA: 'Data Structures & Algorithms',
  OOD: 'Object-Oriented Design',
  APTI: 'Aptitude & Problem Solving',
  COMM: 'Technical Communication',
  AI: 'Artificial Intelligence & ML',
  CLOUD: 'DevOps & Cloud Computing',
  SQL: 'Databases & SQL Architecture',
  SWE: 'Software Engineering Practices',
  SYSD: 'System Design & Scalability',
  NETW: 'Computer Networking',
  OS: 'Operating Systems & Kernels',
};

const BENCHMARK_CANDIDATES = [
  { id: 'active_resume', name: 'Active Uploaded Resume / Profile' },
  { id: 'candidate_1_all_rounder', name: 'Alex Chen (All-Rounder)' },
  { id: 'candidate_2_data_analyst', name: 'Maya Patel (Data Analyst)' },
  { id: 'candidate_3_oracle_support', name: 'Liam Rodriguez (Oracle Support)' },
  { id: 'candidate_4_systems_engineer', name: 'Marcus Vance (Systems Eng - Stuffed)' },
];

const TOP_COMPANIES = [
  'Google LLC (Subsidiary of Alphabet Inc.)',
  'Microsoft Corporation',
  'Oracle India Private Limited',
  'Amazon.com, Inc.',
  'Apple Inc.',
  'Adobe Inc.',
];

export const TalentPage: React.FC = () => {
  const { company, setCompany, currentProfile, parsedResume, setCurrentStep, selectedJd } = useApp();

  const [companies, setCompanies] = useState<CompanyInfo[]>([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>('active_resume');
  const [result, setResult] = useState<TalentCheckResult | null>(null);
  const [, setIsLoading] = useState(false);

  // Company Search & Dropdown State
  const [companySearch, setCompanySearch] = useState('');
  const [isCompanyDropdownOpen, setIsCompanyDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // What-If Sliders State: map of category_code -> simulated level (0-10)
  const [simulatedLevels, setSimulatedLevels] = useState<Record<string, number>>({});

  // Baseline levels (from actual candidate profile before simulation)
  const [baselineLevels, setBaselineLevels] = useState<Record<string, number>>({});

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsCompanyDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Determine effective profile to evaluate
  const effectiveProfile = useMemo<Profile | null>(() => {
    if (selectedCandidateId !== 'active_resume') return null;

    if (currentProfile && currentProfile.skills && currentProfile.skills.length > 0) {
      return currentProfile;
    }

    if (parsedResume && parsedResume.skills && parsedResume.skills.length > 0) {
      const extraObj = (parsedResume.extras || {}) as Record<string, any>;
      return {
        name: extraObj.candidate_name || extraObj.name || 'Active Candidate',
        email: extraObj.email || '',
        education: extraObj.education || '',
        skills: parsedResume.skills,
        hackathons: [],
        internships: [],
        certifications: extraObj.certifications || [],
        preferred_roles: parsedResume.role ? [parsedResume.role] : [],
        cv_file: parsedResume.source_file,
      };
    }

    return null;
  }, [selectedCandidateId, currentProfile, parsedResume]);

  // Load companies list on mount
  useEffect(() => {
    let active = true;
    const fetchCompanies = async () => {
      try {
        const list = await getCompanies();
        if (!active) return;
        setCompanies(list);

        // If currently selected company is not in list, pick Microsoft or first available
        if (list.length > 0 && !list.some((c) => c.name === company)) {
          const defaultComp =
            list.find((c) => c.name.includes('Microsoft'))?.name ||
            list.find((c) => c.name.includes('Google'))?.name ||
            list[0].name;
          setCompany(defaultComp);
        }
      } catch (err) {
        console.error('Failed to load companies:', err);
      }
    };
    void fetchCompanies();
    return () => {
      active = false;
    };
  }, []);

  // Run baseline talent check evaluation whenever company or candidate changes
  const runEvaluation = useCallback(
    async (compName: string, candId: string, prof: Profile | null) => {
      if (!compName) return;
      setIsLoading(true);
      try {
        let payload: { company: string; profile_id?: string; profile?: Profile };

        if (candId === 'active_resume') {
          if (prof) {
            payload = { company: compName, profile: prof };
          } else {
            // Fallback to candidate_1 if no resume has been uploaded yet
            payload = { company: compName, profile_id: 'candidate_1_all_rounder' };
          }
        } else {
          payload = { company: compName, profile_id: candId };
        }

        const data = await checkTalent(payload);
        setResult(data);

        // Initialize baseline levels and reset sliders
        const initialMap: Record<string, number> = {};
        data.skillset_gap.forEach((gap) => {
          initialMap[gap.category_code] = gap.candidate_level;
        });
        setBaselineLevels(initialMap);
        setSimulatedLevels(initialMap);
      } catch (error) {
        console.error('Talent check evaluation error:', error);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    if (companies.length > 0 && company) {
      void runEvaluation(company, selectedCandidateId, effectiveProfile);
    }
  }, [companies, company, selectedCandidateId, effectiveProfile, runEvaluation]);

  // Filtered companies for search combobox
  const filteredCompanies = useMemo(() => {
    if (!companySearch.trim()) return companies;
    const query = companySearch.toLowerCase();
    return companies.filter((c) => c.name.toLowerCase().includes(query));
  }, [companies, companySearch]);

  // Handle slider change for a single category
  const handleSliderChange = (categoryCode: string, newLevel: number) => {
    setSimulatedLevels((prev) => ({
      ...prev,
      [categoryCode]: newLevel,
    }));
  };

  // Check if any slider is currently modified from baseline
  const isSimulated = useMemo(() => {
    return Object.keys(simulatedLevels).some(
      (code) => simulatedLevels[code] !== baselineLevels[code]
    );
  }, [simulatedLevels, baselineLevels]);

  // Client-side instantaneous preview of simulated readiness score & stats
  const simulatedStats = useMemo(() => {
    if (!result) return null;

    let totalMatched = 0;
    let totalRequired = 0;
    let totalMissing = 0;
    let modifiedCount = 0;

    const updatedGaps = result.skillset_gap.map((gap) => {
      const code = gap.category_code;
      const simLevel = simulatedLevels[code] !== undefined ? simulatedLevels[code] : gap.candidate_level;
      const baseLevel = baselineLevels[code] !== undefined ? baselineLevels[code] : gap.candidate_level;
      const required = gap.required_level;

      if (simLevel !== baseLevel) {
        modifiedCount++;
      }

      const matched = Math.min(simLevel, required);
      totalMatched += matched;
      totalRequired += required;
      totalMissing += Math.max(0, required - simLevel);

      return {
        ...gap,
        simulated_level: simLevel,
        is_modified: simLevel !== baseLevel,
        delta_level: simLevel - baseLevel,
        bar_met: simLevel >= required,
        simulated_gap: Math.max(0, required - simLevel),
      };
    });

    const simScore = totalRequired > 0 ? (100 * totalMatched) / totalRequired : 0;
    const baseScore = result.readiness_score;
    const scoreDelta = simScore - baseScore;

    let simLabel = 'Not yet';
    if (simScore >= 80) simLabel = 'Ready';
    else if (simScore >= 60) simLabel = 'Almost there';

    return {
      score: Math.round(simScore * 10) / 10,
      baseScore: Math.round(baseScore * 10) / 10,
      scoreDelta: Math.round(scoreDelta * 10) / 10,
      label: simLabel,
      weeksEstimate: simLabel === 'Ready' ? 0 : totalMissing,
      gaps: updatedGaps,
      modifiedCount,
      totalMissing,
    };
  }, [result, simulatedLevels, baselineLevels]);

  // Debounced backend sync for what-if
  useEffect(() => {
    if (!isSimulated || !result) return;

    const timer = setTimeout(async () => {
      const changes = Object.keys(simulatedLevels)
        .filter((code) => simulatedLevels[code] !== baselineLevels[code])
        .map((code) => ({
          category_code: code,
          new_level: simulatedLevels[code],
        }));

      if (changes.length === 0) return;

      try {
        let payload: {
          company: string;
          profile_id?: string;
          profile?: Profile;
          changes: { category_code: string; new_level: number }[];
        };

        if (selectedCandidateId === 'active_resume') {
          if (effectiveProfile) {
            payload = { company, profile: effectiveProfile, changes };
          } else {
            payload = { company, profile_id: 'candidate_1_all_rounder', changes };
          }
        } else {
          payload = { company, profile_id: selectedCandidateId, changes };
        }

        const whatifResult = await checkTalentWhatIf(payload);
        if (whatifResult) {
          // Keep backend synchronized
          setResult((prev) => (prev ? { ...prev, ...whatifResult } : whatifResult));
        }
      } catch (e) {
        console.warn('What-If backend sync failed (using live client calculation):', e);
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [simulatedLevels, isSimulated, company, selectedCandidateId, effectiveProfile, baselineLevels]);

  // Reset all sliders back to baseline
  const handleResetSimulation = () => {
    setSimulatedLevels({ ...baselineLevels });
  };

  // Max out met skills
  const handleMeetAllGaps = () => {
    if (!result) return;
    const allMet: Record<string, number> = {};
    result.skillset_gap.forEach((g) => {
      allMet[g.category_code] = Math.max(g.candidate_level, g.required_level);
    });
    setSimulatedLevels(allMet);
  };

  const currentScore = simulatedStats ? simulatedStats.score : result ? result.readiness_score : 0;
  const currentLabel = simulatedStats ? simulatedStats.label : result ? result.label : 'Evaluating';
  const currentWeeks =
    simulatedStats !== null
      ? simulatedStats.weeksEstimate
      : result?.weeks_to_ready_estimate ?? null;

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Header Banner */}
      <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300">
              Module 4: Talent Check (Aditya)
            </span>
            <span className="text-xs text-slate-400">•</span>
            <span className="text-xs font-semibold text-slate-500">Pillar 2: Live What-If Simulator</span>
          </div>
          <h2 className="text-2xl font-black text-slate-900 dark:text-white mt-1 tracking-tight">
            Company Talent Readiness Benchmark
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 max-w-2xl">
            Compares candidate skills against company hiring bars across all 12 standardized categories.
            Drag the sliders to simulate skill leveling and watch the score recalculate live!
          </p>
        </div>

        {isSimulated && (
          <button
            onClick={handleResetSimulation}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30 hover:bg-amber-500/20 transition-all shadow-sm cursor-pointer self-start md:self-auto"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset All Sliders
          </button>
        )}
      </div>

      {/* Candidate Profile Switcher Bar */}
      <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <User className="w-4 h-4 text-brand-600 dark:text-brand-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Candidate Profile:</span>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {BENCHMARK_CANDIDATES.map((cand) => {
            const isSelected = selectedCandidateId === cand.id;
            const isUploaded = cand.id === 'active_resume';
            const hasUploadedData = Boolean(effectiveProfile);

            return (
              <button
                key={cand.id}
                onClick={() => setSelectedCandidateId(cand.id)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-xl transition-all flex items-center gap-1.5 ${
                  isSelected
                    ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-sm'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                }`}
              >
                {cand.name}
                {isUploaded && (
                  <span
                    className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                      hasUploadedData
                        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                        : 'bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-400'
                    }`}
                  >
                    {hasUploadedData ? `${effectiveProfile?.skills?.length || 0} skills` : 'Empty (Upload in Step 2)'}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Searchable Company Selector (Replaces the 163-pill button wall) */}
      <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <Building className="w-4 h-4 text-brand-600 dark:text-brand-400" />
            Target Hiring Company ({companies.length} Companies in Benchmark DB):
          </label>
          {selectedJd && 'company' in selectedJd && selectedJd.company && (
            <span className="text-[11px] text-brand-600 dark:text-brand-400 font-semibold bg-brand-50 dark:bg-brand-950/60 px-2.5 py-1 rounded-lg border border-brand-200 dark:border-brand-800">
              🎯 Synced from Step 1 JD: {selectedJd.company}
            </span>
          )}
        </div>

        {/* Search Combobox Input */}
        <div className="relative" ref={dropdownRef}>
          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                value={companySearch}
                onChange={(e) => {
                  setCompanySearch(e.target.value);
                  setIsCompanyDropdownOpen(true);
                }}
                onFocus={() => setIsCompanyDropdownOpen(true)}
                placeholder={`Current: ${company} — Type to search companies...`}
                className="w-full pl-10 pr-10 py-2.5 text-xs font-semibold rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all"
              />
              {companySearch && (
                <button
                  onClick={() => setCompanySearch('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            <button
              onClick={() => setIsCompanyDropdownOpen((prev) => !prev)}
              className="px-4 py-2.5 text-xs font-bold rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center gap-1.5 transition-all"
            >
              <span>{isCompanyDropdownOpen ? 'Close List' : 'Browse All'}</span>
              {isCompanyDropdownOpen ? (
                <ChevronUp className="w-3.5 h-3.5 text-slate-500" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
              )}
            </button>
          </div>

          {/* Scrollable Dropdown Menu */}
          {isCompanyDropdownOpen && (
            <div className="absolute z-30 left-0 right-0 mt-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl shadow-2xl max-h-60 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800">
              <div className="p-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider bg-slate-50 dark:bg-slate-800/60 sticky top-0 backdrop-blur-sm">
                Showing {filteredCompanies.length} matches (click to select)
              </div>
              {filteredCompanies.length === 0 ? (
                <div className="p-4 text-center text-xs text-slate-500">
                  No company matching &quot;{companySearch}&quot; found.
                </div>
              ) : (
                filteredCompanies.map((c) => {
                  const isCurrent = company === c.name;
                  return (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => {
                        setCompany(c.name);
                        setCompanySearch('');
                        setIsCompanyDropdownOpen(false);
                      }}
                      className={`w-full text-left px-4 py-2.5 text-xs flex items-center justify-between hover:bg-brand-50 dark:hover:bg-brand-950/40 transition-colors ${
                        isCurrent
                          ? 'bg-brand-100/60 dark:bg-brand-950 text-brand-700 dark:text-brand-300 font-bold'
                          : 'text-slate-700 dark:text-slate-300 font-medium'
                      }`}
                    >
                      <span>{c.name}</span>
                      {isCurrent && <CheckCircle2 className="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />}
                    </button>
                  );
                })
              )}
            </div>
          )}
        </div>

        {/* Quick select chips for top benchmark companies */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          <span className="text-[11px] font-semibold text-slate-400 mr-1">Popular:</span>
          {TOP_COMPANIES.map((topName) => {
            const isCurrent = company === topName;
            const shortLabel = topName.split(' ')[0].replace('.', '');
            return (
              <button
                key={topName}
                onClick={() => setCompany(topName)}
                className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg transition-all ${
                  isCurrent
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700'
                }`}
              >
                {shortLabel}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Readiness & What-If Layout */}
      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Live Score Gauge & Summary Card */}
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-gradient-to-br from-slate-900 via-slate-850 to-slate-800 text-white p-6 rounded-2xl shadow-xl flex flex-col justify-between border border-slate-700 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-brand-500/10 rounded-full blur-2xl pointer-events-none" />

              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-brand-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Zap className="w-3.5 h-3.5 text-amber-400" />
                    Talent Readiness Score
                  </span>
                  {isSimulated && (
                    <span className="px-2 py-0.5 text-[10px] font-black rounded-full bg-cyan-500 text-slate-950 uppercase tracking-wide flex items-center gap-1 animate-pulse">
                      <Sparkles className="w-3 h-3" /> Simulated
                    </span>
                  )}
                </div>

                {/* Score Number Display */}
                <div className="flex items-baseline gap-2 mt-3">
                  <span className="text-6xl font-black tracking-tight">{Math.round(currentScore)}</span>
                  <span className="text-2xl text-slate-400 font-bold">/ 100</span>

                  {isSimulated && simulatedStats && simulatedStats.scoreDelta !== 0 && (
                    <span
                      className={`ml-2 text-sm font-black px-2.5 py-1 rounded-lg flex items-center gap-1 ${
                        simulatedStats.scoreDelta > 0
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                          : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                      }`}
                    >
                      <TrendingUp className="w-3.5 h-3.5" />
                      {simulatedStats.scoreDelta > 0 ? `+${simulatedStats.scoreDelta}` : simulatedStats.scoreDelta} pts
                    </span>
                  )}
                </div>

                {/* Readiness Status Badge */}
                <div className="mt-4 flex flex-wrap items-center gap-2">
                  <div
                    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${
                      currentLabel === 'Ready'
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        : currentLabel === 'Almost there'
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    }`}
                  >
                    {currentLabel === 'Ready' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                    {currentLabel === 'Almost there' && <AlertCircle className="w-3.5 h-3.5 text-amber-400" />}
                    {currentLabel === 'Not yet' && <Zap className="w-3.5 h-3.5 text-rose-400" />}
                    Status: {currentLabel}
                  </div>

                  {isSimulated && simulatedStats && simulatedStats.label !== result.label && (
                    <span className="text-[11px] text-cyan-300 font-semibold">
                      (boosted from {result.label}!)
                    </span>
                  )}
                </div>
              </div>

              {/* Prep Timeline & Metric Details */}
              <div className="mt-6 pt-5 border-t border-slate-700/80 space-y-3 text-xs">
                <div>
                  <span className="text-slate-400 font-medium">Estimated Time to Placement:</span>
                  <p className="text-base font-black text-white mt-0.5">
                    {currentWeeks === 0 || currentLabel === 'Ready' ? (
                      <span className="text-emerald-400">0 weeks — Placement Ready! 🎉</span>
                    ) : currentWeeks !== null ? (
                      <span>
                        {currentWeeks} weeks intensive preparation
                        {isSimulated && result.weeks_to_ready_estimate !== null && (
                          <span className="text-slate-400 text-xs block font-normal">
                            (reduced by {Math.max(0, (result.weeks_to_ready_estimate || 0) - currentWeeks)} weeks from baseline)
                          </span>
                        )}
                      </span>
                    ) : (
                      'Estimate calculating...'
                    )}
                  </p>
                </div>

                <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700/60 space-y-1.5 text-[11px]">
                  <div className="flex justify-between text-slate-300">
                    <span>Hiring Company:</span>
                    <span className="font-bold text-white text-right truncate max-w-[160px]">{company}</span>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span>Categories Met:</span>
                    <span className="font-bold text-emerald-400">
                      {simulatedStats ? simulatedStats.gaps.filter((g) => g.bar_met).length : 0} / 12 Met
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span>Gaps Remaining:</span>
                    <span className="font-bold text-amber-400">
                      {simulatedStats ? simulatedStats.gaps.filter((g) => !g.bar_met).length : 0} to close
                    </span>
                  </div>
                </div>

                {isSimulated && (
                  <button
                    onClick={handleResetSimulation}
                    className="w-full mt-2 py-2 text-xs font-bold rounded-xl bg-slate-700 hover:bg-slate-600 text-slate-200 transition-colors flex items-center justify-center gap-1.5"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    Reset All Sliders to Baseline
                  </button>
                )}
              </div>
            </div>

            {/* Quick Action Simulator Helpers */}
            <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Sliders className="w-4 h-4 text-brand-600 dark:text-brand-400" />
                Simulator Quick Actions
              </h4>
              <p className="text-xs text-slate-500">
                Instantly simulate what candidate readiness would look like if all company hiring bars were met:
              </p>
              <div className="flex flex-col gap-2 pt-1">
                <button
                  onClick={handleMeetAllGaps}
                  className="w-full py-2 px-3 text-xs font-bold rounded-xl bg-brand-50 dark:bg-brand-950/60 text-brand-700 dark:text-brand-300 border border-brand-200 dark:border-brand-800 hover:bg-brand-100 dark:hover:bg-brand-900 transition-all flex items-center justify-center gap-1.5"
                >
                  <Sparkles className="w-3.5 h-3.5 text-brand-500" />
                  Simulate Closing All 12 Gaps (100% Score)
                </button>
                {isSimulated && (
                  <button
                    onClick={handleResetSimulation}
                    className="w-full py-2 px-3 text-xs font-bold rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all flex items-center justify-center gap-1.5"
                  >
                    <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
                    Reset Sliders to Original Candidate Levels
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Right Column: 12 Skillset Category Breakdown & Interactive Sliders */}
          <div className="lg:col-span-8 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-4">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Target className="w-4 h-4 text-brand-600 dark:text-brand-400" />
                  12 Skillset Breakdown vs {company} Hiring Bar
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  Drag the sliders (0–10) below to simulate level changes and observe live readiness impact.
                </p>
              </div>

              {simulatedStats && simulatedStats.modifiedCount > 0 && (
                <span className="text-xs font-bold text-cyan-600 dark:text-cyan-400 bg-cyan-50 dark:bg-cyan-950/60 px-3 py-1 rounded-full border border-cyan-200 dark:border-cyan-800 self-start sm:self-auto">
                  {simulatedStats.modifiedCount} Category Sliders Simulated
                </span>
              )}
            </div>

            {/* List of 12 Categories */}
            <div className="space-y-4">
              {simulatedStats?.gaps.map((gap) => {
                const code = gap.category_code;
                const categoryName = CATEGORY_NAMES[code] || (gap as any).category_name || code;
                const simLevel = gap.simulated_level;
                const baseLevel = baselineLevels[code] !== undefined ? baselineLevels[code] : gap.candidate_level;
                const reqLevel = gap.required_level;
                const isModified = gap.is_modified;
                const barMet = gap.bar_met;

                // Points gained if gap is closed
                const gapPoints =
                  reqLevel > baseLevel && result
                    ? Math.round((100 * (reqLevel - baseLevel)) / Math.max(1, result.skillset_gap.reduce((acc, g) => acc + g.required_level, 0)) * 10) / 10
                    : 0;

                return (
                  <div
                    key={code}
                    className={`p-4 rounded-xl border transition-all ${
                      isModified
                        ? 'bg-cyan-50/40 dark:bg-cyan-950/20 border-cyan-300 dark:border-cyan-800'
                        : 'bg-slate-50/60 dark:bg-slate-800/40 border-slate-200 dark:border-slate-800'
                    }`}
                  >
                    {/* Category Title Row */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-extrabold px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200">
                          {code}
                        </span>
                        <span className="text-xs font-bold text-slate-900 dark:text-white">
                          {categoryName}
                        </span>
                      </div>

                      <div className="flex items-center gap-2 text-xs">
                        {isModified && (
                          <span className="text-[11px] font-black text-cyan-600 dark:text-cyan-400 bg-cyan-100 dark:bg-cyan-950 px-2 py-0.5 rounded-full border border-cyan-300 dark:border-cyan-800">
                            Simulated: {simLevel}/10 ({gap.delta_level > 0 ? `+${gap.delta_level}` : gap.delta_level})
                          </span>
                        )}

                        <span
                          className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                            barMet
                              ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                              : 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                          }`}
                        >
                          {barMet ? '✓ Bar Met' : `Gap: -${reqLevel - simLevel}`}
                        </span>

                        <span className="text-[11px] text-slate-500 font-medium">
                          Contrib: {gap.contribution ? gap.contribution.toFixed(1) : '0.0'}%
                        </span>
                      </div>
                    </div>

                    {/* Dual Visual Bar Chart */}
                    <div className="space-y-1 mb-2.5">
                      <div className="h-2.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden flex relative">
                        {/* Candidate Baseline Bar */}
                        <div
                          className={`h-full transition-all ${barMet && !isModified ? 'bg-emerald-500' : 'bg-brand-600'}`}
                          style={{ width: `${(Math.min(baseLevel, simLevel) / 10) * 100}%` }}
                        />

                        {/* What-If Boost Bar */}
                        {isModified && simLevel > baseLevel && (
                          <div
                            className="h-full bg-gradient-to-r from-cyan-400 to-cyan-500 transition-all animate-pulse"
                            style={{ width: `${((simLevel - baseLevel) / 10) * 100}%` }}
                          />
                        )}

                        {/* Company Requirement Target Line */}
                        <div
                          className="absolute top-0 bottom-0 w-1 bg-rose-500 z-10 shadow-sm"
                          style={{ left: `${(reqLevel / 10) * 100}%` }}
                          title={`Company Required: ${reqLevel}/10`}
                        />
                      </div>

                      <div className="flex justify-between text-[11px] text-slate-500">
                        <span>
                          Candidate Baseline: <strong className="text-slate-800 dark:text-slate-200">{baseLevel}/10</strong>
                        </span>
                        <span className="text-rose-600 dark:text-rose-400 font-bold">
                          Required Bar: {reqLevel}/10
                        </span>
                      </div>
                    </div>

                    {/* Interactive What-If Slider Controls */}
                    <div className="flex items-center gap-3 pt-1 border-t border-slate-200/60 dark:border-slate-700/60">
                      <span className="text-[11px] font-bold text-slate-500 min-w-[70px]">
                        What-If Slider:
                      </span>
                      <input
                        type="range"
                        min="0"
                        max="10"
                        step="1"
                        value={simLevel}
                        onChange={(e) => handleSliderChange(code, Number(e.target.value))}
                        className="flex-1 accent-cyan-500 cursor-pointer h-2 bg-slate-200 dark:bg-slate-700 rounded-lg"
                      />
                      <span className="font-mono text-xs font-black text-slate-900 dark:text-white min-w-[36px] text-right">
                        {simLevel} / 10
                      </span>

                      {/* Quick Meet Bar button */}
                      {simLevel < reqLevel && (
                        <button
                          onClick={() => handleSliderChange(code, reqLevel)}
                          className="text-[10px] font-bold px-2 py-0.5 rounded bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300 hover:bg-brand-200 transition-colors"
                          title="Set slider to meet company requirement"
                        >
                          Meet Bar ({reqLevel})
                        </button>
                      )}

                      {/* Reset Single Slider */}
                      {isModified && (
                        <button
                          onClick={() => handleSliderChange(code, baseLevel)}
                          className="text-[10px] font-semibold text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                          title="Reset category to baseline"
                        >
                          <RotateCcw className="w-3 h-3" />
                        </button>
                      )}
                    </div>

                    {/* Aditya's Plain-English Insight Sentence (Section 14) */}
                    <div className="mt-2 text-[11px] text-slate-600 dark:text-slate-400 italic">
                      {isModified ? (
                        <span className="text-cyan-700 dark:text-cyan-300 font-semibold not-italic">
                          ✨ {categoryName}: changed from level {baseLevel} to {simLevel}.{' '}
                          {simLevel >= reqLevel ? 'Company hiring bar satisfied!' : `Remaining gap is ${reqLevel - simLevel} points.`}
                        </span>
                      ) : baseLevel < reqLevel ? (
                        <span>
                          💡 <strong>{categoryName}</strong>: you have level {baseLevel}, {company} requires {reqLevel}. Closing this gap adds{' '}
                          <strong className="text-emerald-600 dark:text-emerald-400">+{gapPoints} points</strong> to your readiness score.
                        </span>
                      ) : (
                        <span className="text-emerald-600 dark:text-emerald-400 font-medium not-italic">
                          ✓ Hiring bar met! Contributing full {gap.contribution ? gap.contribution.toFixed(1) : 0}% towards candidate readiness.
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Bottom Summary Callout of Active What-If Changes */}
            {isSimulated && simulatedStats && (
              <div className="p-4 rounded-xl bg-gradient-to-r from-cyan-900/20 via-brand-900/20 to-indigo-900/20 border border-cyan-500/30 text-xs space-y-2">
                <div className="flex items-center gap-2 font-bold text-cyan-600 dark:text-cyan-300">
                  <Sparkles className="w-4 h-4" />
                  What-If Simulation Active Summary:
                </div>
                <p className="text-slate-700 dark:text-slate-300">
                  Simulating level improvements across <strong>{simulatedStats.modifiedCount} categories</strong> raises readiness from{' '}
                  <strong className="text-slate-900 dark:text-white">{Math.round(simulatedStats.baseScore)}/100</strong> to{' '}
                  <strong className="text-emerald-600 dark:text-emerald-400 text-sm">
                    {Math.round(simulatedStats.score)}/100 (+{simulatedStats.scoreDelta} pts)
                  </strong>{' '}
                  and cuts estimated preparation time down from{' '}
                  <strong>{result.weeks_to_ready_estimate || 0} weeks</strong> to{' '}
                  <strong className="text-emerald-500">{simulatedStats.weeksEstimate} weeks</strong>!
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Stepper Navigation */}
      <div className="flex justify-between items-center pt-6 border-t border-slate-200 dark:border-slate-800">
        <button
          onClick={() => setCurrentStep(3)}
          className="flex items-center gap-2 text-sm font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Step 3: Profile Form
        </button>

        <button
          onClick={() => setCurrentStep(5)}
          className="flex items-center gap-2 px-6 py-2.5 text-sm font-bold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 transition-all shadow-md cursor-pointer"
        >
          Proceed to Step 5: Skill Matching
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
