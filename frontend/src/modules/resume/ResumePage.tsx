import React, { useState, useEffect, useRef } from 'react';
import { useApp } from '../../context/AppContext';
import { getResumes, parseResume, uploadResumeFile } from '../../api';
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
  Award,
  FileText,
} from 'lucide-react';

export const ResumePage: React.FC = () => {
  const { parsedResume, setParsedResume, setCurrentStep } = useApp();
  const [resumes, setResumes] = useState<SampleResume[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string>('res-1');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'skills' | 'experience' | 'projects'>('skills');

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
    } catch (err: any) {
      setUploadError(err.message || 'Failed to parse uploaded resume document.');
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const stuffedSkillsCount = parsedResume?.skills.filter((s: Skill) => s.stuffing_flag).length || 0;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header Banner */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300">
            Module 2: Resume Parsing & Privacy Redaction (Arushi)
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

      {/* Upload Zone & Sample Resumes Grid */}
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
            Drag & drop or click to upload (.pdf, .docx)
          </p>
          <span className="mt-3 text-[11px] font-semibold text-brand-600 dark:text-brand-400 bg-brand-100/60 dark:bg-brand-900/40 px-2.5 py-1 rounded-lg">
            Live Local Parser
          </span>
        </div>

        {/* Sample Resumes */}
        <div className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-3">
          {resumes.map((res) => {
            const isSelected = selectedResumeId === res.id;
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

      {/* Upload Error Banner */}
      {uploadError && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0" />
          <span>{uploadError}</span>
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
        <div className="space-y-4">
          {/* Summary Banner */}
          <div className="p-5 rounded-2xl border border-brand-200 dark:border-brand-900 bg-gradient-to-r from-brand-50/70 to-indigo-50/50 dark:from-brand-950/30 dark:to-indigo-950/30 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-brand-600 text-white rounded-xl shadow-glow">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 dark:text-white text-base">
                  {parsedResume.source_file}
                </h4>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
                  Extracted <span className="font-bold text-brand-600">{parsedResume.skills.length} skills</span>.
                  {stuffedSkillsCount > 0 ? (
                    <span className="text-amber-600 dark:text-amber-400 font-semibold ml-1">
                      ⚠️ {stuffedSkillsCount} skill(s) flagged for stuffing (downgraded confidence).
                    </span>
                  ) : (
                    <span className="text-emerald-600 dark:text-emerald-400 font-semibold ml-1">
                      All skills backed by project or experience evidence.
                    </span>
                  )}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab('skills')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                  activeTab === 'skills'
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100'
                }`}
              >
                Skills ({parsedResume.skills.length})
              </button>
              <button
                onClick={() => setActiveTab('experience')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                  activeTab === 'experience'
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100'
                }`}
              >
                Experience
              </button>
              <button
                onClick={() => setActiveTab('projects')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                  activeTab === 'projects'
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100'
                }`}
              >
                Projects & Extras
              </button>
            </div>
          </div>

          {/* Tab 1: Skills Table */}
          {activeTab === 'skills' && (
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800 uppercase tracking-wider font-semibold">
                    <tr>
                      <th className="py-3 px-4">Skill</th>
                      <th className="py-3 px-3">Category</th>
                      <th className="py-3 px-3">Confidence</th>
                      <th className="py-3 px-3">Stuffing Check</th>
                      <th className="py-3 px-4">Supporting Evidence</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-medium">
                    {parsedResume.skills.map((skill: Skill, idx: number) => {
                      const isStuffed = Boolean(skill.stuffing_flag);
                      const conf = (skill.confidence || 'medium').toLowerCase();

                      return (
                        <tr
                          key={idx}
                          className={`hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition-colors ${
                            isStuffed ? 'bg-amber-50/30 dark:bg-amber-950/10' : ''
                          }`}
                        >
                          <td className="py-3 px-4 font-bold text-slate-900 dark:text-white">
                            {skill.skill_name}
                          </td>
                          <td className="py-3 px-3">
                            <span className="px-2 py-0.5 rounded-md text-[11px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-mono">
                              {skill.category_code}
                            </span>
                          </td>
                          <td className="py-3 px-3">
                            <span
                              className={`px-2 py-0.5 rounded-full text-[11px] font-semibold uppercase ${
                                conf === 'high'
                                  ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300'
                                  : conf === 'medium'
                                  ? 'bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300'
                                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                              }`}
                            >
                              {conf}
                            </span>
                          </td>
                          <td className="py-3 px-3">
                            {isStuffed ? (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300">
                                <AlertTriangle className="w-3 h-3 text-amber-500" />
                                Stuffed (No Evidence)
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                                <CheckCircle className="w-3 h-3 text-emerald-500" />
                                Verified in Text
                              </span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-slate-500 dark:text-slate-400 italic max-w-md truncate">
                            {skill.evidence || (isStuffed ? 'Listed in skills list without supporting project mention' : 'None')}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Tab 2: Experience */}
          {activeTab === 'experience' && (
            <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
              <h4 className="font-bold text-slate-900 dark:text-white text-base flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-brand-600" />
                Work Experience & Internships
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
                          <h5 className="font-bold text-slate-900 dark:text-white text-sm">
                            {exp.role || 'Engineer'}
                          </h5>
                          <p className="text-xs font-semibold text-brand-600 dark:text-brand-400">
                            {exp.company || 'Company'}
                          </p>
                        </div>
                        {exp.duration && (
                          <span className="text-[11px] font-mono text-slate-400 bg-slate-200 dark:bg-slate-700 px-2 py-0.5 rounded">
                            {exp.duration}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-600 dark:text-slate-300 mt-2">
                        {exp.summary || exp.description || 'No description provided.'}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">No formal work experience parsed.</p>
              )}
            </div>
          )}

          {/* Tab 3: Projects & Extras */}
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
                  <Award className="w-4 h-4 text-brand-600" />
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
                  Projects & Deliverables
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
        </div>
      )}

      {/* Stepper Navigation */}
      <div className="flex justify-between items-center pt-4 border-t border-slate-200 dark:border-slate-800">
        <button
          onClick={() => setCurrentStep(1)}
          className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
        >
          <ArrowLeft className="w-4 h-4" /> Back to JD Analytics
        </button>

        <button
          onClick={() => setCurrentStep(3)}
          className="flex items-center gap-2 px-6 py-2.5 text-sm font-semibold text-white bg-slate-900 dark:bg-white dark:text-slate-900 rounded-xl hover:opacity-90 transition-all shadow-md"
        >
          Proceed to Step 3: Candidate Profile Form
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
