import type {
  Profile,
  ExtractionResult,
  TalentCheckResult,
  MatchResult,
  SampleJd,
  SampleResume,
  CompanyInfo,
  MatchMatrix,
  MatrixResponse,
  Skill,
} from './types';

export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function handleResponse<T>(res: Response, fallback?: T): Promise<T> {
  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const errJson = await res.json();
      if (errJson && errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch {
      // ignore json parse error
    }
    if (fallback !== undefined) {
      console.warn(`[API] Call failed (${errorDetail}), using mock fallback.`);
      return fallback;
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

// ============================================================================
// 1. JD Analytics (Samiksha)
// ============================================================================

/**
 * GET /api/jd/jds or /api/jds - List sample Job Descriptions
 */
export async function getJds(): Promise<SampleJd[]> {
  try {
    const res = await fetch(`${API_BASE}/api/jd/jds`);
    const data = await handleResponse<any>(res);
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.files)) {
      return data.files.map((f: any, idx: number) => ({
        id: `jd-${idx + 1}`,
        title: f.title || f.filename.replace(/\.(pdf|docx)$/i, ''),
        company: f.company || (f.filename.includes(' - ') ? f.filename.split(' - ')[0] : 'Target Company'),
        filename: f.filename,
        snippet: f.snippet || `Benchmark Job Description for ${f.filename}`,
      }));
    }
    return data;
  } catch {
    // Fallback sample JDs matching Samiksha's real benchmark dataset
    return [
      {
        id: 'jd-1',
        title: 'Software Engineer',
        company: 'Google LLC',
        filename: 'Google LLC - Software Engineer.pdf',
        snippet: 'Google LLC Software Engineer requiring C++, Java, Python, Go, and Distributed Systems.',
      },
      {
        id: 'jd-2',
        title: 'Data Scientist',
        company: 'Google LLC',
        filename: 'Google LLC - Data Scientist.pdf',
        snippet: 'Google LLC Data Scientist requiring SQL, Machine Learning, A/B Testing, and Python.',
      },
      {
        id: 'jd-3',
        title: 'Software Engineer',
        company: 'Microsoft Corporation',
        filename: 'Microsoft - Software Engineer.pdf',
        snippet: 'Microsoft Software Engineer role emphasizing Cloud, C#, TypeScript, and Algorithms.',
      },
      {
        id: 'jd-4',
        title: 'Data Analyst',
        company: 'Microsoft Corporation',
        filename: 'Microsoft - Data Analyst.pdf',
        snippet: 'Microsoft Data Analyst role focusing on Power BI, SQL, Data Modeling, and Statistics.',
      },
      {
        id: 'jd-5',
        title: 'Associate Software Engineer',
        company: 'Oracle Financial Services Software Limited',
        filename: 'Oracle - Associate Software Engineer.pdf',
        snippet: 'Oracle Associate Software Engineer role covering Java, SQL, OOP, and Spring.',
      },
      {
        id: 'jd-6',
        title: 'Application Support Analyst',
        company: 'Oracle Financial Services Software Limited',
        filename: 'Oracle - Application Support Analyst.pdf',
        snippet: 'Oracle Application Support Analyst role focusing on Unix, SQL, Troubleshooting, and ITIL.',
      },
    ];
  }
}

/**
 * POST /api/jd/analyze - Analyze JD and extract structured skills & requirements
 */
export async function analyzeJd(jdIdOrText: string): Promise<ExtractionResult> {
  try {
    const formData = new FormData();
    if (jdIdOrText.endsWith('.pdf') || jdIdOrText.endsWith('.docx')) {
      formData.append('sample', jdIdOrText);
    } else {
      formData.append('text', jdIdOrText);
    }
    const res = await fetch(`${API_BASE}/api/jd/analyze`, {
      method: 'POST',
      body: formData,
    });
    return await handleResponse<ExtractionResult>(res);
  } catch {
    return {
      schema_version: '1.0',
      source_type: 'jd',
      source_file: jdIdOrText.endsWith('.pdf') || jdIdOrText.endsWith('.docx') ? jdIdOrText : 'sample_jd.pdf',
      company: 'Google LLC',
      role: 'Software Engineer',
      skills: [
        { skill_name: 'Python', category_code: 'COD', confidence: 'high', importance: 'must_have', level_estimate: 8 },
        { skill_name: 'Distributed Systems', category_code: 'SYSD', confidence: 'high', importance: 'must_have', level_estimate: 8 },
        { skill_name: 'Algorithms', category_code: 'DSA', confidence: 'high', importance: 'must_have', level_estimate: 8 },
        { skill_name: 'SQL', category_code: 'SQL', confidence: 'high', importance: 'must_have', level_estimate: 7 },
        { skill_name: 'Cloud Infrastructure', category_code: 'CLOUD', confidence: 'medium', importance: 'nice_to_have', level_estimate: 7 },
        { skill_name: 'Clean Code & OOP', category_code: 'OOD', confidence: 'high', importance: 'must_have', level_estimate: 8 },
      ],
      extras: {},
    };
  }
}

/**
 * POST /api/jd/analyze - Upload and analyze a custom .pdf or .docx Job Description
 */
export async function uploadJdFile(file: File): Promise<ExtractionResult> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/jd/analyze`, {
    method: 'POST',
    body: formData,
  });
  return await handleResponse<ExtractionResult>(res);
}

// ============================================================================
// 2. Resume Parsing (Arushi)
// ============================================================================

/**
 * GET /resumes - List sample resumes
 */
export async function getResumes(): Promise<SampleResume[]> {
  try {
    const res = await fetch(`${API_BASE}/api/resume/resumes`);
    return await handleResponse<SampleResume[]>(res);
  } catch {
    return [
      {
        id: 'res-1',
        candidate_name: 'Aarush Sharma',
        filename: 'aarush_sharma_cv.pdf',
        role: 'Full Stack & AI Engineer',
      },
      {
        id: 'res-2',
        candidate_name: 'Priya Patel',
        filename: 'priya_patel_resume.pdf',
        role: 'Backend Distributed Systems Specialist',
      },
      {
        id: 'res-3',
        candidate_name: 'Devin Vance',
        filename: 'devin_vance_cv.pdf',
        role: 'Cloud Architect & DevOps Lead',
      },
    ];
  }
}

/**
 * POST /resume/parse - Upload real PDF or DOCX file to parse
 */
export async function uploadResumeFile(file: File): Promise<ExtractionResult> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/api/resume/parse`, {
    method: 'POST',
    body: formData,
  });
  return await handleResponse<ExtractionResult>(res);
}

/**
 * POST /resume/parse - Parse resume document into structured extraction result
 */
export async function parseResume(resumeIdOrFile: string): Promise<ExtractionResult> {
  try {
    const res = await fetch(`${API_BASE}/api/resume/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_source: resumeIdOrFile }),
    });
    return await handleResponse<ExtractionResult>(res);
  } catch {
    return {
      schema_version: '1.0',
      source_type: 'resume',
      source_file: resumeIdOrFile.includes('.pdf') ? resumeIdOrFile : 'candidate_resume.pdf',
      company: '',
      role: 'Full Stack & AI Developer',
      skills: [
        {
          skill_name: 'Python',
          category_code: 'COD',
          evidence: 'Developed production REST APIs with FastAPI and Mistral AI',
          confidence: 'high',
          level_estimate: 8,
          source_section: 'skills',
          verified_by: ['resume', 'github'],
          stuffing_flag: false,
          models_agree: true,
        },
        {
          skill_name: 'React',
          category_code: 'COD',
          evidence: 'Built modern reactive frontend web applications with Vite and Tailwind',
          confidence: 'high',
          level_estimate: 8,
          source_section: 'skills',
          verified_by: ['resume'],
          stuffing_flag: false,
        },
        {
          skill_name: 'PostgreSQL',
          category_code: 'SQL',
          evidence: 'Designed relational schemas and queries in Supabase',
          confidence: 'medium',
          level_estimate: 7,
          source_section: 'experience',
          verified_by: ['resume'],
        },
        {
          skill_name: 'Docker',
          category_code: 'CLOUD',
          evidence: 'Containerized microservices and automated deployment CI/CD',
          confidence: 'medium',
          level_estimate: 6,
          source_section: 'projects',
          verified_by: ['github'],
        },
        {
          skill_name: 'Keyword Stuffer Skill',
          category_code: 'OTHER',
          evidence: 'Listed 45 times in footers without code evidence',
          confidence: 'low',
          level_estimate: 2,
          source_section: 'skills',
          stuffing_flag: true,
        },
      ],
      extras: {
        education: 'B.Tech in Computer Science & Engineering, Top Tier University (2021-2025)',
        projects: [
          { name: 'GapMap ATS Platform', description: 'Real-time skill mismatch and talent readiness engine' },
          { name: 'AI Tutor Agent', description: 'Autonomous agent powered by open-mistral-nemo' },
        ],
        experience: [
          { company: 'Tech Innovators Inc.', role: 'Software Engineering Intern', duration: '6 months' },
        ],
        certifications: [
          'AWS Certified Developer - Associate',
          'DeepLearning.AI Generative AI for Everyone',
        ],
      },
    };
  }
}

/**
 * POST /resume/verify-github - Verify extracted skills against GitHub repositories
 */
export interface GitHubVerificationResponse {
  verified_skills: Skill[];
  github_user?: string;
  name?: string;
  avatar_url?: string;
  bio?: string;
  public_repos?: number;
  top_languages?: string[];
  repos?: Array<{
    name: string;
    language: string;
    topics: string[];
    description: string;
    stars: number;
    html_url: string;
  }>;
  verified_count?: number;
}

export async function verifyGithub(githubUrl: string, skills: Skill[]): Promise<GitHubVerificationResponse> {
  try {
    const res = await fetch(`${API_BASE}/api/resume/verify-github`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ github_url: githubUrl, skills }),
    });
    return await handleResponse(res);
  } catch {
    const verified = skills.map((s) => ({
      ...s,
      verified_by: s.verified_by?.includes('github')
        ? s.verified_by
        : [...(s.verified_by || []), 'github'],
    }));
    return { verified_skills: verified };
  }
}

// ============================================================================
// 3. Profile Management (Aarush - Your Module)
// ============================================================================

/**
 * POST /profile - Create candidate profile
 */
export async function createProfile(profile: Profile): Promise<Profile> {
  const res = await fetch(`${API_BASE}/api/profile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
  });
  return handleResponse<Profile>(res);
}

/**
 * GET /profile/{id} - Retrieve candidate profile by ID
 */
export async function getProfile(id: string): Promise<Profile> {
  const res = await fetch(`${API_BASE}/api/profile/${id}`);
  return handleResponse<Profile>(res);
}

/**
 * PUT /profile/{id} - Update candidate profile by ID
 */
export async function updateProfile(id: string, profile: Profile): Promise<Profile> {
  const res = await fetch(`${API_BASE}/api/profile/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
  });
  return handleResponse<Profile>(res);
}

/**
 * GET /profile - List all candidate profiles
 */
export async function listProfiles(): Promise<Profile[]> {
  const res = await fetch(`${API_BASE}/api/profile`);
  return handleResponse<Profile[]>(res);
}

// ============================================================================
// 4. Talent Check (Aditya)
// ============================================================================

/**
 * GET /companies - List companies with benchmarks
 */
export async function getCompanies(): Promise<CompanyInfo[]> {
  try {
    const res = await fetch(`${API_BASE}/api/talent-check/companies`);
    return await handleResponse<CompanyInfo[]>(res);
  } catch {
    return [
      { id: 'comp-1', name: 'Google', domain: 'Search & Cloud' },
      { id: 'comp-2', name: 'Stripe', domain: 'Fintech & Developer API' },
      { id: 'comp-3', name: 'Microsoft', domain: 'Enterprise Software' },
      { id: 'comp-4', name: 'Amazon', domain: 'Cloud & E-Commerce' },
    ];
  }
}

/**
 * POST /talent-check - Evaluate candidate profile against target company benchmarks
 */
export async function checkTalent(payload: { company: string; profile_id?: string; profile?: Profile }): Promise<TalentCheckResult> {
  try {
    const res = await fetch(`${API_BASE}/api/talent-check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return await handleResponse<TalentCheckResult>(res);
  } catch {
    return {
      company: payload.company || 'Stripe',
      readiness_score: 82.5,
      label: 'Almost there',
      weeks_to_ready_estimate: 3,
      skillset_gap: [
        { category_code: 'COD', required_level: 8, candidate_level: 8, gap: false, contribution: 30.0 },
        { category_code: 'DSA', required_level: 8, candidate_level: 7, gap: true, contribution: 20.0 },
        { category_code: 'SYSD', required_level: 8, candidate_level: 6, gap: true, contribution: 15.0 },
        { category_code: 'SQL', required_level: 7, candidate_level: 7, gap: false, contribution: 17.5 },
      ],
    };
  }
}

/**
 * POST /talent-check/whatif - Simulate readiness score impact if specific skills are acquired
 */
export async function checkTalentWhatIf(payload: {
  company: string;
  profile_id?: string;
  profile?: Profile;
  changes: { category_code: string; new_level: number }[];
}): Promise<TalentCheckResult> {
  try {
    const res = await fetch(`${API_BASE}/api/talent-check/whatif`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return await handleResponse<TalentCheckResult>(res);
  } catch {
    return {
      company: payload.company,
      readiness_score: 94.0,
      label: 'Ready',
      weeks_to_ready_estimate: 0,
      skillset_gap: [
        { category_code: 'COD', required_level: 8, candidate_level: 8, gap: false, contribution: 30.0 },
        { category_code: 'DSA', required_level: 8, candidate_level: 8, gap: false, contribution: 25.0 },
        { category_code: 'SYSD', required_level: 8, candidate_level: 8, gap: false, contribution: 21.5 },
        { category_code: 'SQL', required_level: 7, candidate_level: 7, gap: false, contribution: 17.5 },
      ],
    };
  }
}

// ============================================================================
// 5. Skill Matching (Anjali)
// ============================================================================

/**
 * Fetch available sample profiles and JDs for UI selector
 */
export async function fetchSamples(): Promise<{
  profiles: { id: string; name: string }[];
  jds: { id: string; company: string; role: string; source_file: string }[];
}> {
  try {
    const res = await fetch(`${API_BASE}/api/match/samples`);
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn('Using local fallback for samples', e);
  }

  return {
    profiles: [
      { id: 'candidate_1_all_rounder', name: 'Alex Chen (All-Rounder)' },
      { id: 'candidate_2_data_analyst', name: 'Priya Patel (Data & AI Analyst)' },
      { id: 'candidate_3_oracle_support', name: 'Rohan Verma (Support & Database Associate)' },
      { id: 'candidate_4_systems_engineer', name: 'Marcus Vance (Systems & Cloud Engineer)' },
    ],
    jds: [
      { id: 'google_cloud_architect', company: 'Google', role: 'Cloud Infrastructure Architect', source_file: 'google_cloud_architect.pdf' },
      { id: 'google_software_engineer', company: 'Google', role: 'Software Engineer, Core Systems', source_file: 'google_software_engineer.pdf' },
      { id: 'microsoft_data_engineer', company: 'Microsoft', role: 'Senior Data Platform Engineer', source_file: 'microsoft_data_engineer.pdf' },
      { id: 'microsoft_fullstack', company: 'Microsoft', role: 'Full Stack Cloud Developer', source_file: 'microsoft_fullstack.pdf' },
      { id: 'oracle_database_engineer', company: 'Oracle Financial Services Software', role: 'Database Infrastructure Engineer', source_file: 'oracle_database_engineer.pdf' },
      { id: 'oracle_java_engineer', company: 'Oracle Financial Services Software', role: 'Enterprise Java Application Developer', source_file: 'oracle_java_engineer.pdf' },
    ],
  };
}

/**
 * Match a candidate against a target JD by ID
 */
export async function matchCandidateWithJD(profileId: string, jdId: string): Promise<MatchResult> {
  const res = await fetch(`${API_BASE}/api/match`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile_id: profileId, jd_id: jdId }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to compute match' }));
    throw new Error(err.detail || 'Match error');
  }

  return await res.json();
}

/**
 * Retrieve 4x6 matrix heatmap response
 */
export async function fetchMatchMatrix(): Promise<MatrixResponse> {
  const res = await fetch(`${API_BASE}/api/match/matrix`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to load match matrix' }));
    throw new Error(err.detail || 'Matrix error');
  }
  return await res.json();
}

/**
 * POST /api/match - Flexible skill matching with profile or profile_id and jd_id
 */
export async function matchSkills(payload: {
  jd_id?: string;
  profile_id?: string;
  profile?: Profile;
  jd_skills?: Skill[];
  jd_source_file?: string;
}): Promise<MatchResult> {
  try {
    const res = await fetch(`${API_BASE}/api/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return await handleResponse<MatchResult>(res);
  } catch {
    return {
      jd_source_file: payload.jd_source_file || 'google_software_engineer.pdf',
      match_score: 87.5,
      matched_skills: [
        { jd_skill: 'Python', profile_skill: 'Python', match_type: 'exact', similarity: 1.0 },
        { jd_skill: 'TypeScript', profile_skill: 'React / Frontend', match_type: 'semantic', similarity: 0.88 },
        { jd_skill: 'PostgreSQL', profile_skill: 'PostgreSQL', match_type: 'exact', similarity: 1.0 },
        { jd_skill: 'Docker', profile_skill: 'Docker', match_type: 'exact', similarity: 1.0 },
      ],
      missing_skills: [
        {
          skill_name: 'Advanced Distributed System Design',
          category_code: 'SYSD',
          importance: 'must_have',
          score_impact: 12.5,
          learn_order: 1,
          prerequisites: ['System Design Basics', 'Caching & Sharding'],
        },
      ],
    };
  }
}

/**
 * GET /api/match/matrix - Retrieve 4x6 comparative score grid
 */
export async function getMatchMatrix(): Promise<MatchMatrix> {
  try {
    const res = await fetch(`${API_BASE}/api/match/matrix`);
    const data: MatrixResponse = await handleResponse<MatrixResponse>(res);
    return {
      companies: data.jds.map((j) => j.company),
      roles: data.jds.map((j) => j.role),
      grid: data.matrix,
    };
  } catch {
    return {
      companies: ['Stripe', 'Google', 'OpenAI', 'Datadog'],
      roles: ['Backend SWE', 'Frontend SWE', 'Full Stack', 'DevOps / Cloud', 'AI Engineer', 'Systems Architect'],
      grid: [
        [88, 92, 95, 74, 85, 78],
        [84, 80, 86, 79, 90, 82],
        [91, 76, 88, 83, 97, 85],
        [89, 72, 84, 91, 80, 92],
      ],
    };
  }
}

