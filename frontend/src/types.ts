export type CategoryCode =
  | 'COD'
  | 'DSA'
  | 'OOD'
  | 'APTI'
  | 'COMM'
  | 'AI'
  | 'CLOUD'
  | 'SQL'
  | 'SWE'
  | 'SYSD'
  | 'NETW'
  | 'OS'
  | 'OTHER';

export const CATEGORY_CODES: { code: CategoryCode; label: string }[] = [
  { code: 'COD', label: 'Coding / Languages' },
  { code: 'DSA', label: 'Data Structures & Algorithms' },
  { code: 'OOD', label: 'Object-Oriented Design' },
  { code: 'APTI', label: 'Aptitude & Logic' },
  { code: 'COMM', label: 'Communication' },
  { code: 'AI', label: 'AI & Machine Learning' },
  { code: 'CLOUD', label: 'Cloud & DevOps' },
  { code: 'SQL', label: 'Databases & SQL' },
  { code: 'SWE', label: 'Software Engineering' },
  { code: 'SYSD', label: 'System Design' },
  { code: 'NETW', label: 'Networking' },
  { code: 'OS', label: 'Operating Systems' },
  { code: 'OTHER', label: 'Other Skills' },
];

export type Confidence = 'high' | 'medium' | 'low';

export interface Skill {
  skill_name: string;
  category_code: CategoryCode;
  evidence?: string;
  confidence?: Confidence;
  importance?: 'must_have' | 'nice_to_have' | null;
  level_estimate?: number | null; // 1-10
  source_section?: string | null;
  verified_by?: string[];
  stuffing_flag?: boolean;
  models_agree?: boolean | null;
}

export interface ExtractionResult {
  schema_version?: string;
  source_type: 'jd' | 'resume';
  source_file: string;
  company?: string;
  role?: string;
  skills: Skill[];
  extras?: {
    education?: string;
    projects?: any[];
    experience?: any[];
    certifications?: string[];
    [key: string]: any;
  };
}

export interface Profile {
  schema_version?: string;
  profile_id?: string | null;
  name: string;
  email: string;
  education?: string;
  github_url?: string;
  skills: Skill[];
  hackathons: { name: string; project?: string; year?: string; award?: string; [key: string]: any }[];
  internships: { company: string; role: string; duration?: string; description?: string; [key: string]: any }[];
  certifications: string[];
  preferred_roles: string[];
  cv_file?: string;
}

export interface SkillsetGap {
  category_code: CategoryCode;
  required_level: number; // 1-10
  candidate_level: number; // 1-10
  gap: boolean;
  contribution?: number;
}

export interface TalentCheckResult {
  company: string;
  skillset_gap: SkillsetGap[];
  readiness_score: number; // 0-100
  label?: string; // Ready / Almost there / Not yet
  weeks_to_ready_estimate?: number | null;
  score_delta?: number;
}

export interface MatchedSkill {
  jd_skill: string;
  profile_skill: string;
  match_type: 'exact' | 'alias' | 'semantic';
  similarity?: number;
}

export interface MissingSkill {
  skill_name: string;
  category_code: CategoryCode;
  importance?: string;
  score_impact?: number;
  learn_order?: number;
  prerequisites?: string[];
}

export interface MatchResult {
  jd_source_file: string;
  match_score: number; // 0-100
  matched_skills: MatchedSkill[];
  missing_skills: MissingSkill[];
}

export interface SampleJd {
  id: string;
  title: string;
  company: string;
  filename: string;
  snippet?: string;
}

export interface SampleResume {
  id: string;
  candidate_name: string;
  filename: string;
  role?: string;
}

export interface CompanyInfo {
  id: string;
  name: string;
  domain?: string;
  required_skills?: string[];
}

export interface MatchMatrix {
  roles: string[];
  companies: string[];
  grid: number[][]; // 4 x 6 score grid
}

export interface CandidateMeta {
  id: string;
  name: string;
}

export interface JDMeta {
  id: string;
  company: string;
  role: string;
  source_file: string;
}

export interface MatrixResponse {
  resumes: CandidateMeta[];
  jds: JDMeta[];
  matrix: number[][];
}
