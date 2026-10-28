import React from 'react';
import type { MissingSkill } from '../../types';

interface MissingSkillsListProps {
  skills: MissingSkill[];
}

export const MissingSkillsList: React.FC<MissingSkillsListProps> = ({ skills }) => {
  if (!skills || skills.length === 0) {
    return (
      <div className="p-8 text-center bg-white/90 dark:bg-slate-900/90 rounded-2xl border border-emerald-200 dark:border-emerald-800/60 bg-emerald-50/20 dark:bg-emerald-950/20 shadow-sm">
        <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-emerald-100 dark:bg-emerald-900/40 flex items-center justify-center text-emerald-600 dark:text-emerald-400 font-bold text-lg">
          ✓
        </div>
        <p className="text-sm font-semibold text-emerald-800 dark:text-emerald-300">No Skill Gaps Identified!</p>
        <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-1">This candidate meets or exceeds all JD requirements.</p>
      </div>
    );
  }

  return (
    <div className="bg-white/90 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden">
      <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-800/40 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">Missing Skills & Learning Plan ({skills.length})</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Ranked by dependencies (prerequisites first) then score impact descending
          </p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800/60 rounded-lg">
          SkillBridge Priority
        </span>
      </div>

      <div className="divide-y divide-slate-100 dark:divide-slate-800">
        {skills.map((item) => (
          <div key={item.skill_name} className="p-4 hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors flex items-start gap-3.5">
            {/* Learn Order Step Pill */}
            <div className="flex-shrink-0 w-7 h-7 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800/60 text-indigo-700 dark:text-indigo-300 font-bold text-xs flex items-center justify-center shadow-xs">
              #{item.learn_order}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-2 mb-1.5">
                <span className="text-sm font-bold text-slate-900 dark:text-slate-100">{item.skill_name}</span>
                
                {/* Category Code Pill */}
                <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                  {item.category_code}
                </span>

                {/* Importance Badge */}
                {item.importance === 'must_have' ? (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800/60">
                    Must Have
                  </span>
                ) : (
                  <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
                    Nice to Have
                  </span>
                )}

                {/* Points Gained Chip */}
                <span className="ml-auto inline-flex items-center text-xs font-bold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-200 dark:border-emerald-800/60">
                  +{(item.score_impact ?? 0).toFixed(1)} pts
                </span>
              </div>

              {/* Prerequisites section */}
              {item.prerequisites && item.prerequisites.length > 0 ? (
                <div className="flex flex-wrap items-center gap-1.5 mt-2 text-xs">
                  <span className="text-slate-400 dark:text-slate-400 font-medium text-[11px]">Prerequisites:</span>
                  {item.prerequisites.map((p, i) => (
                    <span
                      key={i}
                      className="inline-flex items-center px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/50 text-amber-800 dark:text-amber-300 border border-amber-200/80 dark:border-amber-800/60 font-medium text-[11px]"
                    >
                      <span className="mr-1 text-amber-500">⚡</span>
                      {p}
                    </span>
                  ))}
                </div>
              ) : (
                <div className="text-[11px] text-slate-400 dark:text-slate-400 mt-1 flex items-center gap-1">
                  <span className="text-emerald-500">✓</span> No prerequisites required (ready to learn immediately)
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
