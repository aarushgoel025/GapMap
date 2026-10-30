import React, { useState, useEffect, useRef } from 'react';
import { useApp } from '../../context/AppContext';
import { getResumes, parseResume, uploadResumeFile, verifyGithub } from '../../api';
import type { GitHubVerificationResponse } from '../../api';
import type { SampleResume, Skill } from '../../types';
import {
  FileCode,
  ArrowRight,
  ArrowLeft,
  CheckCircle,
  RefreshCw,
  UploadCloud,
  ShieldCheck,
  AlertTriangle,
  GraduationCap,
  Briefcase,
  Layers,
  FileText,
  RotateCcw,
  User,
  X,
  GitBranch,
  ExternalLink,
  Sparkles,
  
} from 'lucide-react';

export const ResumePage: React.FC = () => {
  const { parsedResume, setParsedResume, setCurrentStep } = useApp();
  const [resumes, setResumes] = useState<SampleResume[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string>('res-1');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'skills' | 'experience' | 'projects'>('skills');
  const [githubUrl, setGithubUrl] = useState<string>('');
  const [githubConsent, setGithubConsent] = useState<boolean>(true);
  const [isVerifyingGithub, setIsVerifyingGithub] = useState<boolean>(false);
  const [githubResult, setGithubResult] = useState<GitHubVerificationResponse | null>(null);
  const [githubError, setGithubError] = useState<string | null>(null);

  // When a resume is parsed, collapse the demo cards and upload box so the screen stays clean
  const [isPickerOpen, setIsPickerOpen] = useState<boolean>(!parsedResume);

  useEffect(() => {
    if (parsedResume) {
      const extraObj = (parsedResume.extras || {}) as Record<string, any>;
      const gh = extraObj.github_url || '';
      if (gh && !githubUrl) {
        setGithubUrl(gh);
      }
    }
  }, [parsedResume]);

  const handleVerifyGithub = async () => {
    if (!githubUrl.trim()) {
      setGithubError('Please enter a GitHub profile username or URL');
      return;
    }
    if (!githubConsent) {
      setGithubError('Please consent to checking public GitHub repositories');
      return;
    }
    setIsVerifyingGithub(true);
    setGithubError(null);
    try {
      const res = await verifyGithub(githubUrl.trim(), parsedResume?.skills || []);
      setGithubResult(res);
      if (res && res.verified_skills && parsedResume) {
        setParsedResume({
          ...parsedResume,
          skills: res.verified_skills,
          extras: {
            ...parsedResume.extras,
            github_url: githubUrl.trim(),
            github_verified: true,
            github_data: res,
          },
        });
      }
    } catch (err: any) {
      setGithubError(err.message || 'Failed to verify GitHub profile');
    } finally {
      setIsVerifyingGithub(false);
    }
  };

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    getResumes().then(setResumes);
  }, []);

  const handleParseSample = async (resume: SampleResume) => {
    setIsLoading(true);
    setUploadError(null);
    setSelectedResumeId(resume.id);
    try {
      const result = await parseResume(resume.filename);
      setParsedResume(result);
      setIsPickerOpen(false); // Hide demo cards once selected!
    } catch (err: any) {
      setUploadError(err.message || 'Failed to parse sample resume.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'pdf' && ext !== 'docx') {
      setUploadError('Unsupported file format. Please upload a .pdf or .docx resume.');
      return;
    }

    setIsLoading(true);
    setUploadError(null);
    setSelectedResumeId('custom-upload');

    try {
      const result = await uploadResumeFile(file);
      setParsedResume(result);
      setIsPickerOpen(false); // Hide upload card once uploaded!
    } catch (err: any) {
      setUploadError(err.message || 'Failed to parse uploaded resume document. Please verify backend connection.');
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const stuffedSkillsCount = parsedResume?.skills.filter((s: Skill) => s.stuffing_flag).length || 0;

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Header Banner */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300">
            Module 2: Resume Parsing & Privacy Redaction
          </span>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">Extract & Parse Candidate Resume</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Upload a real PDF/DOCX or select a candidate CV. Applies PII redaction, section splitting, and evidence-backed skill stuffing detection.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/50 text-emerald-700 dark:text-emerald-300 text-xs font-medium">
          <ShieldCheck className="w-4 h-4 text-emerald-500" />
          <span>PII Scrubbing Active</span>
        </div>
      </div>

      {/* Upload Error Banner */}
      {uploadError && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0" />
            <span>{uploadError}</span>
          </div>
          <button
            onClick={() => setUploadError(null)}
            className="text-rose-400 hover:text-rose-600 dark:hover:text-rose-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Active Selected Resume Banner (Shows when a resume is parsed, with button to switch/browse demos) */}
      {parsedResume && !isPickerOpen && (
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-brand-200 dark:border-brand-900/60 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-600 text-white flex items-center justify-center shadow-md shrink-0">
              <User className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  {(parsedResume.extras as any)?.candidate_name ||
                    (parsedResume.extras as any)?.name ||
                    (parsedResume as any).candidate_name ||
                    'Candidate Profile'}
                </h3>
                {parsedResume.role && (
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                    {parsedResume.role}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 flex flex-wrap items-center gap-2">
                <span>
                  Source: <strong className="font-mono text-slate-700 dark:text-slate-300">{parsedResume.source_file}</strong>
                </span>
                <span>•</span>
                <span className="text-brand-600 dark:text-brand-400 font-semibold">{parsedResume.skills.length} skills parsed</span>
                {stuffedSkillsCount > 0 ? (
                  <>
                    <span>•</span>
                    <span className="text-amber-600 dark:text-amber-400 font-bold flex items-center gap-1">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      {stuffedSkillsCount} Stuffed Skills Flagged
                    </span>
                  </>
                ) : (
                  <>
                    <span>•</span>
                    <span className="text-emerald-600 dark:text-emerald-400 font-semibold">100% Evidenced</span>
                  </>
                )}
              </p>
            </div>
          </div>

          <button
            onClick={() => setIsPickerOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all self-start sm:self-auto cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Switch Resume / Upload Another</span>
          </button>
        </div>
      )}

      {/* Resume Picker Section: Upload Real Resume + Demo Resumes Grid (Hides when a resume is active unless opened) */}
      {isPickerOpen && (
        <div className="space-y-3 animate-fadeIn">
          {parsedResume && (
            <div className="flex justify-between items-center px-1">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Select a benchmark resume or upload your custom resume:
              </span>
              <button
                onClick={() => setIsPickerOpen(false)}
                className="text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 flex items-center gap-1 cursor-pointer"
              >
                <span>Close (Keep Current Resume)</span>
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
            {/* Real File Upload Card */}
            <div
              onClick={() => fileInputRef.current?.click()}
              className={`lg:col-span-1 p-5 rounded-2xl border-2 border-dashed cursor-pointer transition-all flex flex-col justify-center items-center text-center group ${
                selectedResumeId === 'custom-upload'
                  ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-950/30 ring-2 ring-brand-500/20'
                  : 'border-slate-300 dark:border-slate-700 hover:border-brand-400 bg-white dark:bg-slate-900'
              }`}
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept=".pdf,.docx"
                className="hidden"
              />
              <div className="p-3 rounded-2xl bg-brand-50 dark:bg-brand-950 text-brand-600 group-hover:scale-110 transition-transform mb-3">
                <UploadCloud className="w-6 h-6" />
              </div>
              <h4 className="font-bold text-slate-900 dark:text-white text-sm">Upload Real Resume</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Drag &amp; drop or click to upload (.pdf, .docx)
              </p>
              <span className="mt-3 text-[11px] font-semibold text-brand-600 dark:text-brand-400 bg-brand-100/60 dark:bg-brand-900/40 px-2.5 py-1 rounded-lg">
                Live Local Parser
              </span>
            </div>

            {/* Sample Benchmark Resumes */}
            <div className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-3">
              {resumes.map((res) => {
                const isSelected =
                  selectedResumeId === res.id ||
                  (parsedResume && parsedResume.source_file === res.filename);
                return (
                  <div
                    key={res.id}
                    onClick={() => handleParseSample(res)}
                    className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                      isSelected
                        ? 'border-brand-500 bg-brand-50/40 dark:bg-brand-950/20 ring-2 ring-brand-500/30'
                        : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-brand-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-brand-600">
                        <FileCode className="w-4 h-4" />
                      </span>
                      {isSelected && parsedResume && <CheckCircle className="w-4 h-4 text-brand-600" />}
                    </div>
                    <h4 className="font-bold text-slate-900 dark:text-white text-sm">{res.candidate_name}</h4>
                    <p className="text-xs font-semibold text-brand-600 dark:text-brand-400 mt-0.5">{res.role}</p>
                    <p className="text-[11px] text-slate-400 mt-2 font-mono truncate">{res.filename}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col items-center justify-center gap-3">
          <RefreshCw className="w-8 h-8 text-brand-600 animate-spin" />
          <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
            Parsing resume, scrubbing PII, and checking for skill stuffing...
          </p>
        </div>
      )}

      {/* Extraction Results Display */}
      {parsedResume && !isLoading && (
        <div className="space-y-4 animate-fadeIn">
          {/* Tabs Navigation */}
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab('skills')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                  activeTab === 'skills'
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100'
                }`}
              >
                Skills &amp; Stuffing Check ({parsedResume.skills.length})
              </button>
              <button
                onClick={() => setActiveTab('experience')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                  activeTab === 'experience'
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100'
                }`}
              >
                Experience &amp; Internships ({parsedResume.extras?.experience?.length || 0})
              </button>
              <button
                onClick={() => setActiveTab('projects')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                  activeTab === 'projects'
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100'
                }`}
              >
                Projects &amp; Education
              </button>
            </div>
            <span className="text-xs text-slate-400 hidden sm:inline">
              Candidate Resume Data Layer
            </span>
          </div>

          {/* 1. Skills & Stuffing Audit Tab */}
          {activeTab === 'skills' && (
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
                  <thead className="bg-slate-50 dark:bg-slate-800/60 uppercase font-bold text-slate-400 text-[10px] tracking-wider border-b border-slate-200 dark:border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Skill Name</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Confidence</th>
                      <th className="px-4 py-3">Stuffing Check</th>
                      <th className="px-4 py-3">Extracted Evidence</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-medium">
                    {parsedResume.skills.map((skill: Skill, idx: number) => {
                      const isStuffed = Boolean(skill.stuffing_flag);
                      const hasGithub = Boolean(skill.verified_by && skill.verified_by.includes('github'));
                      const conf = (skill.confidence || 'medium').toLowerCase();

                      return (
                        <tr
                          key={idx}
                          className={`hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors ${
                            isStuffed
                              ? 'bg-amber-50/20 dark:bg-amber-950/10'
                              : hasGithub
                              ? 'bg-purple-50/30 dark:bg-purple-950/20'
                              : ''
                          }`}
                        >
                          <td className="px-4 py-3 font-bold text-slate-900 dark:text-white flex items-center gap-1.5 flex-wrap">
                            <span>{skill.skill_name}</span>
                            {hasGithub && (
                              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-bold bg-purple-100 text-purple-800 dark:bg-purple-900/60 dark:text-purple-200 border border-purple-300 dark:border-purple-700">
                                <GitBranch className="w-2.5 h-2.5 text-purple-600 dark:text-purple-400" />
                                GitHub
                              </span>
                            )}
                          </td>
                          <td className="px-4 py-3 font-mono text-[11px] text-slate-500">
                            {skill.category_code}
                          </td>
                          <td className="px-4 py-3">
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                                conf === 'high'
                                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                                  : conf === 'medium'
                                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                                  : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                              }`}
                            >
                              {conf}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            {isStuffed ? (
                              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300 dark:border-amber-800">
                                <AlertTriangle className="w-3 h-3 text-amber-600" />
                                Stuffed (No Evidence)
                              </span>
                            ) : hasGithub ? (
                              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-900 dark:bg-purple-950/80 dark:text-purple-300 border border-purple-300 dark:border-purple-800 shadow-xs">
                                <GitBranch className="w-3 h-3 text-purple-600 dark:text-purple-400" />
                                Verified via GitHub (1.2x Boost)
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
                                <CheckCircle className="w-3 h-3 text-emerald-500" />
                                Verified in Text
                              </span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-slate-500 italic max-w-sm truncate" title={skill.evidence || 'No evidence extracted'}>
                            {skill.evidence ? `"${skill.evidence}"` : <span className="not-italic text-slate-400">None detected</span>}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 2. Experience Tab */}
          {activeTab === 'experience' && (
            <div className="p-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
              <h4 className="font-bold text-slate-900 dark:text-white text-sm flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-brand-600" />
                Work Experience &amp; Internships
              </h4>
              {parsedResume.extras?.experience && parsedResume.extras.experience.length > 0 ? (
                <div className="space-y-3">
                  {parsedResume.extras.experience.map((exp: any, i: number) => (
                    <div
                      key={i}
                      className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-800"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h5 className="font-bold text-slate-900 dark:text-white text-sm">{exp.role || 'Software Role'}</h5>
                          <p className="text-xs font-semibold text-brand-600 dark:text-brand-400">{exp.company || 'Tech Company'}</p>
                        </div>
                        <span className="text-[11px] text-slate-400 font-mono">{exp.duration || 'Past'}</span>
                      </div>
                      <p className="text-xs text-slate-600 dark:text-slate-400 mt-2">{exp.description || 'No description extracted.'}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">No explicit experience entries found in this document.</p>
              )}
            </div>
          )}

          {/* 3. Projects & Education Tab */}
          {activeTab === 'projects' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Education */}
              <div className="p-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3">
                <h4 className="font-bold text-slate-900 dark:text-white text-sm flex items-center gap-2">
                  <GraduationCap className="w-4 h-4 text-brand-600" />
                  Education
                </h4>
                <p className="text-xs text-slate-700 dark:text-slate-300 font-medium">
                  {parsedResume.extras?.education || 'Not specified'}
                </p>
              </div>

              {/* Certifications */}
              <div className="p-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3">
                <h4 className="font-bold text-slate-900 dark:text-white text-sm flex items-center gap-2">
                  <FileText className="w-4 h-4 text-brand-600" />
                  Certifications
                </h4>
                {parsedResume.extras?.certifications && parsedResume.extras.certifications.length > 0 ? (
                  <ul className="text-xs space-y-1 text-slate-700 dark:text-slate-300 list-disc list-inside">
                    {parsedResume.extras.certifications.map((c: string, idx: number) => (
                      <li key={idx}>{c}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-400 italic">No certifications parsed.</p>
                )}
              </div>

              {/* Projects */}
              <div className="md:col-span-2 p-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3">
                <h4 className="font-bold text-slate-900 dark:text-white text-sm flex items-center gap-2">
                  <Layers className="w-4 h-4 text-brand-600" />
                  Projects &amp; Deliverables
                </h4>
                {parsedResume.extras?.projects && parsedResume.extras.projects.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {parsedResume.extras.projects.map((proj: any, idx: number) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-800"
                      >
                        <h5 className="font-bold text-slate-900 dark:text-white text-xs">
                          {proj.title || proj.name || 'Project'}
                        </h5>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                          {proj.description || 'No description.'}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 italic">No projects parsed.</p>
                )}
              </div>
            </div>
          )}

          {/* Evidence Engine: GitHub Repository Verification */}
          <div className="p-5 bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 text-white rounded-2xl border border-slate-800 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-white/10 text-white">
                  <GitBranch className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-white flex items-center gap-2">
                    Evidence Engine: GitHub Repository Verification
                    <span className="text-[10px] bg-brand-500/20 text-brand-300 border border-brand-500/30 px-2 py-0.5 rounded-full font-semibold">
                      1.2x Multi-Source Boost
                    </span>
                  </h4>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Live audit of public repos &amp; languages to verify practical code evidence and clear false stuffing flags.
                  </p>
                </div>
              </div>

              {parsedResume.extras?.github_url && (
                <span className="text-xs text-emerald-400 font-mono bg-emerald-950/60 border border-emerald-800/60 px-2.5 py-1 rounded-lg flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5" />
                  Auto-detected from resume
                </span>
              )}
            </div>

            {/* Input row */}
            <div className="flex flex-col sm:flex-row gap-2">
              <div className="relative flex-1">
                <GitBranch className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  placeholder="e.g. aarushgoel025 or https://github.com/aarushgoel025"
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500/40"
                />
              </div>
              <button
                onClick={handleVerifyGithub}
                disabled={isVerifyingGithub || !githubUrl.trim()}
                className="px-5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-md cursor-pointer"
              >
                {isVerifyingGithub ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Verifying Repositories...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Verify with GitHub</span>
                  </>
                )}
              </button>
            </div>

            {/* Consent Checkbox */}
            <label className="flex items-center gap-2 text-[11px] text-slate-400 cursor-pointer">
              <input
                type="checkbox"
                checked={githubConsent}
                onChange={(e) => setGithubConsent(e.target.checked)}
                className="rounded border-slate-700 bg-white/5 text-brand-500 focus:ring-brand-500/30"
              />
              <span>
                I consent to querying public GitHub repository metadata and languages (Section F Governance audit logged).
              </span>
            </label>

            {/* GitHub Error */}
            {githubError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{githubError}</span>
              </div>
            )}

            {/* GitHub Verified Result Card */}
            {githubResult && (
              <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3 animate-fadeIn">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {githubResult.avatar_url ? (
                      <img
                        src={githubResult.avatar_url}
                        alt="Avatar"
                        className="w-10 h-10 rounded-full border border-white/20"
                      />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center font-bold text-sm">
                        {githubResult.github_user?.[0]?.toUpperCase() || 'GH'}
                      </div>
                    )}
                    <div>
                      <h5 className="font-bold text-xs text-white flex items-center gap-2">
                        {githubResult.name || githubResult.github_user}
                        <span className="text-[10px] text-slate-400 font-mono">@{githubResult.github_user}</span>
                      </h5>
                      {githubResult.bio && <p className="text-[11px] text-slate-300 mt-0.5 line-clamp-1">{githubResult.bio}</p>}
                    </div>
                  </div>
                  <span className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[11px] font-semibold flex items-center gap-1.5">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                    Verified ({githubResult.verified_count || 0} skills)
                  </span>
                </div>

                {/* Top Languages */}
                {githubResult.top_languages && githubResult.top_languages.length > 0 && (
                  <div>
                    <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider">
                      Detected Repository Languages:
                    </span>
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      {githubResult.top_languages.map((lang, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 rounded-md bg-white/10 text-white text-[11px] font-mono"
                        >
                          {lang}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Repos preview */}
                {githubResult.repos && githubResult.repos.length > 0 && (
                  <div>
                    <span className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider">
                      Recent Public Repositories Inspected:
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 mt-1.5">
                      {githubResult.repos.slice(0, 3).map((repo, idx) => (
                        <a
                          key={idx}
                          href={repo.html_url}
                          target="_blank"
                          rel="noreferrer"
                          className="p-2.5 rounded-lg bg-black/30 hover:bg-black/50 border border-white/5 transition-colors block text-left"
                        >
                          <div className="flex items-center justify-between text-xs font-semibold text-brand-300">
                            <span className="truncate">{repo.name}</span>
                            <ExternalLink className="w-3 h-3 text-slate-400" />
                          </div>
                          <div className="text-[10px] text-slate-400 mt-1 flex items-center gap-2">
                            <span className="text-emerald-400">{repo.language}</span>
                            {repo.stars > 0 && <span>★ {repo.stars}</span>}
                          </div>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Stepper Navigation */}
      <div className="flex justify-between items-center pt-6 border-t border-slate-200 dark:border-slate-800">
        <button
          onClick={() => setCurrentStep(1)}
          className="flex items-center gap-2 text-sm font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Step 1: JD Analytics
        </button>

        <button
          onClick={() => setCurrentStep(3)}
          className="flex items-center gap-2 px-6 py-2.5 text-sm font-semibold text-white bg-slate-900 dark:bg-white dark:text-slate-900 rounded-xl hover:opacity-90 transition-all shadow-md cursor-pointer"
        >
          Proceed to Step 3: Candidate Profile Form
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
