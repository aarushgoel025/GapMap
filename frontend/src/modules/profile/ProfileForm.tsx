import React, { useState, useEffect } from 'react';
import type {
  Profile,
  Skill,
  CategoryCode,
  Confidence,
} from '../../types';
import { CATEGORY_CODES } from '../../types';
import { createProfile, getProfile, updateProfile, listProfiles, verifyGithub } from '../../api';
import { useApp } from '../../context/AppContext';
import {
  User,
  Mail,
  GraduationCap,
  GitBranch,
  Upload,
  Plus,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  Save,
  Download,
  Sparkles,
  ShieldCheck,
  Briefcase,
  Trophy,
  Award,
  Layers,
  ChevronRight,
  RefreshCw,
} from 'lucide-react';

const COMMON_ROLES = [
  'Full Stack Developer',
  'Backend Engineer',
  'Frontend Engineer',
  'AI / ML Engineer',
  'Cloud / DevOps Engineer',
  'Systems Architect',
  'Data Engineer',
  'Security Engineer',
];

export const ProfileForm: React.FC = () => {
  const { parsedResume, profileId, setProfileId, setCurrentProfile, setCurrentStep } = useApp();

  // Form State
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [education, setEducation] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [githubConsent, setGithubConsent] = useState(false);
  const [preferredRoles, setPreferredRoles] = useState<string[]>(['Full Stack Developer']);
  const [customRoleInput, setCustomRoleInput] = useState('');
  const [cvFile, setCvFile] = useState('');

  // Lists
  const [skills, setSkills] = useState<Skill[]>([]);
  const [hackathons, setHackathons] = useState<{ name: string; project?: string; year?: string; award?: string }[]>([]);
  const [internships, setInternships] = useState<{ company: string; role: string; duration?: string; description?: string }[]>([]);
  const [certifications, setCertifications] = useState<string[]>([]);

  // Auto-filled tracking
  const [autoFilledFields, setAutoFilledFields] = useState<Record<string, boolean>>({});

  // UI States
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isVerifyingGithub, setIsVerifyingGithub] = useState(false);
  const [showLoadModal, setShowLoadModal] = useState(false);
  const [availableProfiles, setAvailableProfiles] = useState<Profile[]>([]);
  const [loadProfileInput, setLoadProfileInput] = useState('');

  // -------------------------------------------------------------------------
  // Pre-fill from parsedResume if available
  // -------------------------------------------------------------------------
  const applyResumeData = (resume: typeof parsedResume) => {
    if (!resume) return;

    const filled: Record<string, boolean> = {};

    if (resume.role && !preferredRoles.includes(resume.role)) {
      setPreferredRoles((prev) => [...prev, resume.role!]);
      filled['preferred_roles'] = true;
    }

    if (resume.source_file) {
      setCvFile(resume.source_file);
      filled['cv_file'] = true;
    }

    // Skills
    if (resume.skills && resume.skills.length > 0) {
      setSkills(resume.skills);
      filled['skills'] = true;
    }

    // Extras
    if (resume.extras) {
      if (resume.extras.education) {
        setEducation(resume.extras.education);
        filled['education'] = true;
      }
      if (Array.isArray(resume.extras.projects) && resume.extras.projects.length > 0) {
        setHackathons(
          resume.extras.projects.map((p) => ({
            name: p.name || 'Hackathon / Project',
            project: p.description || '',
            year: '2024',
          }))
        );
        filled['hackathons'] = true;
      }
      if (Array.isArray(resume.extras.experience) && resume.extras.experience.length > 0) {
        setInternships(
          resume.extras.experience.map((e) => ({
            company: e.company || 'Tech Company',
            role: e.role || 'Software Engineer',
            duration: e.duration || '3 months',
            description: e.description || '',
          }))
        );
        filled['internships'] = true;
      }
      if (Array.isArray(resume.extras.certifications) && resume.extras.certifications.length > 0) {
        setCertifications(resume.extras.certifications);
        filled['certifications'] = true;
      }
    }

    setAutoFilledFields(filled);
    setStatusMessage({ type: 'info', text: 'Form auto-populated from Parsed Resume!' });
  };

  useEffect(() => {
    if (parsedResume) {
      applyResumeData(parsedResume);
    }
  }, [parsedResume]);

  // -------------------------------------------------------------------------
  // Validation
  // -------------------------------------------------------------------------
  const validate = (): boolean => {
    const errs: Record<string, string> = {};

    if (!name.trim()) {
      errs['name'] = 'Full Name is required.';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email.trim()) {
      errs['email'] = 'Email is required.';
    } else if (!emailRegex.test(email.trim())) {
      errs['email'] = 'Please enter a valid email address.';
    }

    if (githubUrl.trim()) {
      try {
        const parsed = new URL(githubUrl.trim());
        if (!parsed.hostname.includes('github.com')) {
          errs['githubUrl'] = 'GitHub URL must point to github.com (e.g., https://github.com/username).';
        }
      } catch {
        errs['githubUrl'] = 'Please enter a valid URL (starting with https://).';
      }

      if (!githubConsent) {
        errs['githubConsent'] = 'Consent is required to verify GitHub projects.';
      }
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  // -------------------------------------------------------------------------
  // Save / Update Profile
  // -------------------------------------------------------------------------
  const handleSave = async () => {
    if (!validate()) {
      setStatusMessage({ type: 'error', text: 'Please resolve form validation errors before saving.' });
      return;
    }

    setIsSaving(true);
    setStatusMessage(null);

    const payload: Profile = {
      schema_version: '1.0',
      profile_id: profileId || undefined,
      name: name.trim(),
      email: email.trim(),
      education: education.trim(),
      github_url: githubUrl.trim(),
      skills,
      hackathons,
      internships,
      certifications,
      preferred_roles: preferredRoles,
      cv_file: cvFile,
    };

    try {
      let saved: Profile;
      if (profileId) {
        saved = await updateProfile(profileId, payload);
        setStatusMessage({ type: 'success', text: `Profile updated successfully! (ID: ${saved.profile_id})` });
      } else {
        saved = await createProfile(payload);
        if (saved.profile_id) {
          setProfileId(saved.profile_id);
        }
        setStatusMessage({ type: 'success', text: `Profile created successfully! (ID: ${saved.profile_id})` });
      }
      setCurrentProfile(saved);
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: `Save failed: ${err.message || 'Unknown error'}` });
    } finally {
      setIsSaving(false);
    }
  };

  // -------------------------------------------------------------------------
  // Load Profile
  // -------------------------------------------------------------------------
  const handleOpenLoadModal = async () => {
    setShowLoadModal(true);
    try {
      const list = await listProfiles();
      setAvailableProfiles(list);
    } catch (e) {
      console.warn('Could not fetch existing profiles:', e);
    }
  };

  const handleSelectProfileToLoad = (p: Profile) => {
    setName(p.name || '');
    setEmail(p.email || '');
    setEducation(p.education || '');
    setGithubUrl(p.github_url || '');
    setGithubConsent(Boolean(p.github_url));
    setPreferredRoles(p.preferred_roles || []);
    setCvFile(p.cv_file || '');
    setSkills(p.skills || []);
    setHackathons(p.hackathons || []);
    setInternships(p.internships || []);
    setCertifications(p.certifications || []);

    if (p.profile_id) {
      setProfileId(p.profile_id);
    }
    setCurrentProfile(p);
    setAutoFilledFields({});
    setShowLoadModal(false);
    setStatusMessage({ type: 'success', text: `Loaded profile "${p.name || p.profile_id}"` });
  };

  const handleLoadById = async () => {
    if (!loadProfileInput.trim()) return;
    try {
      const p = await getProfile(loadProfileInput.trim());
      handleSelectProfileToLoad(p);
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: `Load failed: ${err.message}` });
    }
  };

  // -------------------------------------------------------------------------
  // GitHub Verification Trigger
  // -------------------------------------------------------------------------
  const handleVerifyGithubSkills = async () => {
    if (!githubUrl.trim()) {
      setErrors((prev) => ({ ...prev, githubUrl: 'Enter GitHub URL first' }));
      return;
    }
    setIsVerifyingGithub(true);
    try {
      const res = await verifyGithub(githubUrl.trim(), skills);
      if (res && res.verified_skills) {
        setSkills(res.verified_skills);
        setStatusMessage({ type: 'success', text: 'GitHub verification completed: skills verified!' });
      }
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: `Verification failed: ${err.message}` });
    } finally {
      setIsVerifyingGithub(false);
    }
  };

  // -------------------------------------------------------------------------
  // Skills Management
  // -------------------------------------------------------------------------
  const addSkill = () => {
    const newSkill: Skill = {
      skill_name: '',
      category_code: 'COD',
      confidence: 'medium',
      level_estimate: 5,
      evidence: '',
      verified_by: [],
      stuffing_flag: false,
    };
    setSkills([...skills, newSkill]);
  };

  const updateSkill = (index: number, patch: Partial<Skill>) => {
    setSkills((prev) => {
      const copy = [...prev];
      copy[index] = { ...copy[index], ...patch };
      return copy;
    });
  };

  const removeSkill = (index: number) => {
    setSkills((prev) => prev.filter((_, i) => i !== index));
  };

  // -------------------------------------------------------------------------
  // File Upload
  // -------------------------------------------------------------------------
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setCvFile(file.name);
      setStatusMessage({ type: 'info', text: `CV attached: "${file.name}"` });
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Header & Actions Bar */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-6 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300">
              Module 3: Profile Contract
            </span>
            {profileId && (
              <span className="text-xs text-slate-500 font-mono">ID: {profileId.slice(0, 8)}...</span>
            )}
          </div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">Candidate Profile & Skillset</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Edit, audit, and verify candidate skills, credentials, and work history.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleOpenLoadModal}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-200 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 rounded-xl transition-all"
          >
            <Download className="w-4 h-4 text-slate-500" />
            Load Profile
          </button>

          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center gap-2 px-5 py-2 text-sm font-semibold text-white bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 rounded-xl shadow-glow transition-all disabled:opacity-50"
          >
            {isSaving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {profileId ? 'Update Profile' : 'Save Profile'}
          </button>
        </div>
      </div>

      {/* Notifications / Alerts */}
      {statusMessage && (
        <div
          className={`p-4 rounded-xl flex items-center justify-between gap-3 text-sm transition-all ${
            statusMessage.type === 'success'
              ? 'bg-emerald-50 text-emerald-800 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
              : statusMessage.type === 'error'
              ? 'bg-rose-50 text-rose-800 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800'
              : 'bg-brand-50 text-brand-800 border border-brand-200 dark:bg-brand-950/40 dark:text-brand-300 dark:border-brand-800'
          }`}
        >
          <div className="flex items-center gap-2">
            {statusMessage.type === 'success' && <CheckCircle2 className="w-5 h-5 text-emerald-600" />}
            {statusMessage.type === 'error' && <AlertTriangle className="w-5 h-5 text-rose-600" />}
            {statusMessage.type === 'info' && <Sparkles className="w-5 h-5 text-brand-600" />}
            <span>{statusMessage.text}</span>
          </div>
          <button
            onClick={() => setStatusMessage(null)}
            className="text-xs font-semibold hover:underline opacity-80"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* SECTION 1: Personal & Education */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
        <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2 mb-4">
          <User className="w-5 h-5 text-brand-600" />
          General Information & Credentials
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Full Name */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                Full Name <span className="text-rose-500">*</span>
              </label>
              {autoFilledFields['name'] && (
                <span className="text-xs px-2 py-0.5 rounded-md bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300 flex items-center gap-1 font-medium">
                  <Sparkles className="w-3 h-3" /> Auto-filled
                </span>
              )}
            </div>
            <div className="relative">
              <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Jane Doe"
                className={`w-full pl-10 pr-4 py-2 text-sm rounded-xl border bg-slate-50/50 dark:bg-slate-800/50 text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:outline-none transition-all ${
                  errors['name'] ? 'border-rose-400' : 'border-slate-300 dark:border-slate-700'
                }`}
              />
            </div>
            {errors['name'] && <p className="text-xs text-rose-500 mt-1">{errors['name']}</p>}
          </div>

          {/* Email */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                Email Address <span className="text-rose-500">*</span>
              </label>
              {autoFilledFields['email'] && (
                <span className="text-xs px-2 py-0.5 rounded-md bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300 flex items-center gap-1 font-medium">
                  <Sparkles className="w-3 h-3" /> Auto-filled
                </span>
              )}
            </div>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="jane.doe@example.com"
                className={`w-full pl-10 pr-4 py-2 text-sm rounded-xl border bg-slate-50/50 dark:bg-slate-800/50 text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:outline-none transition-all ${
                  errors['email'] ? 'border-rose-400' : 'border-slate-300 dark:border-slate-700'
                }`}
              />
            </div>
            {errors['email'] && <p className="text-xs text-rose-500 mt-1">{errors['email']}</p>}
          </div>

          {/* Education */}
          <div className="md:col-span-2">
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                Education & Degree Details
              </label>
              {autoFilledFields['education'] && (
                <span className="text-xs px-2 py-0.5 rounded-md bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300 flex items-center gap-1 font-medium">
                  <Sparkles className="w-3 h-3" /> Auto-filled from CV
                </span>
              )}
            </div>
            <div className="relative">
              <GraduationCap className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="text"
                value={education}
                onChange={(e) => setEducation(e.target.value)}
                placeholder="e.g. B.Tech Computer Science, Tier 1 University, GPA 3.9"
                className="w-full pl-10 pr-4 py-2 text-sm rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50 text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:outline-none transition-all"
              />
            </div>
          </div>

          {/* GitHub URL & Verification */}
          <div className="md:col-span-2 p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200/80 dark:border-slate-800">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-2">
              <label className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                <GitBranch className="w-4 h-4 text-slate-800 dark:text-slate-200" />
                GitHub Profile URL & Repository Verification
              </label>
              <button
                type="button"
                onClick={handleVerifyGithubSkills}
                disabled={isVerifyingGithub || !githubUrl}
                className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-900 text-white dark:bg-slate-700 hover:bg-slate-800 disabled:opacity-40 transition-all shadow-sm"
              >
                {isVerifyingGithub ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />}
                Trigger GitHub Code Verification
              </button>
            </div>

            <input
              type="url"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              placeholder="https://github.com/username"
              className={`w-full px-4 py-2 text-sm rounded-xl border bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:outline-none transition-all ${
                errors['githubUrl'] ? 'border-rose-400' : 'border-slate-300 dark:border-slate-700'
              }`}
            />
            {errors['githubUrl'] && <p className="text-xs text-rose-500 mt-1">{errors['githubUrl']}</p>}

            <label className="flex items-center gap-2.5 mt-3 text-xs text-slate-600 dark:text-slate-400 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={githubConsent}
                onChange={(e) => setGithubConsent(e.target.checked)}
                className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500 border-slate-300"
              />
              <span>I consent to automated GitHub repo code parsing and commit verification for my skillset claims.</span>
            </label>
            {errors['githubConsent'] && <p className="text-xs text-rose-500 mt-1">{errors['githubConsent']}</p>}
          </div>

          {/* CV Upload Section */}
          <div className="md:col-span-2">
            <label className="text-sm font-semibold text-slate-700 dark:text-slate-300 block mb-1.5">
              CV / Resume Attachment
            </label>
            <div className="flex flex-col sm:flex-row items-center gap-4 p-4 border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-xl hover:border-brand-400 transition-all bg-slate-50/50 dark:bg-slate-900/50">
              <div className="p-3 bg-brand-50 dark:bg-brand-950/60 rounded-xl text-brand-600">
                <Upload className="w-6 h-6" />
              </div>
              <div className="flex-1 text-center sm:text-left">
                <p className="text-sm font-medium text-slate-900 dark:text-white">
                  {cvFile ? `Attached File: ${cvFile}` : 'Upload candidate CV or Resume (PDF / DOCX)'}
                </p>
                <p className="text-xs text-slate-500">
                  {cvFile ? 'Filename stored in candidate profile contract' : 'Filename will be linked to profile metadata'}
                </p>
              </div>
              <label className="px-4 py-2 text-xs font-semibold bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl shadow-sm hover:bg-slate-100 cursor-pointer text-slate-700 dark:text-slate-200">
                Choose File
                <input type="file" onChange={handleFileUpload} className="hidden" accept=".pdf,.doc,.docx" />
              </label>
            </div>
          </div>

          {/* Preferred Roles Multi-Select */}
          <div className="md:col-span-2">
            <label className="text-sm font-semibold text-slate-700 dark:text-slate-300 block mb-2">
              Preferred Target Roles (Multi-Select)
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {COMMON_ROLES.map((role) => {
                const selected = preferredRoles.includes(role);
                return (
                  <button
                    key={role}
                    type="button"
                    onClick={() => {
                      setPreferredRoles((prev) =>
                        selected ? prev.filter((r) => r !== role) : [...prev, role]
                      );
                    }}
                    className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                      selected
                        ? 'bg-brand-600 text-white shadow-sm ring-1 ring-brand-500'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                    }`}
                  >
                    {selected ? '✓ ' : '+ '}
                    {role}
                  </button>
                );
              })}
            </div>
            {/* Add Custom Role */}
            <div className="flex gap-2">
              <input
                type="text"
                value={customRoleInput}
                onChange={(e) => setCustomRoleInput(e.target.value)}
                placeholder="Or add custom role title..."
                className="text-xs px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white"
              />
              <button
                type="button"
                onClick={() => {
                  if (customRoleInput.trim() && !preferredRoles.includes(customRoleInput.trim())) {
                    setPreferredRoles([...preferredRoles, customRoleInput.trim()]);
                    setCustomRoleInput('');
                  }
                }}
                className="px-3 py-1.5 text-xs font-semibold bg-slate-800 dark:bg-slate-700 text-white rounded-lg hover:bg-slate-900"
              >
                Add Role
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* SECTION 2: Skills Editor with Verified Badge & Stuffing Warning */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-brand-600" />
              Verified Skills Matrix ({skills.length})
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Evaluated with category classification, evidence quotes, and cross-verification badges.
            </p>
          </div>

          <button
            type="button"
            onClick={addSkill}
            className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950 border border-brand-200 dark:border-brand-800 rounded-xl hover:bg-brand-100 transition-all"
          >
            <Plus className="w-4 h-4" /> Add Skill
          </button>
        </div>

        {skills.length === 0 ? (
          <div className="text-center py-10 border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl">
            <Layers className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-600 dark:text-slate-300">No skills added yet</p>
            <p className="text-xs text-slate-400 mt-1">Pre-fill from Resume or click "Add Skill" above.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {skills.map((skill, idx) => {
              const isVerified = Array.isArray(skill.verified_by) && skill.verified_by.length > 0;
              const hasStuffingFlag = Boolean(skill.stuffing_flag);

              return (
                <div
                  key={idx}
                  className={`p-4 rounded-xl border transition-all ${
                    hasStuffingFlag
                      ? 'border-amber-300 bg-amber-50/40 dark:border-amber-900/60 dark:bg-amber-950/20'
                      : isVerified
                      ? 'border-emerald-200 bg-emerald-50/20 dark:border-emerald-900/40 dark:bg-emerald-950/10'
                      : 'border-slate-200 dark:border-slate-800 bg-slate-50/30 dark:bg-slate-800/20'
                  }`}
                >
                  <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-start">
                    {/* Skill Name */}
                    <div className="sm:col-span-4">
                      <div className="flex items-center justify-between mb-1">
                        <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                          Skill Name
                        </label>
                        {/* Status Badges */}
                        <div className="flex items-center gap-1.5">
                          {isVerified && (
                            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 flex items-center gap-0.5" title={`Verified by: ${skill.verified_by?.join(', ')}`}>
                              <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" />
                              Verified
                            </span>
                          )}
                          {hasStuffingFlag && (
                            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-300 flex items-center gap-0.5" title="Detected possible keyword stuffing in resume">
                              <AlertTriangle className="w-2.5 h-2.5 text-amber-600" />
                              Stuffing Flag
                            </span>
                          )}
                        </div>
                      </div>
                      <input
                        type="text"
                        value={skill.skill_name}
                        onChange={(e) => updateSkill(idx, { skill_name: e.target.value })}
                        placeholder="e.g. FastAPI / React"
                        className="w-full px-3 py-1.5 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                      />
                    </div>

                    {/* Category Code (12 codes + OTHER) */}
                    <div className="sm:col-span-3">
                      <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                        Category Code
                      </label>
                      <select
                        value={skill.category_code}
                        onChange={(e) => updateSkill(idx, { category_code: e.target.value as CategoryCode })}
                        className="w-full px-2.5 py-1.5 text-xs font-medium rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                      >
                        {CATEGORY_CODES.map((cat) => (
                          <option key={cat.code} value={cat.code}>
                            {cat.code} - {cat.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Confidence */}
                    <div className="sm:col-span-2">
                      <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                        Confidence
                      </label>
                      <select
                        value={skill.confidence || 'medium'}
                        onChange={(e) => updateSkill(idx, { confidence: e.target.value as Confidence })}
                        className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                      >
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                      </select>
                    </div>

                    {/* Level Estimate (1-10) */}
                    <div className="sm:col-span-2">
                      <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                        Level (1-10)
                      </label>
                      <input
                        type="number"
                        min={1}
                        max={10}
                        value={skill.level_estimate || 5}
                        onChange={(e) => updateSkill(idx, { level_estimate: Number(e.target.value) })}
                        className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                      />
                    </div>

                    {/* Remove Action */}
                    <div className="sm:col-span-1 flex justify-end pt-5">
                      <button
                        type="button"
                        onClick={() => removeSkill(idx)}
                        className="p-1.5 text-slate-400 hover:text-rose-500 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950 transition-colors"
                        title="Remove skill"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    {/* Evidence Quote / Context */}
                    <div className="sm:col-span-12 mt-1">
                      <input
                        type="text"
                        value={skill.evidence || ''}
                        onChange={(e) => updateSkill(idx, { evidence: e.target.value })}
                        placeholder="Evidence quote or justification (e.g. 'Built microservices and handled database migrations')"
                        className="w-full px-3 py-1 text-xs rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-400 italic"
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* SECTION 3: Experience, Hackathons & Certifications */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Internships & Experience */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-brand-600" />
              Work & Internships ({internships.length})
            </h3>
            <button
              type="button"
              onClick={() => setInternships([...internships, { company: '', role: '', duration: '' }])}
              className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Add
            </button>
          </div>

          <div className="space-y-3">
            {internships.map((item, idx) => (
              <div key={idx} className="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-700 text-xs space-y-2">
                <div className="flex justify-between items-center">
                  <input
                    type="text"
                    value={item.company}
                    onChange={(e) => {
                      const updated = [...internships];
                      updated[idx].company = e.target.value;
                      setInternships(updated);
                    }}
                    placeholder="Company name"
                    className="font-semibold text-slate-900 dark:text-white bg-transparent border-b border-transparent hover:border-slate-300 focus:outline-none"
                  />
                  <button
                    onClick={() => setInternships(internships.filter((_, i) => i !== idx))}
                    className="text-slate-400 hover:text-rose-500"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="text"
                    value={item.role}
                    onChange={(e) => {
                      const updated = [...internships];
                      updated[idx].role = e.target.value;
                      setInternships(updated);
                    }}
                    placeholder="Role title"
                    className="px-2 py-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-md"
                  />
                  <input
                    type="text"
                    value={item.duration || ''}
                    onChange={(e) => {
                      const updated = [...internships];
                      updated[idx].duration = e.target.value;
                      setInternships(updated);
                    }}
                    placeholder="Duration (e.g. 6 mos)"
                    className="px-2 py-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-md"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Hackathons & Projects */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Trophy className="w-4 h-4 text-amber-500" />
              Hackathons & Projects ({hackathons.length})
            </h3>
            <button
              type="button"
              onClick={() => setHackathons([...hackathons, { name: '', project: '', year: '2024' }])}
              className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Add
            </button>
          </div>

          <div className="space-y-3">
            {hackathons.map((item, idx) => (
              <div key={idx} className="p-3 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-700 text-xs space-y-2">
                <div className="flex justify-between items-center">
                  <input
                    type="text"
                    value={item.name}
                    onChange={(e) => {
                      const updated = [...hackathons];
                      updated[idx].name = e.target.value;
                      setHackathons(updated);
                    }}
                    placeholder="Hackathon or Project Name"
                    className="font-semibold text-slate-900 dark:text-white bg-transparent border-b border-transparent hover:border-slate-300 focus:outline-none"
                  />
                  <button
                    onClick={() => setHackathons(hackathons.filter((_, i) => i !== idx))}
                    className="text-slate-400 hover:text-rose-500"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
                <input
                  type="text"
                  value={item.project || ''}
                  onChange={(e) => {
                    const updated = [...hackathons];
                    updated[idx].project = e.target.value;
                    setHackathons(updated);
                  }}
                  placeholder="Key deliverables / technologies used"
                  className="w-full px-2 py-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-md"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Certifications List */}
        <div className="md:col-span-2 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Award className="w-4 h-4 text-purple-500" />
              Certifications & Badges ({certifications.length})
            </h3>
            <button
              type="button"
              onClick={() => setCertifications([...certifications, ''])}
              className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Add Certification
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {certifications.map((cert, idx) => (
              <div key={idx} className="flex items-center gap-2 p-2 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-700">
                <input
                  type="text"
                  value={cert}
                  onChange={(e) => {
                    const updated = [...certifications];
                    updated[idx] = e.target.value;
                    setCertifications(updated);
                  }}
                  placeholder="e.g. AWS Solutions Architect"
                  className="flex-1 text-xs px-2 py-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-md"
                />
                <button
                  onClick={() => setCertifications(certifications.filter((_, i) => i !== idx))}
                  className="text-slate-400 hover:text-rose-500 p-1"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Navigation Footer */}
      <div className="flex justify-between items-center pt-4 border-t border-slate-200 dark:border-slate-800">
        <button
          onClick={() => setCurrentStep(2)}
          className="text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
        >
          ← Back to Resume
        </button>

        <button
          onClick={() => {
            handleSave();
            setCurrentStep(4);
          }}
          className="flex items-center gap-2 px-6 py-2.5 text-sm font-semibold text-white bg-slate-900 dark:bg-white dark:text-slate-900 rounded-xl hover:opacity-90 transition-all shadow-md"
        >
          Proceed to Talent Check
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Modal: Load Existing Profile */}
      {showLoadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Load Stored Profile</h3>
              <button
                onClick={() => setShowLoadModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                ✕
              </button>
            </div>

            {/* Load by ID */}
            <div className="flex gap-2">
              <input
                type="text"
                value={loadProfileInput}
                onChange={(e) => setLoadProfileInput(e.target.value)}
                placeholder="Enter Profile ID..."
                className="flex-1 px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
              />
              <button
                onClick={handleLoadById}
                className="px-4 py-2 text-xs font-semibold bg-brand-600 text-white rounded-xl hover:bg-brand-500"
              >
                Fetch
              </button>
            </div>

            <div className="border-t border-slate-200 dark:border-slate-800 pt-3">
              <p className="text-xs font-semibold text-slate-500 mb-2">Available Profiles in Database:</p>
              {availableProfiles.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No stored profiles found yet.</p>
              ) : (
                <div className="max-h-60 overflow-y-auto space-y-2 pr-1">
                  {availableProfiles.map((p, i) => (
                    <button
                      key={p.profile_id || i}
                      onClick={() => handleSelectProfileToLoad(p)}
                      className="w-full text-left p-3 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-all text-xs"
                    >
                      <div className="font-semibold text-slate-900 dark:text-white">
                        {p.name || 'Unnamed Candidate'}
                      </div>
                      <div className="text-slate-500">{p.email || 'No email'}</div>
                      <div className="text-[10px] text-slate-400 font-mono mt-0.5">ID: {p.profile_id}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
