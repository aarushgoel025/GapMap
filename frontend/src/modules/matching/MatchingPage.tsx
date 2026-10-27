import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { matchSkills, getMatchMatrix } from '../../api';
import type { MatchResult, MatchMatrix } from '../../types';
import { CheckCircle2, AlertOctagon, Grid, ArrowLeft, RefreshCw } from 'lucide-react';

export const MatchingPage: React.FC = () => {
  const { currentProfile, setCurrentStep } = useApp();
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);
  const [matrix, setMatrix] = useState<MatchMatrix | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    Promise.all([
      matchSkills({ profile: currentProfile || undefined }),
      getMatchMatrix(),
    ])
      .then(([res, mat]) => {
        setMatchResult(res);
        setMatrix(mat);
      })
      .finally(() => setIsLoading(false));
  }, [currentProfile]);

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300">
          Module 5: Skill Matching (Anjali)
        </span>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">Skill Matching & Fit Matrix</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Evaluates direct, semantic, and alias skill matches, pinpointing gaps with score impact and learn priority.
        </p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-16">
          <RefreshCw className="w-8 h-8 animate-spin text-brand-600" />
        </div>
      ) : (
        <>
          {/* Top Score Banner */}
          {matchResult && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-6 bg-gradient-to-br from-brand-600 to-indigo-700 text-white rounded-2xl shadow-glow flex flex-col justify-between">
                <div>
                  <span className="text-xs uppercase tracking-wider font-semibold text-brand-200">
                    JD Match Score
                  </span>
                  <div className="flex items-baseline gap-2 mt-2">
                    <span className="text-5xl font-black">{Math.round(matchResult.match_score)}</span>
                    <span className="text-2xl text-brand-200">%</span>
                  </div>
                </div>
                <p className="text-xs text-brand-100 mt-4">
                  Evaluated against target JD: {matchResult.jd_source_file}
                </p>
              </div>

              {/* Matched Skills List */}
              <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1.5 mb-3">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  Matched Skills ({matchResult.matched_skills.length})
                </h4>
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {matchResult.matched_skills.map((m, i) => (
                    <div
                      key={i}
                      className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 flex justify-between items-center text-xs"
                    >
                      <div>
                        <span className="font-semibold text-slate-900 dark:text-white">{m.jd_skill}</span>
                        <span className="text-slate-400 block text-[10px]">Candidate: {m.profile_skill}</span>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                        {m.match_type} ({Math.round((m.similarity || 1) * 100)}%)
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Missing Skills List */}
              <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1.5 mb-3">
                  <AlertOctagon className="w-4 h-4 text-amber-500" />
                  Missing Skills ({matchResult.missing_skills.length})
                </h4>
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {matchResult.missing_skills.map((miss, i) => (
                    <div
                      key={i}
                      className="p-2.5 rounded-xl bg-amber-50/40 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/50 flex justify-between items-center text-xs"
                    >
                      <div>
                        <span className="font-semibold text-slate-900 dark:text-white">{miss.skill_name}</span>
                        <span className="text-amber-700 dark:text-amber-400 block text-[10px]">
                          Order #{miss.learn_order} • Priority: {miss.importance}
                        </span>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-200 text-amber-900 dark:bg-amber-900 dark:text-amber-200">
                        +{miss.score_impact} pts
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 4 x 6 Score Grid Matrix */}
          {matrix && (
            <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Grid className="w-4 h-4 text-brand-600" />
                Cross-Company & Role Readiness Matrix (4 x 6 Grid)
              </h4>

              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 dark:border-slate-700">
                      <th className="py-2.5 px-3 font-bold text-slate-500 uppercase tracking-wider">Company</th>
                      {matrix.roles.map((r, i) => (
                        <th key={i} className="py-2.5 px-3 font-semibold text-slate-700 dark:text-slate-300">
                          {r}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {matrix.companies.map((comp, rowIdx) => (
                      <tr key={comp} className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                        <td className="py-3 px-3 font-bold text-slate-900 dark:text-white">{comp}</td>
                        {matrix.grid[rowIdx]?.map((val, colIdx) => (
                          <td key={colIdx} className="py-3 px-3">
                            <span
                              className={`px-2.5 py-1 rounded-lg font-bold text-[11px] inline-block ${
                                val >= 90
                                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                                  : val >= 80
                                  ? 'bg-brand-100 text-brand-800 dark:bg-brand-950 dark:text-brand-300'
                                  : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                              }`}
                            >
                              {val}%
                            </span>
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Stepper Navigation */}
      <div className="flex justify-between items-center pt-4 border-t border-slate-200 dark:border-slate-800">
        <button
          onClick={() => setCurrentStep(4)}
          className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Talent Check
        </button>

        <button
          onClick={() => setCurrentStep(1)}
          className="px-6 py-2.5 text-sm font-semibold text-white bg-slate-900 dark:bg-white dark:text-slate-900 rounded-xl hover:opacity-90 transition-all shadow-md"
        >
          Start New Analysis Cycle
        </button>
      </div>
    </div>
  );
};
