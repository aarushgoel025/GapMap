import React from 'react';

interface ScoreRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
}

export const ScoreRing: React.FC<ScoreRingProps> = ({
  score,
  size = 180,
  strokeWidth = 14,
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const normalizedScore = Math.max(0, Math.min(100, score));
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  let colorClass = 'text-rose-500';
  let badgeText = 'High Gap';
  let badgeBg = 'bg-rose-50 text-rose-700 border-rose-200';

  if (normalizedScore >= 80) {
    colorClass = 'text-emerald-500';
    badgeText = 'Strong Match';
    badgeBg = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  } else if (normalizedScore >= 60) {
    colorClass = 'text-amber-500';
    badgeText = 'Moderate Match';
    badgeBg = 'bg-amber-50 text-amber-700 border-amber-200';
  }

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-slate-100"
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={`${colorClass} transition-all duration-700 ease-out`}
            fill="transparent"
          />
        </svg>

        {/* Center label */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-4xl font-extrabold text-slate-800 tracking-tight">
            {score.toFixed(1)}
          </span>
          <span className="text-xs uppercase font-semibold text-slate-400 mt-0.5">
            Match Score
          </span>
        </div>
      </div>

      <div className={`mt-3 px-3 py-1 rounded-full text-xs font-semibold border ${badgeBg}`}>
        {badgeText}
      </div>
    </div>
  );
};

