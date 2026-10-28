import React from 'react';
import type { MatchedSkill } from '../../types';

interface MatchedSkillsTableProps {
  skills: MatchedSkill[];
}

export const MatchedSkillsTable: React.FC<MatchedSkillsTableProps> = ({ skills }) => {
  if (!skills || skills.length === 0) {
    return (
      <div className="p-8 text-center bg-white/90 dark:bg-slate-900/90 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400">
          🔍
        </div>
        <p className="text-sm font-medium text-slate-600 dark:text-slate-300">No skills matched yet</p>
        <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Check missing skills or select a different profile</p>
      </div>
    );
  }

  const renderBadge = (type: MatchedSkill['match_type']) => {
    switch (type) {
      case 'exact':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800/60">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5"></span>
            Exact (1.0)
          </span>
        );
      case 'alias':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200 dark:bg-blue-950/60 dark:text-blue-300 dark:border-blue-800/60">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mr-1.5"></span>
            Alias (0.9)
          </span>
        );
      case 'semantic':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 border border-purple-200 dark:bg-purple-950/60 dark:text-purple-300 dark:border-purple-800/60">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-500 mr-1.5"></span>
            Semantic
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="overflow-hidden bg-white/90 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm">
      <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-800/40 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">Matched Skills ({skills.length})</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Skills verified across Exact, Alias, and Semantic layers</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-100 dark:divide-slate-800 text-left text-sm">
          <thead className="bg-slate-50/80 dark:bg-slate-800/60 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            <tr>
              <th className="px-5 py-3">Required JD Skill</th>
              <th className="px-5 py-3">Candidate Skill</th>
              <th className="px-5 py-3">Match Layer</th>
              <th className="px-5 py-3 text-right">Similarity</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {skills.map((item, idx) => (
              <tr key={idx} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition-colors">
                <td className="px-5 py-3 font-semibold text-slate-900 dark:text-slate-100">
                  {item.jd_skill}
                </td>
                <td className="px-5 py-3 text-slate-600 dark:text-slate-300 flex items-center gap-1.5">
                  <span className="text-slate-400 dark:text-slate-500 text-xs">↳</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">{item.profile_skill}</span>
                </td>
                <td className="px-5 py-3">
                  {renderBadge(item.match_type)}
                </td>
                <td className="px-5 py-3 text-right font-mono text-xs font-semibold text-slate-600 dark:text-slate-400">
                  {((item.similarity ?? 1.0) * 100).toFixed(0)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
