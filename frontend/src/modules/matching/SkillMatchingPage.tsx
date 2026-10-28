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
  const { currentProfile, parsedResume, selectedJd: globalSelectedJd } = useApp();
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

  // Load samples list
  useEffect(() => {
    fetchSamples().then((data) => {
      const candidateList = [...data.profiles];
      if (currentProfile?.skills?.length || parsedResume?.skills?.length) {
        const customName = currentProfile?.name || (parsedResume?.extras as any)?.candidate_name || 'Uploaded Resume';
        candidateList.unshift({
          id: 'active_candidate',
          name: 'Active: ' + customName,
        });
      }
      setCandidates(candidateList);

      const jdList = [...data.jds];
      if (globalSelectedJd) {
        const jdSource = 'source_file' in globalSelectedJd ? globalSelectedJd.source_file : globalSelectedJd.filename;
        const jdRole = 'role' in globalSelectedJd ? globalSelectedJd.role : ('title' in globalSelectedJd ? globalSelectedJd.title : 'Role');
        jdList.unshift({
          id: 'active_jd',
          company: globalSelectedJd.company || 'Active Target JD',
          role: jdRole || 'Target Role',
          source_file: jdSource || 'active_jd.pdf',
        });
      }
      setJds(jdList);

      if (!initialCandidateId && candidateList.length > 0) {
        setSelectedCandidate(candidateList[0].id);
      }
      if (!initialJdId && jdList.length > 0) {
        setSelectedJd(jdList[0].id);
      }
    });
  }, [currentProfile, parsedResume, globalSelectedJd, initialCandidateId, initialJdId]);

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
        jd_skills: isCustomJd && globalSelectedJd && 'skills' in globalSelectedJd ? globalSelectedJd.skills : undefined,
        jd_source_file: isCustomJd && globalSelectedJd ? ('source_file' in globalSelectedJd ? globalSelectedJd.source_file : globalSelectedJd.filename) : undefined,
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

  return (
    <div className="space-y-6">
      {/* Header & Controls bar */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-100 text-indigo-700 uppercase tracking-wide">
                Pillar 3: 3-Layer Matching
              </span>
              <span className="text-xs text-slate-400">|</span>
              <span className="text-xs text-slate-500 font-medium">Explainable Skill Gaps & Dependencies</span>
            </div>
            <h1 className="text-2xl font-black text-slate-900 mt-1 tracking-tight">
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

        {/* Candidate & JD Selectors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-slate-100">
          {/* Candidate Switcher */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Select Candidate Profile
            </label>
            <div className="flex flex-col gap-1.5">
              <select
                value={selectedCandidate}
                onChange={(e) => setSelectedCandidate(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {candidates.map((c) => (
                  <option key={c.id} value={c.id}>
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
                    className={`text-[11px] px-2.5 py-1 rounded-lg font-medium transition-all ${
                      selectedCandidate === c.id
                        ? 'bg-slate-900 text-white shadow-xs'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
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
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Select Job Description (Target Role)
            </label>
            <select
              value={selectedJd}
              onChange={(e) => setSelectedJd(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {jds.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.company} — {j.role}
                </option>
              ))}
            </select>
            {activeJd && (
              <p className="text-xs text-slate-400 mt-2 font-mono flex items-center gap-1">
                <span>📄 Source:</span>
                <span className="font-semibold text-slate-600">{activeJd.source_file}</span>
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div className="flex flex-col items-center justify-center p-16 bg-white rounded-2xl border border-slate-200 text-slate-500">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-3"></div>
          <p className="text-sm font-medium">Matching candidate skills against JD...</p>
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800">
          <p className="font-bold text-sm">Failed to compute match</p>
          <p className="text-xs mt-1">{error}</p>
        </div>
      ) : matchResult ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Score Ring & Quick Summary */}
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col items-center">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4 text-center">
                Match Readiness Score
              </h3>
              <ScoreRing score={matchResult.match_score} />

              <div className="w-full grid grid-cols-2 gap-3 mt-6 pt-6 border-t border-slate-100">
                <div className="bg-emerald-50/60 border border-emerald-100 p-3 rounded-xl text-center">
                  <div className="text-2xl font-black text-emerald-700">
                    {matchResult.matched_skills.length}
                  </div>
                  <div className="text-[11px] font-semibold text-emerald-800 uppercase mt-0.5">
                    Matched Skills
                  </div>
                </div>

                <div className="bg-amber-50/60 border border-amber-100 p-3 rounded-xl text-center">
                  <div className="text-2xl font-black text-amber-700">
                    {matchResult.missing_skills.length}
                  </div>
                  <div className="text-[11px] font-semibold text-amber-800 uppercase mt-0.5">
                    Missing Gaps
                  </div>
                </div>
              </div>

              {/* Explanatory summary text */}
              <div className="mt-4 p-3 bg-slate-50 rounded-xl text-xs text-slate-600 border border-slate-200/60 w-full">
                <span className="font-semibold text-slate-800">Scoring formula:</span>{' '}
                Weighted sum of credits (must-have=2, nice-to-have=1) divided by total weight. Gaps prioritized by prerequisites.
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

