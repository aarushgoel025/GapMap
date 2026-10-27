import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { getCompanies, checkTalent, checkTalentWhatIf } from '../../api';
import type { TalentCheckResult, CompanyInfo } from '../../types';
import { Target, ArrowRight, ArrowLeft, Building, Zap } from 'lucide-react';

export const TalentPage: React.FC = () => {
  const { company, setCompany, currentProfile, setCurrentStep } = useApp();
  const [companies, setCompanies] = useState<CompanyInfo[]>([]);
  const [result, setResult] = useState<TalentCheckResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [simulatedSkill, setSimulatedSkill] = useState('');

  useEffect(() => {
    getCompanies().then(setCompanies);
  }, []);

  const runEvaluation = async (compName: string) => {
    setIsLoading(true);
    try {
      const data = await checkTalent({
        company: compName,
        profile: currentProfile || undefined,
      });
      setResult(data);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    runEvaluation(company || 'Stripe');
  }, [company]);

  const handleWhatIf = async () => {
    if (!simulatedSkill.trim() || !result) return;
    setIsLoading(true);
    try {
      const sim = await checkTalentWhatIf({
        company,
        profile: currentProfile || { name: 'Candidate', email: '', skills: [], hackathons: [], internships: [], certifications: [], preferred_roles: [] },
        additional_skills: [simulatedSkill.trim()],
      });
      setResult(sim);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300">
          Module 4: Talent Check (Aditya)
        </span>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">Company Talent Readiness Benchmark</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Evaluates candidate capability against company-specific hiring bars, estimating weeks-to-readiness.
        </p>
      </div>

      {/* Select Company */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-slate-500 mr-2 flex items-center gap-1">
          <Building className="w-3.5 h-3.5" /> Target Company:
        </span>
        {companies.map((c) => (
          <button
            key={c.id}
            onClick={() => {
              setCompany(c.name);
              runEvaluation(c.name);
            }}
            className={`px-3.5 py-1.5 text-xs font-semibold rounded-xl transition-all ${
              company === c.name
                ? 'bg-brand-600 text-white shadow-glow'
                : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-brand-400'
            }`}
          >
            {c.name}
          </button>
        ))}
      </div>

      {/* Main Readiness Card */}
      {result && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Score Card */}
          <div className="bg-gradient-to-br from-slate-900 to-slate-800 text-white p-6 rounded-2xl shadow-xl flex flex-col justify-between">
            <div>
              <span className="text-xs font-semibold text-brand-400 uppercase tracking-wider">Talent Readiness</span>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-5xl font-black">{Math.round(result.readiness_score)}</span>
                <span className="text-xl text-slate-400 font-semibold">/ 100</span>
              </div>
              <div className="mt-4 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-white/10 backdrop-blur-md">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                Status: {result.label || 'Evaluating'}
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-700/60 text-xs text-slate-300">
              <p>Estimated Time to Ready:</p>
              <p className="text-sm font-bold text-white mt-0.5">
                {result.weeks_to_ready_estimate !== null && result.weeks_to_ready_estimate !== undefined
                  ? `${result.weeks_to_ready_estimate} weeks intensive preparation`
                  : 'Ready for placement'}
              </p>
            </div>
          </div>

          {/* Skillset Gap Breakdown */}
          <div className="md:col-span-2 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Target className="w-4 h-4 text-brand-600" />
              Category Level Breakdown vs {result.company} Hiring Bar
            </h4>

            <div className="space-y-3">
              {result.skillset_gap.map((gap, i) => (
                <div key={i} className="text-xs space-y-1">
                  <div className="flex justify-between font-semibold">
                    <span className="text-slate-800 dark:text-slate-200">
                      {gap.category_code} ({gap.gap ? 'Needs Gap Closing' : 'Bar Met'})
                    </span>
                    <span className="text-slate-500">
                      Candidate: {gap.candidate_level}/10 | Required: {gap.required_level}/10
                    </span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden flex">
                    <div
                      className={`h-full rounded-full transition-all ${
                        gap.gap ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${(gap.candidate_level / 10) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* What-If Simulation Box */}
            <div className="mt-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700">
              <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 mb-2">
                Simulate "What-If" Skill Acquisition:
              </p>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={simulatedSkill}
                  onChange={(e) => setSimulatedSkill(e.target.value)}
                  placeholder="e.g. Distributed System Design / Go"
                  className="flex-1 px-3 py-1.5 text-xs rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900"
                />
                <button
                  onClick={handleWhatIf}
                  disabled={isLoading || !simulatedSkill.trim()}
                  className="px-4 py-1.5 text-xs font-semibold bg-brand-600 text-white rounded-xl hover:bg-brand-500 disabled:opacity-50"
                >
                  Simulate Score
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stepper Navigation */}
      <div className="flex justify-between items-center pt-4 border-t border-slate-200 dark:border-slate-800">
        <button
          onClick={() => setCurrentStep(3)}
          className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Profile
        </button>

        <button
          onClick={() => setCurrentStep(5)}
          className="flex items-center gap-2 px-6 py-2.5 text-sm font-semibold text-white bg-slate-900 dark:bg-white dark:text-slate-900 rounded-xl hover:opacity-90 transition-all shadow-md"
        >
          Proceed to Step 5: Skill Matching
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
