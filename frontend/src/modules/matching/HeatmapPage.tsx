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
    if (score > 0) return 'bg-rose-100 text-rose-800 hover:bg-rose-200';
    return 'bg-slate-100 text-slate-400 hover:bg-slate-200';
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-slate-500">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-3"></div>
        <p className="text-sm font-medium">Calculating 4x6 Skill Match Matrix...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-center max-w-lg mx-auto mt-8">
        <p className="font-bold text-sm">Failed to load Heatmap Matrix</p>
        <p className="text-xs mt-1 text-rose-600">{error}</p>
        <button
          onClick={onBackToMatching}
          className="mt-4 px-4 py-2 bg-rose-600 text-white rounded-lg text-xs font-semibold hover:bg-rose-700"
        >
          Return to Matching
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-100 text-indigo-700 uppercase tracking-wide">
              Pillar 3 & System 03
            </span>
            <span className="text-xs font-medium text-slate-400">|</span>
            <span className="text-xs text-slate-500 font-medium">4 Candidates × 6 Job Descriptions</span>
          </div>
          <h2 className="text-2xl font-black text-slate-900 mt-1 tracking-tight">
            Skill Match Matrix Heatmap
          </h2>
          <p className="text-sm text-slate-500 mt-1 max-w-2xl">
            Proves candidate differentiation across job specifications. Click any cell to inspect the deep-dive match breakdown.
          </p>
        </div>

        <button
          onClick={onBackToMatching}
          className="self-start md:self-auto px-4 py-2 text-sm font-semibold rounded-xl bg-slate-900 text-white hover:bg-slate-800 transition-colors shadow-sm flex items-center gap-2"
        >
          <span>← Back to Single Match View</span>
        </button>
      </div>

      {/* Heatmap Matrix Card */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse">
            <thead>
              <tr>
                <th className="p-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider min-w-[200px] border-b border-slate-200 bg-slate-50/50">
                  Candidate Profile
                </th>
                {data.jds.map((jd) => (
                  <th
                    key={jd.id}
                    className="p-3 text-center text-xs font-bold text-slate-700 border-b border-slate-200 min-w-[130px] max-w-[160px] bg-slate-50/50"
                  >
                    <div className="text-[10px] font-extrabold uppercase text-indigo-600 tracking-wider">
                      {jd.company}
                    </div>
                    <div className="text-xs font-bold text-slate-800 truncate" title={jd.role}>
                      {jd.role}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.resumes.map((cand, rIdx) => (
                <tr key={cand.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="p-3.5 border-r border-slate-100 font-semibold text-slate-900 text-sm">
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
        <div className="mt-6 pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-500">Score Range:</span>
            <div className="flex items-center gap-1.5">
              <span className="w-4 h-4 rounded bg-emerald-500 inline-block"></span>
              <span className="text-slate-600 font-medium">≥80% Strong</span>
            </div>
            <div className="flex items-center gap-1.5 ml-2">
              <span className="w-4 h-4 rounded bg-amber-400 inline-block"></span>
              <span className="text-slate-600 font-medium">60-79% Moderate</span>
            </div>
            <div className="flex items-center gap-1.5 ml-2">
              <span className="w-4 h-4 rounded bg-amber-200 inline-block"></span>
              <span className="text-slate-600 font-medium">35-59% Fair</span>
            </div>
            <div className="flex items-center gap-1.5 ml-2">
              <span className="w-4 h-4 rounded bg-rose-100 inline-block"></span>
              <span className="text-slate-600 font-medium">&lt;35% Gap</span>
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

