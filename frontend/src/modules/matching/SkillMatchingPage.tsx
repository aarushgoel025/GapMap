import React, { useEffect, useState } from 'react';
import { useApp } from '../../context/AppContext';
import { fetchSamples, matchCandidateWithJD, matchSkills } from '../../api';
import type { MatchResult, Profile } from '../../types';
import { ScoreRing } from './ScoreRing';
import { MatchedSkillsTable } from './MatchedSkillsTable';
import { MissingSkillsList } from './MissingSkillsList';

interface SkillMatchingPageProps {
  initialCandidateId?: string;
  initialJdId?: string;
  onOpenHeatmap: () => void;
}

export const SkillMatchingPage: React.FC<SkillMatchingPageProps> = ({
  initialCandidateId,
  initialJdId,
  onOpenHeatmap,
}) => {
  const { currentProfile, parsedResume, selectedJd: globalSelectedJd, company } = useApp();
  const [candidates, setCandidates] = useState<{ id: string; name: string }[]>([]);
  const [jds, setJds] = useState<{ id: string; company: string; role: string; source_file: string }[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<string>(
    initialCandidateId || 'candidate_1_all_rounder'
  );
  const [selectedJd, setSelectedJd] = useState<string>(
    initialJdId || 'google_software_engineer'
  );

  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load samples list and synchronize with active AppContext
  useEffect(() => {
    fetchSamples().then((data) => {
      const candidateList = [...data.profiles];
      const hasActiveProfile = Boolean(currentProfile?.skills?.length || parsedResume?.skills?.length);

      if (hasActiveProfile) {
        const customName =
          currentProfile?.name ||
          (parsedResume?.extras as any)?.candidate_name ||
          (parsedResume?.extras as any)?.name ||
          'Uploaded Resume';
        candidateList.unshift({
          id: 'active_candidate',
          name: 'Active: ' + customName,
        });
      }
      setCandidates(candidateList);

      const jdList = [...data.jds];
      if (globalSelectedJd) {
        const jdSource =
          'source_file' in globalSelectedJd
            ? globalSelectedJd.source_file
            : (globalSelectedJd as any).filename;
        const jdRole =
          'role' in globalSelectedJd
            ? globalSelectedJd.role
            : ('title' in globalSelectedJd ? (globalSelectedJd as any).title : 'Role');
        jdList.unshift({
          id: 'active_jd',
          company: globalSelectedJd.company || 'Active Target JD',
          role: jdRole || 'Target Role',
          source_file: jdSource || 'active_jd.pdf',
        });
      }
      setJds(jdList);

      // Intelligent Context Pre-Selection:
      if (!initialCandidateId) {
        if (hasActiveProfile) {
          setSelectedCandidate('active_candidate');
        } else if (candidateList.length > 0) {
          setSelectedCandidate(candidateList[0].id);
        }
      }

      if (!initialJdId) {
        if (globalSelectedJd) {
          setSelectedJd('active_jd');
        } else if (company) {
          const compLower = company.toLowerCase();
          const matchedJd = jdList.find(
            (j) =>
              j.company.toLowerCase().includes(compLower) ||
              compLower.includes(j.company.toLowerCase())
          );
          if (matchedJd) {
            setSelectedJd(matchedJd.id);
          } else if (jdList.length > 0) {
            setSelectedJd(jdList[0].id);
          }
        } else if (jdList.length > 0) {
          setSelectedJd(jdList[0].id);
        }
      }
    });
  }, [currentProfile, parsedResume, globalSelectedJd, company, initialCandidateId, initialJdId]);

  // Update selection if props change (e.g. from heatmap click)
  useEffect(() => {
    if (initialCandidateId) setSelectedCandidate(initialCandidateId);
    if (initialJdId) setSelectedJd(initialJdId);
  }, [initialCandidateId, initialJdId]);

  // Run match when selections change
  useEffect(() => {
    if (!selectedCandidate || !selectedJd) return;

    setLoading(true);
    setError(null);

    const isCustomCandidate = selectedCandidate === 'active_candidate';
    const isCustomJd = selectedJd === 'active_jd';

    if (isCustomCandidate || isCustomJd) {
      const extraObj = (parsedResume?.extras || {}) as Record<string, any>;
      const activeProf: Profile = currentProfile || {
        name: extraObj.candidate_name || extraObj.name || 'Active Candidate',
        email: extraObj.email || '',
        skills: parsedResume?.skills || [],
        hackathons: [],
        internships: [],
        certifications: [],
        preferred_roles: [],
      };

      matchSkills({
        profile: isCustomCandidate ? activeProf : undefined,
        profile_id: !isCustomCandidate ? selectedCandidate : undefined,
        jd_id: !isCustomJd ? selectedJd : undefined,
        jd_skills:
          isCustomJd && globalSelectedJd && 'skills' in globalSelectedJd
            ? globalSelectedJd.skills
            : undefined,
        jd_source_file:
          isCustomJd && globalSelectedJd
            ? 'source_file' in globalSelectedJd
              ? globalSelectedJd.source_file
              : (globalSelectedJd as any).filename
            : undefined,
      })
        .then((res) => {
          setMatchResult(res);
          setLoading(false);
        })
        .catch((err) => {
          setError(err.message || 'Error executing skill match');
          setLoading(false);
        });
    } else {
      matchCandidateWithJD(selectedCandidate, selectedJd)
        .then((res) => {
          setMatchResult(res);
          setLoading(false);
        })
        .catch((err) => {
          setError(err.message || 'Error executing skill match');
          setLoading(false);
        });
    }
  }, [selectedCandidate, selectedJd, currentProfile, parsedResume, globalSelectedJd]);

  const activeJd = jds.find((j) => j.id === selectedJd);
  const activeCand = candidates.find((c) => c.id === selectedCandidate);

  return (
    <div className="space-y-6">
      {/* Header & Controls bar */}
      <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 uppercase tracking-wide">
                Pillar 3: 3-Layer Matching
              </span>
              <span className="text-xs text-slate-400">|</span>
              <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">Explainable Skill Gaps & Dependencies</span>
            </div>
            <h1 className="text-2xl font-black text-slate-900 dark:text-slate-100 mt-1 tracking-tight">
              Skill Matching & Gap Analysis
            </h1>
          </div>

          <button
            onClick={onOpenHeatmap}
            className="self-start md:self-auto px-4 py-2.5 text-xs font-bold rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 transition-colors shadow-sm flex items-center gap-2 cursor-pointer"
          >
            <span>📊 View 4×6 Matrix Heatmap</span>
          </button>
        </div>

        {/* Context Sync Banner */}
        <div className="flex flex-wrap items-center justify-between gap-2 px-3.5 py-2.5 rounded-xl bg-blue-50/80 dark:bg-blue-950/40 border border-blue-200/80 dark:border-blue-900/60 text-xs text-blue-800 dark:text-blue-300 font-medium">
          <div className="flex items-center gap-2">
            <span className="text-base">🎯</span>
            <span>
              <strong>Synced with Pipeline:</strong> Evaluating{' '}
              <span className="font-bold underline decoration-blue-400 underline-offset-2">
                {activeCand?.name || 'Selected Candidate'}
              </span>{' '}
              against{' '}
              <span className="font-bold underline decoration-blue-400 underline-offset-2">
                {activeJd ? `${activeJd.company} — ${activeJd.role}` : 'Selected JD'}
              </span>
            </span>
          </div>
          {company && (
            <span className="text-[11px] px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900/60 text-blue-800 dark:text-blue-200 font-semibold">
              Target Company: {company}
            </span>
          )}
        </div>

        {/* Candidate & JD Selectors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-slate-100 dark:border-slate-800">
          {/* Candidate Switcher */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5">
              Select Candidate Profile
            </label>
            <div className="flex flex-col gap-1.5">
              <select
                value={selectedCandidate}
                onChange={(e) => setSelectedCandidate(e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {candidates.map((c) => (
                  <option key={c.id} value={c.id} className="dark:bg-slate-800 dark:text-slate-100">
                    {c.name}
                  </option>
                ))}
              </select>

              {/* Quick switch pills */}
              <div className="flex flex-wrap gap-1.5 mt-1">
                {candidates.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => setSelectedCandidate(c.id)}
                    className={`text-[11px] px-2.5 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                      selectedCandidate === c.id
                        ? 'bg-slate-900 dark:bg-brand-600 text-white shadow-xs'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                    }`}
                  >
                    {c.name.split(' ')[0]} ({c.name.match(/\((.*?)\)/)?.[1] || 'Profile'})
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* JD Dropdown */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5">
              Select Job Description (Target Role)
            </label>
            <select
              value={selectedJd}
              onChange={(e) => setSelectedJd(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {jds.map((j) => (
                <option key={j.id} value={j.id} className="dark:bg-slate-800 dark:text-slate-100">
                  {j.company} — {j.role}
                </option>
              ))}
            </select>
            {activeJd && (
              <p className="text-xs text-slate-400 dark:text-slate-400 mt-2 font-mono flex items-center gap-1">
                <span>📄 Source:</span>
                <span className="font-semibold text-slate-600 dark:text-slate-300">{activeJd.source_file}</span>
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div className="flex flex-col items-center justify-center p-16 bg-white/90 dark:bg-slate-900/90 rounded-2xl border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-3"></div>
          <p className="text-sm font-medium">Matching candidate skills against JD across 3 layers...</p>
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 rounded-2xl text-rose-800 dark:text-rose-300">
          <p className="font-bold text-sm">Failed to compute match</p>
          <p className="text-xs mt-1">{error}</p>
        </div>
      ) : matchResult ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Score Ring & Quick Summary */}
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-md p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-400 mb-4 text-center">
                Match Readiness Score
              </h3>
              <ScoreRing score={matchResult.match_score} />

              <div className="w-full grid grid-cols-2 gap-3 mt-6 pt-6 border-t border-slate-100 dark:border-slate-800">
                <div className="bg-emerald-50/60 dark:bg-emerald-950/40 border border-emerald-100 dark:border-emerald-800/60 p-3 rounded-xl text-center">
                  <div className="text-2xl font-black text-emerald-700 dark:text-emerald-400">
                    {matchResult.matched_skills.length}
                  </div>
                  <div className="text-[11px] font-semibold text-emerald-800 dark:text-emerald-300 uppercase mt-0.5">
                    Matched Skills
                  </div>
                </div>

                <div className="bg-amber-50/60 dark:bg-amber-950/40 border border-amber-100 dark:border-amber-800/60 p-3 rounded-xl text-center">
                  <div className="text-2xl font-black text-amber-700 dark:text-amber-400">
                    {matchResult.missing_skills.length}
                  </div>
                  <div className="text-[11px] font-semibold text-amber-800 dark:text-amber-300 uppercase mt-0.5">
                    Missing Gaps
                  </div>
                </div>
              </div>

              {/* Explanatory summary text */}
              <div className="mt-4 p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl text-xs text-slate-600 dark:text-slate-300 border border-slate-200/60 dark:border-slate-700/60 w-full space-y-1.5">
                <div className="font-bold text-slate-800 dark:text-slate-100 flex items-center gap-1.5">
                  <span>🧮</span>
                  <span>Deterministic Scoring Breakdown:</span>
                </div>
                <p className="text-[11px] leading-relaxed text-slate-500 dark:text-slate-400">
                  Calculated as weighted sum of credits (Must-Have = 2.0, Nice-to-Have = 1.0) divided by total JD requirement weight. Exact matches = 1.0, Aliases = 0.9, Semantic = 0.8 × Cosine. Gaps are ordered by prerequisite dependencies.
                </p>
              </div>
            </div>
          </div>

          {/* Right Column: Matched Skills and Ordered Missing Skills */}
          <div className="lg:col-span-8 space-y-6">
            {/* Matched Skills */}
            <MatchedSkillsTable skills={matchResult.matched_skills} />

            {/* Missing Skills with Learning Order */}
            <MissingSkillsList skills={matchResult.missing_skills} />
          </div>
        </div>
      ) : null}
    </div>
  );
};
