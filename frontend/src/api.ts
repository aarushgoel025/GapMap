import type {
  Profile,
  ExtractionResult,
  TalentCheckResult,
  MatchResult,
  SampleJd,
  SampleResume,
  CompanyInfo,
  MatchMatrix,
  Skill,
} from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
 * GET /jds - List sample Job Descriptions
 */
export async function getJds(): Promise<SampleJd[]> {
  try {
    const res = await fetch(`${API_BASE}/api/jd/jds`);
    return await handleResponse<SampleJd[]>(res);
  } catch {
    // Fallback sample JDs
    return [
      {
        id: 'jd-1',
        title: 'Full Stack Engineer (AI Platform)',
        company: 'Stripe',
        filename: 'stripe_fullstack_ai.pdf',
        snippet: 'Seeking experienced TypeScript, Python, and Cloud engineers to build intelligent payment workflows.',
      },
      {
        id: 'jd-2',
        title: 'Backend Systems Developer',
        company: 'Datadog',
        filename: 'datadog_backend_systems.pdf',
        snippet: 'Requires strong DSA, System Design, SQL, and Go/Python expertise for high-throughput distributed tracing.',
      },
      {
        id: 'jd-3',
        title: 'Machine Learning Infrastructure Engineer',
        company: 'OpenAI',
        filename: 'openai_ml_infra.pdf',
        snippet: 'Focus on LLM serving, GPU cluster orchestration, Docker, Kubernetes, and Python model pipelines.',
      },
    ];
  }
}

/**
 * POST /jd/analyze - Analyze JD and extract structured skills & requirements
 */
export async function analyzeJd(jdIdOrText: string): Promise<ExtractionResult> {
  try {
    const res = await fetch(`${API_BASE}/api/jd/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jd_input: jdIdOrText }),
    });
    return await handleResponse<ExtractionResult>(res);
  } catch {
    return {
      schema_version: '1.0',
      source_type: 'jd',
      source_file: jdIdOrText.endsWith('.pdf') ? jdIdOrText : 'sample_jd.pdf',
      company: 'Stripe',
      role: 'Full Stack Engineer (AI Platform)',
      skills: [
        { skill_name: 'Python', category_code: 'COD', confidence: 'high', importance: 'must_have', level_estimate: 8 },
        { skill_name: 'TypeScript', category_code: 'COD', confidence: 'high', importance: 'must_have', level_estimate: 7 },
        { skill_name: 'System Design', category_code: 'SYSD', confidence: 'medium', importance: 'must_have', level_estimate: 8 },
        { skill_name: 'PostgreSQL', category_code: 'SQL', confidence: 'high', importance: 'must_have', level_estimate: 7 },
        { skill_name: 'Docker', category_code: 'CLOUD', confidence: 'medium', importance: 'nice_to_have', level_estimate: 6 },
        { skill_name: 'Data Structures', category_code: 'DSA', confidence: 'high', importance: 'must_have', level_estimate: 8 },
      ],
      extras: {},
    };
  }
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
export async function verifyGithub(githubUrl: string, skills: Skill[]): Promise<{ verified_skills: Skill[] }> {
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
  profile: Profile;
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
 * POST /match - Compute skill match between JD and candidate profile
 */
export async function matchSkills(payload: { jd_id?: string; profile_id?: string; profile?: Profile }): Promise<MatchResult> {
  try {
    const res = await fetch(`${API_BASE}/api/skill-matching/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return await handleResponse<MatchResult>(res);
  } catch {
    return {
      jd_source_file: 'stripe_fullstack_ai.pdf',
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
 * GET /match/matrix - Retrieve 4x6 comparative score grid
 */
export async function getMatchMatrix(): Promise<MatchMatrix> {
  try {
    const res = await fetch(`${API_BASE}/api/skill-matching/matrix`);
    return await handleResponse<MatchMatrix>(res);
  } catch {
    return {
      companies: ['Stripe', 'Google', 'OpenAI', 'Datadog'],
      roles: ['Backend SWE', 'Frontend SWE', 'Full Stack', 'DevOps / Cloud', 'AI Engineer', 'Systems Architect'],
      grid: [
        [88, 92, 95, 74, 85, 78], // Stripe
        [84, 80, 86, 79, 90, 82], // Google
        [91, 76, 88, 83, 97, 85], // OpenAI
        [89, 72, 84, 91, 80, 92], // Datadog
      ],
    };
  }
}
