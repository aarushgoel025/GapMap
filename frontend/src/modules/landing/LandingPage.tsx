import React from 'react';
import {
  Compass,
  ArrowRight,
  CheckCircle2,
  Layers,
  Cpu,
  Database,
  Server,
  Sparkles,
  FileText,
  Lock,
  Activity,
  Code,
  Sliders,
  Zap,
  BarChart3,
  Terminal,
  FileCheck,
  Search,
  ShieldCheck,
} from 'lucide-react';

interface LandingPageProps {
  onStartPipeline: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onStartPipeline }) => {
  const TALENCIA_SYSTEMS = [
    {
      number: '01',
      title: 'Parameter Discovery',
      badge: 'Taxonomy Standardization',
      icon: Layers,
      color: 'from-blue-500 to-cyan-500',
      description:
        'Eliminates ambiguous job titles and fragmented naming conventions by establishing a standardized 12-domain technical competency taxonomy.',
      implementation:
        'Enforced strictly in backend schemas (COD, DSA, OOD, APTI, COMM, AI, CLOUD, SQL, SWE, SYSD, NETW, OS) and mapped across 117+ corporate hiring bars in talent_check_company_skillsets.json.',
      benefit: 'Zero ambiguity between JD demands and resume skills across any industry tier.',
    },
    {
      number: '02',
      title: 'Database Normalization',
      badge: '3NF Relational Architecture',
      icon: Database,
      color: 'from-indigo-500 to-purple-500',
      description:
        'Structured, third-normal-form relational data persistence designed for enterprise scalability and instant candidate retrieval.',
      implementation:
        'Implemented via Supabase PostgreSQL schema with automatic zero-configuration JSON fallback in backend/data/ (profiles, jds, runs, audit_log) for bulletproof offline execution.',
      benefit: 'High availability with seamless local failover for hackathon live demos.',
    },
    {
      number: '03',
      title: 'Test Automation',
      badge: '135 Passing Test Cases',
      icon: Terminal,
      color: 'from-emerald-500 to-teal-500',
      description:
        'Rigorous automated test coverage guaranteeing contract adherence, deterministic scoring, and regression-free pipelines.',
      implementation:
        'Full pytest test suite (135 tests passing in ~7s) testing multi-LLM merge logic, SHA-256 caching, PII masking, keyword stuffing edge cases, and 4×6 heatmap matrix variance.',
      benefit: '100% verified math with reproducible outputs across all sample permutations.',
    },
    {
      number: '04',
      title: 'Agentic Research',
      badge: 'Dual-LLM Parallel Engine',
      icon: Zap,
      color: 'from-amber-500 to-orange-500',
      description:
        'Cross-verifies extracted competencies using multi-agent consensus to eliminate hallucinations and single-model bias.',
      implementation:
        'Dispatches parallel prompts to Google Gemini and Mistral AI via ThreadPoolExecutor. Disagreements and category disputes are audited in extras.disagreements with automatic confidence lowering.',
      benefit: 'High-precision skill extraction with transparent multi-model agreement flags.',
    },
    {
      number: '05',
      title: 'Agentic Ecosystem',
      badge: 'Self-Correcting Schemas',
      icon: Activity,
      color: 'from-pink-500 to-rose-500',
      description:
        'Resilient LLM-to-backend interface enforcing strict Pydantic data contracts with self-healing feedback loops.',
      implementation:
        'Pydantic v2 schemas validate all model outputs; on validation failure, a self-correcting retry loop (up to 3 attempts) feeds validation error traces back to the model for automated prompt correction.',
      benefit: 'Never fails on malformed LLM responses; guarantees clean structured JSON.',
    },
    {
      number: '06',
      title: 'DevOps & Cloud Architecture',
      badge: 'Containerized CI/CD',
      icon: Server,
      color: 'from-sky-500 to-blue-600',
      description:
        'Production-ready containerization and automated verification pipelines for predictable deployment anywhere.',
      implementation:
        'Multi-stage backend Dockerfile (Python 3.11/3.14), frontend Vite Dockerfile, docker-compose orchestration, and GitHub Actions CI workflow executing pytest on every commit.',
      benefit: 'Zero "works on my machine" issues; portable and production-deployable.',
    },
    {
      number: '07',
      title: 'Vector Databases & ML',
      badge: 'Deterministic Semantic Match',
      icon: Cpu,
      color: 'from-violet-500 to-indigo-600',
      description:
        'Three-layer matching engine (Exact → Alias → Semantic) with localized vector embeddings for true synonym detection.',
      implementation:
        'Local precomputed 256-dim embedding index with cosine similarity calculation and circuit-breaker fallback. Tuned semantic threshold and aliases.json for tech synonyms like Networking ↔ Computer Networks.',
      benefit: 'Fair candidate scoring without costly external embedding API calls or latency.',
    },
    {
      number: '08',
      title: 'Enterprise Architecture & Governance',
      badge: 'Privacy & Audit Governance',
      icon: Lock,
      color: 'from-red-500 to-rose-600',
      description:
        'Enterprise-grade candidate privacy protection, anti-cheat detection, and immutable auditable tracking.',
      implementation:
        'Regex PII scrubber redacting phone/email/addresses prior to LLM submission, word-boundary keyword stuffing detection flagging unproven skills, opt-in GitHub API verification, and Section F audit trail.',
      benefit: 'Candidate data privacy compliance + rigorous prevention of resume spamming.',
    },
  ];

  const PIPELINE_STEPS = [
    {
      step: '1',
      title: 'JD Analytics',
      subtitle: 'Target Role Benchmark',
      desc: 'Dual Gemini + Mistral extraction, importance weighting (Must-Have = 2, Nice-to-Have = 1), and instant SHA-256 caching.',
      icon: FileText,
      tag: 'Dual LLM Consensus',
    },
    {
      step: '2',
      title: 'Resume Parsing',
      subtitle: 'Evidence & Anti-Stuffing',
      desc: 'Automated PII scrubbing, section splitting, keyword stuffing detection (flagging skills without experience), and optional GitHub repo audit.',
      icon: Search,
      tag: 'PII Redacted & Audited',
    },
    {
      step: '3',
      title: 'Profile Contract',
      subtitle: 'Structured Data Store',
      desc: 'Standardized profile schema stored in Supabase with zero-config JSON fallback and immutable Section F audit logging.',
      icon: FileCheck,
      tag: 'Unified Pydantic Contract',
    },
    {
      step: '4',
      title: 'Talent Readiness',
      subtitle: 'Corporate Hiring Bars',
      desc: 'Readiness evaluation against 117+ top tech hiring bars across 12 categories with a real-time What-If Simulator and placement timeline.',
      icon: Sliders,
      tag: 'What-If Simulation',
    },
    {
      step: '5',
      title: 'Skill Matching',
      subtitle: '3-Layer Gap Engine',
      desc: 'Exact (1.0) → Alias (0.9) → Semantic (0.8×Cos) matching, prerequisite-ordered learning plan, and a 4×6 candidate-role heatmap matrix.',
      icon: BarChart3,
      tag: 'Prerequisite Graph',
    },
  ];

  const FOUR_USPS = [
    {
      number: '01',
      pillar: 'Pillar 1',
      title: 'Proof-Backed Skills & Anti-Stuffing',
      subtitle: 'The Evidence Engine',
      badge: 'Verbatim Citations',
      icon: ShieldCheck,
      color: 'from-amber-500 to-orange-500',
      tagColor: 'bg-amber-950/80 text-amber-300 border-amber-800/80',
      demoLine: 'Do not just claim it. Prove it.',
      description:
        'Every skill comes with an exact quote snippet from the resume and a confidence level. We flag keyword stuffing—skills listed in a summary but never used in any real project or job—and slash their score impact by 50%.',
      highlights: [
        'Verbatim resume quote citations for every claimed competency',
        'Word-boundary regex (\\b) keyword stuffing detection with 50% penalty',
        'Optional GitHub API check verifying skills from real public code repositories',
      ],
      videoTime: 'Video: 4:00 – 6:30',
    },
    {
      number: '02',
      pillar: 'Pillar 2',
      title: 'What-If Simulator & Impact-Ranked Gaps',
      subtitle: 'Dynamic Career Planning',
      badge: '117+ Corporate Profiles',
      icon: Sliders,
      color: 'from-cyan-500 to-blue-500',
      tagColor: 'bg-cyan-950/80 text-cyan-300 border-cyan-800/80',
      demoLine: 'Interactive live slider deltas & prerequisite DAG',
      description:
        'Talent Check explains readiness scores with the contribution of each of the 12 skillsets. Interactive sliders let candidates try: "What if my SQL level was 6?" to see live score deltas and weeks-to-ready estimates.',
      highlights: [
        'Live score sliders updating candidate readiness against corporate hiring bars',
        'Topological prerequisite sorting (e.g. Learn Docker before Kubernetes)',
        'Score-impact ranking revealing which missing skill unlocks the most points',
      ],
      videoTime: 'Video: 9:00 – 11:30',
    },
    {
      number: '03',
      pillar: 'Pillar 3',
      title: 'Smarter 3-Layer Matching (SkillBridge-Style)',
      subtitle: 'Deterministic Scoring Math',
      badge: '100% Explainable',
      icon: Layers,
      color: 'from-purple-500 to-indigo-500',
      tagColor: 'bg-purple-950/80 text-purple-300 border-purple-800/80',
      demoLine: 'Exact (1.0) ➔ Alias (0.9) ➔ Semantic (0.8 × Cosine)',
      description:
        'Skill matching cascades across 3 deterministic tiers: exact name, alias/family (ReactJS = React, Postgres = SQL), and local embedding vector similarity. Every match explicitly states which layer found it, eliminating math hallucination.',
      highlights: [
        'Layer 1 Exact Match (1.0 weight credit)',
        'Layer 2 Curated Alias / Family Match (0.9 weight credit)',
        'Layer 3 Semantic Cosine Vector Similarity (0.8 × Cosine credit)',
      ],
      videoTime: 'Video: 11:30 – 14:00',
    },
    {
      number: '04',
      pillar: 'Pillar 4',
      title: 'Trustworthy AI Consensus Pipeline',
      subtitle: 'Multi-LLM Architecture',
      badge: 'Gemini 2.5 + Mistral',
      icon: Zap,
      color: 'from-emerald-500 to-teal-500',
      tagColor: 'bg-emerald-950/80 text-emerald-300 border-emerald-800/80',
      demoLine: 'Two LLMs read each document; consensus settles disagreements',
      description:
        'Two distinct models, Gemini 2.5 Flash and Mistral, analyze documents in parallel with a deterministic merge resolver. Every output is validated by Pydantic v2 with auto-retry, backed by 135 unit tests and full Section F audit logs.',
      highlights: [
        'Dual-LLM parallel consensus eliminating single-model hallucinations',
        'Pydantic v2 auto-correcting feedback retry loop on schema discrepancies',
        'SHA-256 caching for instant sub-second repeat runs & offline resilience',
      ],
      videoTime: 'Video: 1:30 – 4:00',
    },
  ];

  return (
    <div className="space-y-16 animate-fadeIn pb-16">
      {/* 1. Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-slate-900/90 via-slate-900/70 to-slate-950/90 border border-slate-800 p-8 sm:p-12 md:p-16 shadow-2xl backdrop-blur-xl">
        {/* Glow ambient background effects */}
        <div className="absolute top-0 right-1/4 -z-10 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/4 -z-10 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-4xl mx-auto text-center space-y-6">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-950/80 border border-brand-800/80 text-brand-300 text-xs font-bold tracking-wide shadow-xs">
            <Sparkles className="w-4 h-4 text-brand-400" />
            <span>RADIX TALENT MATCH HACKATHON • TALENCIA SYSTEMS ARCHITECTURE</span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tight text-white leading-tight">
            Evidence-Driven ATS & <br />
            <span className="bg-gradient-to-r from-brand-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
              Skill Gap Intelligence Engine
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Traditional ATS algorithms rely on naive keyword matching—rejecting qualified talent and rewarding resume buzzword stuffers. <strong className="text-white">GapMap</strong> verifies evidence-backed skills, benchmarks candidates against 117+ corporate hiring bars, and creates actionable learning pathways.
          </p>

          {/* Key Metric Highlights */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 max-w-3xl mx-auto text-left">
            <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="text-2xl font-black text-white">12</div>
              <div className="text-xs text-slate-400 font-medium">Standardized Categories</div>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="text-2xl font-black text-brand-400">117+</div>
              <div className="text-xs text-slate-400 font-medium">Company Hiring Bars</div>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="text-2xl font-black text-indigo-400">3-Layer</div>
              <div className="text-xs text-slate-400 font-medium">Matching (Exact/Alias/AI)</div>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="text-2xl font-black text-emerald-400">135/135</div>
              <div className="text-xs text-slate-400 font-medium">Pytest Tests Passing</div>
            </div>
          </div>

          {/* Main Call to Action Button */}
          <div className="pt-6 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={onStartPipeline}
              className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-gradient-to-r from-brand-600 via-brand-500 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-extrabold text-base transition-all duration-200 transform hover:scale-[1.02] shadow-glow flex items-center justify-center gap-3 cursor-pointer group"
            >
              <span>Launch Pipeline (Step 1: Upload JD)</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <a
              href="#our-usps"
              className="w-full sm:w-auto px-6 py-4 rounded-2xl bg-amber-950/40 hover:bg-amber-900/60 text-amber-300 font-bold text-sm border border-amber-800/60 transition-colors flex items-center justify-center gap-2 cursor-pointer"
            >
              <span>Explore 4 USPs</span>
              <Sparkles className="w-4 h-4 text-amber-400" />
            </a>
            <a
              href="#talencia-systems"
              className="w-full sm:w-auto px-6 py-4 rounded-2xl bg-slate-800/80 hover:bg-slate-800 text-slate-200 font-bold text-sm border border-slate-700 transition-colors flex items-center justify-center gap-2 cursor-pointer"
            >
              <span>The 8 Systems</span>
              <Layers className="w-4 h-4 text-slate-400" />
            </a>
          </div>
        </div>
      </section>

      {/* 2. Core 5-Stage Pipeline Overview */}
      <section className="space-y-6">
        <div className="text-center space-y-2">
          <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-950 text-indigo-300 border border-indigo-800/60 uppercase tracking-wider">
            End-to-End Pipeline
          </span>
          <h2 className="text-3xl font-black text-white tracking-tight">
            How GapMap Operates
          </h2>
          <p className="text-sm text-slate-400 max-w-xl mx-auto">
            From raw job postings to actionable candidate learning graphs in 5 cohesive stages.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {PIPELINE_STEPS.map((s, idx) => {
            const Icon = s.icon;
            return (
              <div
                key={idx}
                className="relative bg-slate-900/90 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between space-y-4 shadow-sm"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="w-7 h-7 rounded-lg bg-brand-950 border border-brand-800/80 text-brand-300 font-black text-xs flex items-center justify-center">
                      {s.step}
                    </span>
                    <Icon className="w-4 h-4 text-slate-400" />
                  </div>
                  <h3 className="text-base font-bold text-white">{s.title}</h3>
                  <div className="text-xs text-brand-400 font-semibold mb-2">{s.subtitle}</div>
                  <p className="text-xs text-slate-400 leading-relaxed">{s.desc}</p>
                </div>

                <div className="pt-2 border-t border-slate-800/60">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 inline-block">
                    {s.tag}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 3. The 4 USPs / Pillars: What Makes Us Different */}
      <section id="our-usps" className="space-y-8 scroll-mt-24">
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-bold bg-amber-950/80 text-amber-300 border border-amber-800/80 uppercase tracking-wider shadow-xs">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Our USP • What Makes Us Different</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            The 4 Pillars That Set GapMap Apart
          </h2>
          <p className="text-sm text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Most teams build: upload resume, get an ATS score, see missing keywords. Public projects already do that. We stand out with four foundational pillars engineered for truth, explainability, and actionable career advancement.
          </p>
        </div>

        {/* 4 USP Cards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {FOUR_USPS.map((usp) => {
            const Icon = usp.icon;
            return (
              <div
                key={usp.number}
                className="group relative bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-3xl p-6 sm:p-7 transition-all duration-300 flex flex-col justify-between space-y-5 shadow-xl hover:shadow-2xl backdrop-blur-sm overflow-hidden"
              >
                {/* Accent top gradient bar */}
                <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${usp.color}`} />

                <div className="space-y-4">
                  {/* Top Bar with Number, Pillar Badge & Tag */}
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <div className="flex items-center gap-2.5">
                      <div className={`w-8 h-8 rounded-xl bg-gradient-to-tr ${usp.color} text-white font-black text-xs flex items-center justify-center shadow-xs`}>
                        {usp.number}
                      </div>
                      <div className="flex flex-col">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                          {usp.pillar}
                        </span>
                        <span className="text-lg font-black text-white tracking-tight">
                          {usp.title}
                        </span>
                      </div>
                    </div>
                    <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full border ${usp.tagColor}`}>
                      {usp.badge}
                    </span>
                  </div>

                  {/* Demo Quote / Motto Line */}
                  <div className="px-3.5 py-2 rounded-xl bg-slate-950/70 border border-slate-800/80 flex items-center justify-between text-xs">
                    <span className="italic font-semibold text-slate-200">
                      "{usp.demoLine}"
                    </span>
                    <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                      {usp.videoTime}
                    </span>
                  </div>

                  {/* Core Description */}
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                    {usp.description}
                  </p>

                  {/* Highlight bullets */}
                  <div className="space-y-2 pt-1">
                    {usp.highlights.map((item, hIdx) => (
                      <div key={hIdx} className="flex items-start gap-2 text-xs text-slate-300">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Subtitle Footer */}
                <div className="pt-3 border-t border-slate-800/70 flex items-center justify-between text-xs text-slate-400">
                  <div className="flex items-center gap-1.5 font-medium text-slate-300">
                    <Icon className="w-4 h-4 text-brand-400" />
                    <span>{usp.subtitle}</span>
                  </div>
                  <span className="text-[10px] uppercase font-bold tracking-wider text-brand-400">
                    Active in Pipeline
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Standout Feature & Formula Callout Banner */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-brand-950/40 to-slate-900 border border-brand-800/50 p-5 sm:p-6 shadow-lg">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1.5 max-w-2xl">
              <div className="flex items-center gap-2 text-xs font-bold text-brand-400 uppercase tracking-wide">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Our Standout Feature</span>
              </div>
              <p className="text-sm font-semibold text-white leading-relaxed">
                "GapMap replaces black-box ATS keyword guessing with proof-backed evidence verification, an interactive 12-domain What-If corporate readiness simulator, and prerequisite-sorted learning pathways."
              </p>
            </div>

            {/* Formula Pill */}
            <div className="p-3.5 bg-slate-950/80 rounded-xl border border-slate-800 text-left min-w-[270px]">
              <div className="text-[11px] font-bold text-slate-300 mb-1 flex items-center gap-1.5">
                <BarChart3 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Deterministic Scoring Engine</span>
              </div>
              <div className="text-[11px] font-mono text-emerald-400">
                Score = Σ(w · c) / Σ(w) × 100
              </div>
              <div className="text-[10px] text-slate-400 mt-1">
                Must-Have: 2.0x • Nice-to-Have: 1.0x<br />
                Exact: 1.0 • Alias: 0.9 • AI: 0.8 × Cosine
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. The 8 Talencia Systems */}
      <section id="talencia-systems" className="space-y-8 scroll-mt-24">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-emerald-950 text-emerald-300 border border-emerald-800/60 uppercase tracking-wider">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Specification Compliance</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            The 8 Talencia Systems & How They Are Implemented
          </h2>
          <p className="text-sm text-slate-400 max-w-2xl mx-auto">
            Every architectural pointer mandated by the Talencia project document is actively integrated, tested, and operational in GapMap.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {TALENCIA_SYSTEMS.map((sys) => {
            const Icon = sys.icon;
            return (
              <div
                key={sys.number}
                className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-2xl p-6 transition-all duration-200 shadow-md flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  {/* Top Bar with Number & Badge */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white font-black text-xs flex items-center justify-center shadow-xs">
                        {sys.number}
                      </div>
                      <Icon className="w-4 h-4 text-brand-400" />
                      <span className="text-lg font-bold text-white tracking-tight">
                        {sys.title}
                      </span>
                    </div>
                    <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                      {sys.badge}
                    </span>
                  </div>

                  {/* Core Description */}
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {sys.description}
                  </p>

                  {/* Implementation Details */}
                  <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-1.5">
                    <div className="text-[11px] font-bold text-brand-400 flex items-center gap-1.5 uppercase tracking-wide">
                      <Code className="w-3.5 h-3.5" />
                      <span>Codebase Implementation:</span>
                    </div>
                    <p className="text-xs text-slate-400 leading-normal font-mono">
                      {sys.implementation}
                    </p>
                  </div>
                </div>

                {/* Practical Benefit */}
                <div className="pt-2 border-t border-slate-800 flex items-center gap-2 text-xs text-emerald-400 font-medium">
                  <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                  <span>{sys.benefit}</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 4. Bottom Launch CTA Banner */}
      <section className="bg-gradient-to-r from-brand-950/60 via-slate-900/90 to-indigo-950/60 border border-brand-800/40 rounded-3xl p-8 sm:p-12 text-center space-y-6 shadow-xl backdrop-blur-md">
        <div className="max-w-2xl mx-auto space-y-3">
          <div className="w-12 h-12 mx-auto rounded-2xl bg-brand-600/20 border border-brand-500/40 flex items-center justify-center text-brand-400">
            <Compass className="w-6 h-6 animate-spin-slow" />
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Ready to Run the GapMap Pipeline?
          </h2>
          <p className="text-sm text-slate-300">
            Start by uploading any benchmark or custom Job Description to extract competencies, parse candidate resumes with privacy scrubbing, test corporate readiness, and view the 3-layer matching breakdown.
          </p>
        </div>

        <div>
          <button
            onClick={onStartPipeline}
            className="px-8 py-4 rounded-2xl bg-brand-600 hover:bg-brand-500 text-white font-extrabold text-base transition-all duration-200 transform hover:scale-105 shadow-glow inline-flex items-center gap-3 cursor-pointer"
          >
            <span>Proceed to Step 1: Upload Job Description</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </section>
    </div>
  );
};
