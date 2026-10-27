import React from 'react';
import { useApp } from '../context/AppContext';
import { Check, FileText, UserCheck, ShieldAlert, Cpu, Sparkles } from 'lucide-react';

const STEPS = [
  { id: 1, label: 'JD', fullLabel: 'Job Description', icon: FileText, owner: 'Samiksha' },
  { id: 2, label: 'Resume', fullLabel: 'Resume Parsing', icon: UserCheck, owner: 'Arushi' },
  { id: 3, label: 'Profile', fullLabel: 'Candidate Profile', icon: Sparkles, owner: 'Aarush (You)' },
  { id: 4, label: 'Talent Check', fullLabel: 'Talent Readiness', icon: ShieldAlert, owner: 'Aditya' },
  { id: 5, label: 'Skill Matching', fullLabel: 'Skill Matching', icon: Cpu, owner: 'Anjali' },
];

export const Stepper: React.FC = () => {
  const { currentStep, setCurrentStep } = useApp();

  return (
    <div className="w-full bg-white/90 dark:bg-slate-900/90 backdrop-blur-md rounded-2xl border border-slate-200/80 dark:border-slate-800 p-4 shadow-sm">
      <div className="flex items-center justify-between max-w-4xl mx-auto">
        {STEPS.map((step, idx) => {
          const isCompleted = currentStep > step.id;
          const isCurrent = currentStep === step.id;
          const Icon = step.icon;

          return (
            <React.Fragment key={step.id}>
              {/* Step Item */}
              <button
                onClick={() => setCurrentStep(step.id)}
                className="group flex flex-col items-center text-center cursor-pointer focus:outline-none transition-all"
              >
                <div
                  className={`w-11 h-11 rounded-2xl flex items-center justify-center font-bold text-sm transition-all duration-300 ${
                    isCurrent
                      ? 'bg-gradient-to-tr from-brand-600 to-brand-400 text-white shadow-glow scale-105 ring-4 ring-brand-100 dark:ring-brand-950'
                      : isCompleted
                      ? 'bg-emerald-500 text-white shadow-sm'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 group-hover:bg-slate-200 dark:group-hover:bg-slate-700'
                  }`}
                >
                  {isCompleted ? <Check className="w-5 h-5 stroke-[2.5]" /> : <Icon className="w-5 h-5" />}
                </div>

                <div className="mt-2">
                  <span
                    className={`block text-xs font-bold transition-colors ${
                      isCurrent
                        ? 'text-brand-600 dark:text-brand-400'
                        : isCompleted
                        ? 'text-slate-800 dark:text-slate-200'
                        : 'text-slate-400 dark:text-slate-500'
                    }`}
                  >
                    {step.id}. {step.label}
                  </span>
                  <span className="hidden sm:block text-[10px] text-slate-400 dark:text-slate-500">
                    {step.owner}
                  </span>
                </div>
              </button>

              {/* Connecting Line */}
              {idx < STEPS.length - 1 && (
                <div className="flex-1 h-0.5 mx-2 -mt-5 bg-slate-200 dark:bg-slate-800">
                  <div
                    className={`h-full transition-all duration-500 ${
                      currentStep > idx + 1 ? 'bg-emerald-500 w-full' : 'bg-transparent w-0'
                    }`}
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
