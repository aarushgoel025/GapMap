import React, { useEffect, useState } from 'react';
import { fetchMatchMatrix } from '../../api';
import type { MatrixResponse } from '../../types';

interface HeatmapPageProps {
  onSelectCandidateAndJD: (candidateId: string, jdId: string) => void;
  onBackToMatching: () => void;
}

export const HeatmapPage: React.FC<HeatmapPageProps> = ({
  onSelectCandidateAndJD,
  onBackToMatching,
}) => {
  const [data, setData] = useState<MatrixResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMatchMatrix()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to fetch matrix');
        setLoading(false);
      });
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'bg-emerald-500 text-white font-bold hover:bg-emerald-600';
    if (score >= 60) return 'bg-amber-400 text-slate-900 font-semibold hover:bg-amber-500';
    if (score >= 35) return 'bg-amber-200 text-slate-900 hover:bg-amber-300';
    if (score > 0) return 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300 hover:bg-rose-200 dark:hover:bg-rose-900/60';
    return 'bg-slate-100 text-slate-400 dark:bg-slate-800 dark:text-slate-500 hover:bg-slate-200 dark:hover:bg-slate-700';
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-slate-500 dark:text-slate-400">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-3"></div>
        <p className="text-sm font-medium">Calculating 4x6 Skill Match Matrix...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 rounded-xl text-rose-800 dark:text-rose-300 text-center max-w-lg mx-auto mt-8">
        <p className="font-bold text-sm">Failed to load Heatmap Matrix</p>
        <p className="text-xs mt-1 text-rose-600 dark:text-rose-400">{error}</p>
        <button
          onClick={onBackToMatching}
          className="mt-4 px-4 py-2 bg-rose-600 text-white rounded-lg text-xs font-semibold hover:bg-rose-700 cursor-pointer"
        >
          Return to Matching
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 uppercase tracking-wide">
              Pillar 3 & System 03
            </span>
            <span className="text-xs font-medium text-slate-400">|</span>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">4 Candidates × 6 Job Descriptions</span>
          </div>
          <h2 className="text-2xl font-black text-slate-900 dark:text-slate-100 mt-1 tracking-tight">
            Skill Match Matrix Heatmap
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-2xl">
            Proves candidate differentiation across job specifications. Click any cell to inspect the deep-dive match breakdown.
          </p>
        </div>

        <button
          onClick={onBackToMatching}
          className="self-start md:self-auto px-4 py-2.5 text-xs font-bold rounded-xl bg-slate-900 dark:bg-brand-600 text-white hover:bg-slate-800 dark:hover:bg-brand-700 transition-colors shadow-sm flex items-center gap-2 cursor-pointer"
        >
          <span>← Back to Single Match View</span>
        </button>
      </div>

      {/* Heatmap Matrix Card */}
      <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-md rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse">
            <thead>
              <tr>
                <th className="p-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider min-w-[200px] border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40">
                  Candidate Profile
                </th>
                {data.jds.map((jd) => (
                  <th
                    key={jd.id}
                    className="p-3 text-center text-xs font-bold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-800 min-w-[130px] max-w-[160px] bg-slate-50/50 dark:bg-slate-800/40"
                  >
                    <div className="text-[10px] font-extrabold uppercase text-indigo-600 dark:text-indigo-400 tracking-wider">
                      {jd.company}
                    </div>
                    <div className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate" title={jd.role}>
                      {jd.role}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {data.resumes.map((cand, rIdx) => (
                <tr key={cand.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
                  <td className="p-3.5 border-r border-slate-100 dark:border-slate-800 font-semibold text-slate-900 dark:text-slate-100 text-sm">
                    <div>{cand.name}</div>
                    <div className="text-xs text-slate-400 font-normal font-mono">{cand.id}</div>
                  </td>

                  {data.jds.map((jd, jIdx) => {
                    const score = data.matrix[rIdx][jIdx];
                    return (
                      <td key={jd.id} className="p-2 text-center">
                        <button
                          onClick={() => onSelectCandidateAndJD(cand.id, jd.id)}
                          className={`w-full py-2.5 px-2 rounded-xl transition-all duration-150 transform hover:scale-105 shadow-xs cursor-pointer ${getScoreColor(
                            score
                          )}`}
                          title={`Click to analyze ${cand.name} for ${jd.role}`}
                        >
                          <span className="text-sm font-extrabold">{score.toFixed(1)}%</span>
                        </button>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Legend */}
        <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-500 dark:text-slate-400">Score Range:</span>
            <div className="flex items-center gap-1.5">
              <span className="w-4 h-4 rounded bg-emerald-500 inline-block"></span>
              <span className="text-slate-600 dark:text-slate-300 font-medium">≥80% Strong</span>
            </div>
            <div className="flex items-center gap-1.5 ml-2">
              <span className="w-4 h-4 rounded bg-amber-400 inline-block"></span>
              <span className="text-slate-600 dark:text-slate-300 font-medium">60-79% Moderate</span>
            </div>
            <div className="flex items-center gap-1.5 ml-2">
              <span className="w-4 h-4 rounded bg-amber-200 inline-block"></span>
              <span className="text-slate-600 dark:text-slate-300 font-medium">35-59% Fair</span>
            </div>
            <div className="flex items-center gap-1.5 ml-2">
              <span className="w-4 h-4 rounded bg-rose-100 dark:bg-rose-950/60 inline-block"></span>
              <span className="text-slate-600 dark:text-slate-300 font-medium">&lt;35% Gap</span>
            </div>
          </div>

          <div className="text-slate-400 italic">
            * Brief requirements verified: all-rounder versatile, data-analyst leads data roles, support leads Oracle.
          </div>
        </div>
      </div>
    </div>
  );
};
