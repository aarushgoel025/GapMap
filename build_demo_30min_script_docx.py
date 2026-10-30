import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=130, right=130):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_header_styled_row(table, headers, col_widths=None, bg_color="1E3A8A"):
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], bg_color)
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=130, right=130)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(10)
            run.font.name = "Calibri"
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)

def add_script_row(table, time_action_text, spoken_text, bg_color="FFFFFF", col_widths=None):
    row = table.add_row()
    
    # Left Cell: Time & Screen Action
    c_left = row.cells[0]
    c_left.text = time_action_text
    set_cell_background(c_left, bg_color)
    set_cell_margins(c_left, top=100, bottom=100, left=120, right=120)
    p_left = c_left.paragraphs[0]
    for run in p_left.runs:
        run.font.name = "Calibri"
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(31, 41, 55)
        
    # Right Cell: Speaker & Spoken Script
    c_right = row.cells[1]
    c_right.text = spoken_text
    set_cell_background(c_right, bg_color)
    set_cell_margins(c_right, top=100, bottom=100, left=130, right=130)
    p_right = c_right.paragraphs[0]
    for run in p_right.runs:
        run.font.name = "Calibri"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(17, 24, 39)

    if col_widths:
        row.cells[0].width = Inches(col_widths[0])
        row.cells[1].width = Inches(col_widths[1])

def add_callout(doc, text, title=None, alert_type="info"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(7.0)
    
    bg_map = {
        "info": "EFF6FF",     # Light Blue
        "warning": "FEF3C7",  # Light Yellow / Amber
        "tip": "ECFDF5",      # Light Green
        "navy": "F8FAFC"      # Slate Light
    }
    fill = bg_map.get(alert_type, "F3F4F6")
    set_cell_background(cell, fill)
    set_cell_margins(cell, top=110, bottom=110, left=150, right=150)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    
    if title:
        r_title = p.add_run(f"{title}\n")
        r_title.bold = True
        r_title.font.name = "Calibri"
        r_title.font.size = Pt(10)
        r_title.font.color.rgb = RGBColor(30, 58, 138)
            
    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(9.5)
    r_text.font.color.rgb = RGBColor(31, 41, 55)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def build_complete_document():
    doc = Document()
    
    # Page setup
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(31, 41, 55)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    # ==========================================
    # HEADER & TITLE BLOCK
    # ==========================================
    p_hdr = doc.add_paragraph()
    r = p_hdr.add_run("RADIX Talent Match Hackathon • 30-Minute Master Pitch Script\n")
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(107, 114, 128)
    
    p_title = doc.add_paragraph()
    r_main = p_title.add_run("GapMap: 30-Minute Master Pitch &\nLive Product Demonstration Script\n")
    r_main.font.size = Pt(22)
    r_main.font.bold = True
    r_main.font.color.rgb = RGBColor(30, 58, 138)
    
    r_sub = p_title.add_run("Complete Word-for-Word Script for All 5 Team Members with Parallel On-Screen Guide")
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(59, 130, 246)
    
    add_callout(doc, 
        "Pacing & Delivery Guide:\n"
        "• Total Duration: Exactly 30:00 (Structured into 7 clear segments).\n"
        "• Vocabulary: Natural, simple, conversational English. Speak calmly and clearly at ~130 words per minute.\n"
        "• Screen Synergy: The left column tells the screen controller exactly what to display, click, drag, or highlight while the speaker is talking in the right column.\n"
        "• All 5 members have substantial, balanced speaking time matching their official roles.",
        title="INSTRUCTIONS FOR THE TEAM",
        alert_type="info"
    )

    # Master Team Roster Table
    p_team_hdr = doc.add_paragraph()
    r = p_team_hdr.add_run("Team Presentation Roster & Time Allocation")
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor(30, 58, 138)
    
    t_team = doc.add_table(rows=1, cols=4)
    t_team.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_w = [1.2, 1.8, 1.2, 2.8]
    add_header_styled_row(t_team, ["Time", "Presenter", "Assigned Role", "Core Demonstration & Speaking Focus"], c_w)
    
    roster_rows = [
        ("00:00 – 06:00 (6m)", "Aarush (Lead)", "Scrum Master", "Executive Hook, The Broken ATS Reality, 4 USPs, and 5-Stage Pipeline Overview."),
        ("06:00 – 11:30 (5.5m)", "Samiksha", "Role 1: JD Analytics", "The 8 Talencia Systems Overview + Stage 1 Live Demo (Dual LLM, Weighting, SHA-256 Cache)."),
        ("11:30 – 17:00 (5.5m)", "Arushi", "Role 2: Resume Parsing", "Stage 2 Live Demo: Regex PII Scrubbing, Evidence Engine Proof Quotes, Anti-Stuffing Penalty Check."),
        ("17:00 – 20:30 (3.5m)", "Aarush", "Role 3: Profile Contract", "Stage 3 Live Demo: Pydantic v2 Unified Schema, Supabase + Offline JSON Fallback, Section F Audit Logs."),
        ("20:30 – 25:00 (4.5m)", "Aditya", "Role 4: Talent Check", "Stage 4 Live Demo: 12 Standardized Categories, 117+ Corporate Bars, Live What-If Slider Score Deltas."),
        ("25:00 – 28:00 (3m)", "Anjali", "Role 5: Skill Matching", "Stage 5 Live Demo: 3-Layer Matching Waterfall, Topological Prerequisite Learning Plan, 4x6 Heatmap."),
        ("28:00 – 30:00 (2m)", "Aarush", "Scrum Master Wrap-Up", "Quality Evidence (93% Precision, 96.8% Recall, 6 Robustness Tests), 135/135 Tests & Closing Pitch.")
    ]
    for r_data in roster_rows:
        row = t_team.add_row()
        for i, val in enumerate(r_data):
            row.cells[i].text = val
            set_cell_background(row.cells[i], "F9FAFB" if r_data[0].startswith("00") or r_data[0].startswith("17") else "FFFFFF")
            set_cell_margins(row.cells[i], top=80, bottom=80, left=110, right=110)
            p = row.cells[i].paragraphs[0]
            for run in p.runs:
                run.font.name = "Calibri"
                run.font.size = Pt(8.5)
                if i == 0 or i == 1:
                    run.font.bold = True
        for i, w in enumerate(c_w):
            row.cells[i].width = Inches(w)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    add_callout(doc,
        "1. Backend Server: Running on port 8000 (python -m uvicorn app.main:app --host 0.0.0.0 --port 8000)\n"
        "2. Frontend Web App: Running on port 5173 (npm --prefix frontend run dev) -> Open http://localhost:5173\n"
        "3. Presentation Slides: Open GapMap Hackathon Pitch.pptx in presenter view.\n"
        "4. Demo Files Folder: Have a clean desktop folder ready with:\n"
        "   • Google LLC - Software Engineer.pdf\n"
        "   • candidate_4_systems_engineer.pdf (Marcus Vance - triggers keyword stuffing anti-cheat)\n"
        "   • aarush_sharma_cv.pdf (or candidate_1_all_rounder.pdf)",
        title="PRE-FLIGHT SCREEN & DEMO CHECKLIST",
        alert_type="warning"
    )

    doc.add_page_break()

    # ==========================================
    # PART 1: AARUSH (00:00 - 06:00)
    # ==========================================
    p_sec = doc.add_paragraph()
    r = p_sec.add_run("Part 1: The Hook, Problem, 4 USPs & Pipeline Overview\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(30, 58, 138)
    
    r_meta = p_sec.add_run("Speaker: Aarush (Scrum Master / Team Lead) | Time: 00:00 – 06:00 (Duration: 6 Minutes)")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(107, 114, 128)
    
    t_p1 = doc.add_table(rows=1, cols=2)
    t_p1.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_widths = [2.5, 4.5]
    add_header_styled_row(t_p1, ["Time & On-Screen Action", "Speaker & Spoken Script"], s_widths)

    add_script_row(t_p1,
        "TIME: 00:00 – 01:15\n\n"
        "ON SCREEN:\n"
        "Slide 1 (Title Slide)\n"
        "• 'GapMap: Know your gap. Prove your skills.'\n"
        "• Badges visible: 117+ Corporate Hiring Bars | Dual-LLM Consensus | 135 Passing Tests.\n\n"
        "ACTION:\n"
        "Camera on Aarush / full screen slide. Steady, welcoming presence.",
        "SPEAKER: Aarush\n\n"
        "\"Good afternoon, respected judges, mentors, and fellow participants. Welcome to the final presentation of Team GapMap.\n\n"
        "My name is Aarush, and I am the Scrum Master for this project. Alongside me today are my four brilliant teammates: Samiksha, who built our Job Description Analytics engine; Arushi, who engineered our Resume Parsing and Evidence Verification; Aditya, who created our Corporate Talent Check and What-If Simulator; and Anjali, who developed our Explainable 3-Layer Skill Matching algorithm.\n\n"
        "Together, we built GapMap. Our mission is very simple and very clear: 'Know your gap, prove your skills.' Over the next 30 minutes, we are going to walk you through why modern hiring is broken, how our system completely changes the game with four unique engineering pillars, and we will demonstrate every single feature running live in front of you.\"",
        bg_color="F9FAFB", col_widths=s_widths
    )

    add_script_row(t_p1,
        "TIME: 01:15 – 02:45\n\n"
        "ON SCREEN:\n"
        "Transition to Slide 2:\n"
        "'The Problem with Traditional ATS'\n"
        "• Highlight graphic: 'The Keyword Lottery' vs 'The Stuffing Cheat'.\n"
        "• Stat callout: 75% of resumes filtered out by naive filters.\n\n"
        "ACTION:\n"
        "Use laser pointer or smooth click to reveal the keyword lottery diagram.",
        "SPEAKER: Aarush\n\n"
        "\"Let us start with the painful truth that every single student, job seeker, and engineer faces today: The hiring system is broken.\n\n"
        "Today, over 75% of qualified resumes are silently rejected before a human recruiter ever opens them. Why does this happen? Because traditional Applicant Tracking Systems—or ATS—rely purely on dumb keyword matching. They play what we call a 'keyword lottery.'\n\n"
        "For example, if a job description asks for 'SQL Databases' and an applicant writes 'PostgreSQL' or 'Relational Databases', legacy tools reject them simply because the exact letters do not match.\n\n"
        "Even worse is what we call 'The Stuffing Cheat.' Dishonest applicants quickly figure out how the system works. They copy buzzwords like Docker, Kubernetes, and System Design into their resume summary, or hide them in white text. The legacy ATS sees those keywords, assumes the candidate is an expert, and pushes them forward, while honest candidates who actually built real projects get filtered out.\n\n"
        "And the saddest part? When candidates are rejected, they get zero feedback. They have no idea why they failed, how far they were from the hiring bar, or what they need to learn to get hired next time. It is a completely opaque black box.\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    add_script_row(t_p1,
        "TIME: 02:45 – 04:30\n\n"
        "ON SCREEN:\n"
        "Transition to Slide 3 & Slide 4:\n"
        "'The GapMap Solution & The 4 Core USPs'\n"
        "• Show the 4 Quadrant Cards:\n"
        "  1. Proof-Backed Skills & Anti-Stuffing\n"
        "  2. What-If Simulator & Hiring Bars\n"
        "  3. Explainable 3-Layer Matching\n"
        "  4. Trustworthy AI Consensus\n\n"
        "ACTION:\n"
        "Highlight each of the 4 cards smoothly as they are introduced.",
        "SPEAKER: Aarush\n\n"
        "\"That brings us to GapMap. Most teams in this hackathon will build the basic tool: upload a resume, ask an LLM for an ATS score, and output a list of missing words. But public GitHub repositories already do that, and that alone does not solve the candidate's real problem.\n\n"
        "We set out to stand out by building our tool around Four Deep Pillars:\n\n"
        "First is our Evidence Engine. Our motto is: 'Do not just claim it. Prove it.' Every skill GapMap extracts is paired with an exact sentence quote from the resume. If someone lists a skill without any project proof, our anti-stuffing detector flags it and cuts its score credit by 50%.\n\n"
        "Second is our What-If Simulator. Instead of an arbitrary percentage, we benchmark candidates against 117+ top corporate hiring bars across 12 standardized categories. With live sliders, candidates can test: 'What if my SQL was level 6?' and immediately see their score update and their weeks-to-ready placement timeline drop.\n\n"
        "Third is our Explainable 3-Layer Matching. We do not let LLMs invent scores out of thin air. We use strict deterministic math across three layers: Exact Match for 1.0 credit, Curated Aliases for 0.9 credit, and Local Vector Cosine Similarity for 0.8 credit.\n\n"
        "And fourth is our Trustworthy AI Pipeline. We use two LLMs—Google Gemini 2.5 and Mistral—running in parallel to settle disagreements, validated with Pydantic self-healing loops, and tested with 135 automated unit tests.\"",
        bg_color="F9FAFB", col_widths=s_widths
    )

    add_script_row(t_p1,
        "TIME: 04:30 – 06:00\n\n"
        "ON SCREEN:\n"
        "Transition to Slide 5:\n"
        "'The 5-Stage End-to-End Pipeline'\n"
        "• Show the full flow:\n"
        "  JD Analytics -> Resume Parsing -> Profile Contract -> Talent Check -> Skill Matching\n\n"
        "ACTION:\n"
        "Trace the arrow from Stage 1 to Stage 5, then hand over screen to Samiksha.",
        "SPEAKER: Aarush\n\n"
        "\"To turn this vision into a working product, we organized our software into a seamless 5-stage automated flow, as you see right here on Slide 5:\n\n"
        "In Stage 1, we analyze the Job Description to extract essential must-have skills versus nice-to-have skills.\n\n"
        "In Stage 2, we parse the candidate resume, scrub private contact info, pull proof quotes, and run our anti-stuffing check.\n\n"
        "In Stage 3, we build the unified Profile Contract, saving it into our database with an offline failover.\n\n"
        "In Stage 4, we evaluate the candidate's readiness against actual corporate hiring thresholds and let them experiment with the What-If slider.\n\n"
        "And in Stage 5, our 3-layer matching engine computes the final match score and generates a step-by-step prerequisite learning roadmap.\n\n"
        "Now, rather than talking through slides, we want to prove that our tool truly works. I will now hand over to Samiksha to walk us through the Talencia architecture and demonstrate Stage 1 live on our web platform.\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    doc.add_page_break()

    # ==========================================
    # PART 2: SAMIKSHA (06:00 - 11:30)
    # ==========================================
    p_sec = doc.add_paragraph()
    r = p_sec.add_run("Part 2: Talencia Systems Overview & Stage 1 Live Demo (JD Analytics)\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(30, 58, 138)
    
    r_meta = p_sec.add_run("Speaker: Samiksha (Role 1 — JD Analytics) | Time: 06:00 – 11:30 (Duration: 5.5 Minutes)")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(107, 114, 128)
    
    t_p2 = doc.add_table(rows=1, cols=2)
    t_p2.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_styled_row(t_p2, ["Time & On-Screen Action", "Speaker & Spoken Script"], s_widths)

    add_script_row(t_p2,
        "TIME: 06:00 – 07:30\n\n"
        "ON SCREEN:\n"
        "Slide 6 & Slide 7:\n"
        "'The 8 TalenciaGlobal Systems'\n"
        "• Quickly show the 8 systems grid:\n"
        "  01. Parameter Discovery (12 Codes)\n"
        "  02. Database Normalization (3NF)\n"
        "  03. Test Automation (135 tests)\n"
        "  04. Agentic Research (Dual LLM)\n"
        "  05. Agentic Ecosystem (Pydantic)\n"
        "  06. DevOps & Cloud (Docker/CI)\n"
        "  07. Vector DB & ML (Cosine/Embed)\n"
        "  08. Enterprise Governance (PII/Audit)\n\n"
        "ACTION:\n"
        "Brief highlight of Systems 01 and 04 before switching to the browser.",
        "SPEAKER: Samiksha\n\n"
        "\"Thank you, Aarush. Hello everyone, I am Samiksha, and I led the development of our Job Description Analytics module.\n\n"
        "Before we look at the live tool, let us look at Slides 6 and 7. The hackathon guidelines outlined 8 Talencia Systems, and our team ensured that every single one of them is built right into our codebase:\n\n"
        "System 1 gives us standardized taxonomy across 12 engineering categories like Coding, Cloud, and Databases. System 2 is our 3NF database schema with local JSON fallback. System 3 is our test suite of 135 passing pytest tests. System 4 is our dual-LLM consensus engine. System 5 is our self-healing Pydantic schema loop. System 6 is our multi-stage Docker setup. System 7 is our local vector embedding engine. And System 8 is our privacy protection and Section F audit trail.\n\n"
        "Every single architectural pointer has been built, tested, and verified. Now, let us switch our screen to our live web application running on port 5173.\"",
        bg_color="F9FAFB", col_widths=s_widths
    )

    add_script_row(t_p2,
        "TIME: 07:30 – 09:15\n\n"
        "ON SCREEN:\n"
        "Switch to Browser: http://localhost:5173\n"
        "• Landing Page is visible.\n"
        "• Scroll down smoothly past the Hero Section.\n"
        "• Pause at the new 'Why GapMap Stands Out: The 4 USPs' section.\n"
        "• Highlight the 4 cards and the Deterministic Formula callout banner.\n\n"
        "ACTION:\n"
        "Click the top CTA button:\n"
        "'Launch Pipeline (Step 1: Upload JD)'.",
        "SPEAKER: Samiksha\n\n"
        "\"Here we are on the GapMap landing page. As you can see, our 4 Core Pillars and our 8 Talencia systems are prominently displayed right below our 5-stage pipeline overview.\n\n"
        "Now, let us begin the live demo by clicking 'Launch Pipeline (Step 1: Upload JD)'. This takes us into Stage 1: Job Description Analytics.\n\n"
        "The fundamental question in Stage 1 is: How do you extract what a company really cares about without relying on lucky keyword guesses? When a company posts a job, not all skills are equal. A Software Engineer role at Google requires Coding and Data Structures as mandatory must-haves, whereas knowing Kubernetes or Docker might simply be a nice-to-have bonus.\n\n"
        "To solve this, our backend uses a dual-LLM architecture. We send parallel prompt requests to Google Gemini 2.5 Flash and Mistral AI. Both models read the text, identify technical requirements, and classify them into our 12 standardized category codes.\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    add_script_row(t_p2,
        "TIME: 09:15 – 11:30\n\n"
        "ON SCREEN:\n"
        "Inside JD Analytics Page:\n"
        "• Click 'Choose Sample JD' -> Select 'Google LLC - Software Engineer.pdf'.\n"
        "• Click 'Analyze Job Description'.\n"
        "• Watch the progress bar complete in ~1.2s.\n"
        "• Point mouse at the table:\n"
        "  - Skill Name column\n"
        "  - Category Code (COD, DSA, SWE, CLOUD)\n"
        "  - Importance Badge (Must-Have = 2.0x vs Nice-to-Have = 1.0x)\n"
        "  - Consensus Badge (Gemini + Mistral Agree)\n"
        "  - SHA-256 Cache badge.\n\n"
        "ACTION:\n"
        "Scroll through the 18 extracted skills cleanly.",
        "SPEAKER: Samiksha\n\n"
        "\"Let us upload the official Google Software Engineer Job Description. When I click 'Analyze Job Description', watch how fast it responds: in just 1.2 seconds, the analysis is complete.\n\n"
        "Why is it so fast? Because of our SHA-256 prompt hashing cache. If this exact job description has been analyzed before, GapMap returns the verified, cached JSON payload instantly, saving API cost and eliminating latency.\n\n"
        "Now look at the results table:\n"
        "Notice the 'Importance' column. Python, C++, Data Structures, and Algorithms are clearly tagged as 'Must-Have'. In our downstream scoring engine, Must-Have skills are assigned double weight—a 2.0 multiplier. In contrast, skills like Kubernetes and Cloud Architecture are tagged as 'Nice-to-Have' with a 1.0 multiplier.\n\n"
        "Also notice the 'Consensus' indicator: both Gemini and Mistral concurred on these categories. When models disagree on a category code, our backend records it in an audit log and adjusts the initial confidence.\n\n"
        "Now that our target job requirements are structured and weighted, the next step is to examine the candidate's resume. I will hand over to Arushi to demonstrate Stage 2.\"",
        bg_color="F9FAFB", col_widths=s_widths
    )

    doc.add_page_break()

    # ==========================================
    # PART 3: ARUSHI (11:30 - 17:00)
    # ==========================================
    p_sec = doc.add_paragraph()
    r = p_sec.add_run("Part 3: Stage 2 Live Demo (Resume Parsing & The Evidence Engine)\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(30, 58, 138)
    
    r_meta = p_sec.add_run("Speaker: Arushi (Role 2 — Resume Parsing) | Time: 11:30 – 17:00 (Duration: 5.5 Minutes)")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(107, 114, 128)
    
    t_p3 = doc.add_table(rows=1, cols=2)
    t_p3.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_styled_row(t_p3, ["Time & On-Screen Action", "Speaker & Spoken Script"], s_widths)

    add_script_row(t_p3,
        "TIME: 11:30 – 13:45\n\n"
        "ON SCREEN:\n"
        "• Click button: 'Proceed to Step 2: Resume Parsing'.\n"
        "• Select file: 'candidate_4_systems_engineer.pdf' (Marcus Vance).\n"
        "• Click 'Extract & Verify Resume'.\n"
        "• Point out the top header: Candidate Name is parsed, but personal email, phone number, and street address are cleanly masked as [REDACTED].\n\n"
        "ACTION:\n"
        "Hover over the PII Anonymization badge to show privacy compliance.",
        "SPEAKER: Arushi\n\n"
        "\"Thank you, Samiksha. Hello everyone, my name is Arushi, and I built the Resume Parsing engine and our Evidence Verification pipeline.\n\n"
        "Parsing a resume is where legacy ATS systems cause the most harm. Resumes come in messy two-column formats, different font encodings, and wildly varying layouts. Furthermore, sending unmasked personal data to external AI models is a serious privacy violation.\n\n"
        "In GapMap, we solved this with a two-tier approach. First, our plain Python backend uses pdfplumber and python-docx with coordinate bounding-box extraction. This ensures that two-column resumes are read in logical vertical order, without sentences from column one bleeding into column two.\n\n"
        "Second, before any text is processed or sent to an LLM, our regex PII scrubber scans the document and completely redacts telephone numbers, personal emails, and home addresses, as you can see on screen in the top preview. This guarantees candidate privacy and satisfies Talencia System 8 enterprise governance.\"",
        bg_color="F9FAFB", col_widths=s_widths
    )

    add_script_row(t_p3,
        "TIME: 13:45 – 15:30\n\n"
        "ON SCREEN:\n"
        "Inside Resume Results:\n"
        "• Look at verified skill: 'Docker'.\n"
        "• Click 'View Evidence' button to slide open the Proof Drawer.\n"
        "• Show the verbatim sentence quote from the resume: 'Containerized 4 microservices with Docker Compose and managed automated builds.'\n"
        "• Show Confidence: HIGH.\n"
        "• Show Source: Projects section.\n\n"
        "ACTION:\n"
        "Highlight the quote box on screen.",
        "SPEAKER: Arushi\n\n"
        "\"Now, let us demonstrate our first core USP: **The Evidence Engine**.\n\n"
        "Remember our demo line: 'Do not just claim it. Prove it.' In traditional tools, if an applicant writes 'Docker' anywhere on the page, the system gives them a green checkmark. But did they actually build anything with Docker, or did they just read a blog post?\n\n"
        "Look at what GapMap does when I click on 'Docker'. A proof drawer slides open. GapMap shows the exact sentence quote directly from Marcus's resume: *'Containerized 4 microservices with Docker Compose and managed automated builds.'*\n\n"
        "Because this skill is anchored to practical implementation in the Projects section, our algorithm assigns it High Confidence and verifies it. A human hiring manager or an automated evaluator can immediately see the proof behind the claim. There is zero guessing.\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    add_script_row(t_p3,
        "TIME: 15:30 – 17:00\n\n"
        "ON SCREEN:\n"
        "Scroll down to ungrounded skills in the table:\n"
        "• Look at 'Kubernetes' and 'GraphQL'.\n"
        "• Point mouse at the Amber Alert Badge: 'Keyword Stuffing Detected'.\n"
        "• Expand the warning details: shows that skill appeared only in top summary list, with 0 project mentions.\n"
        "• Point out: 'Confidence demoted to LOW; 50% Scoring Penalty applied'.\n\n"
        "ACTION:\n"
        "Show the difference between honest skills and stuffed skills.",
        "SPEAKER: Arushi\n\n"
        "\"Now look at what happens when someone tries to cheat the system.\n\n"
        "Marcus Vance listed 'Kubernetes' and 'GraphQL' in his introductory summary skills list. A legacy ATS would give him full points for both. But GapMap's anti-stuffing engine audits the entire narrative of the resume using word-boundary regular expressions and contextual sentence trees.\n\n"
        "Our engine found that Marcus never mentioned Kubernetes in any company role, never mentioned it in any project, and never cited a single metric or achievement. It was just a buzzword dumped into the text to manipulate search filters.\n\n"
        "Notice what GapMap does: it immediately flags `stuffing_flag = True`, displays an amber warning badge, lowers the confidence level to Low, and cuts its scoring weight in half (`STUFFING_PENALTY = 0.5`). We also provide an optional GitHub API check that verifies if the candidate has public repositories using those languages.\n\n"
        "This completely protects honest candidates from being outranked by dishonest resume padders. I will now hand back to Aarush to show how this data forms our unified Profile Contract.\"",
        bg_color="F9FAFB", col_widths=s_widths
    )

    doc.add_page_break()

    # ==========================================
    # PART 4: AARUSH (17:00 - 20:30)
    # ==========================================
    p_sec = doc.add_paragraph()
    r = p_sec.add_run("Part 4: Stage 3 Live Demo (Unified Profile Contract & Persistence)\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(30, 58, 138)
    
    r_meta = p_sec.add_run("Speaker: Aarush (Role 3 — Profile Builder) | Time: 17:00 – 20:30 (Duration: 3.5 Minutes)")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(107, 114, 128)
    
    t_p4 = doc.add_table(rows=1, cols=2)
    t_p4.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_styled_row(t_p4, ["Time & On-Screen Action", "Speaker & Spoken Script"], s_widths)

    add_script_row(t_p4,
        "TIME: 17:00 – 18:45\n\n"
        "ON SCREEN:\n"
        "• Click button: 'Proceed to Step 3: Candidate Profile'.\n"
        "• Profile form loads seamlessly.\n"
        "• Shows Candidate Name, Education, Verified Skills List with categories, and Preferred Roles.\n"
        "• Demonstrate inline editing: Change candidate's estimated skill level or add a verified hackathon/internship.\n\n"
        "ACTION:\n"
        "Type an update in the input box, showing full reactivity.",
        "SPEAKER: Aarush\n\n"
        "\"Thank you, Arushi. Welcome to Stage 3: The Profile Builder.\n\n"
        "In a five-person team project, the biggest point of failure is almost always integration. If the resume parser outputs one format, the profile builder expects another, and the scoring engine expects a third, the entire application breaks.\n\n"
        "As Scrum Master, we tackled this right at the beginning by defining strict Pydantic v2 data models in `shared/schemas.py`. Every field—from `category_code` to `confidence` and `stuffing_flag`—is strictly typed.\n\n"
        "Here on screen, you see our candidate profile. It is automatically pre-filled from Arushi's parser. But we also believe in candidate empowerment: an applicant can review their parsed profile, verify their education, and make manual edits if needed. If I want to update an estimated level or add an internship, I can do so right here in the UI.\"",
        bg_color="F9FAFB", col_widths=s_widths
    )

    add_script_row(t_p4,
        "TIME: 18:45 – 20:30\n\n"
        "ON SCREEN:\n"
        "• Click 'Save Profile' button.\n"
        "• Green success notification: 'Profile Saved Successfully'.\n"
        "• Open Section F Audit Logs drawer on the right side of the screen.\n"
        "• Show log entry with timestamp, profile ID, and action performed.\n\n"
        "ACTION:\n"
        "Scroll through the audit log entries cleanly.",
        "SPEAKER: Aarush\n\n"
        "\"When I click 'Save Profile', watch what happens under the hood:\n\n"
        "The profile is validated by Pydantic and committed to our Supabase PostgreSQL relational database, satisfying Talencia System 2. But what if there is no internet connection during a live interview or hackathon demo? Our backend automatically falls back to local JSON persistence in `backend/data/profiles/`. It is 100% resilient and will never crash due to a network drop.\n\n"
        "Now look at the right side of the screen. I am opening the **Section F Audit Trail** drawer. Every single operation—every document parsed, every profile updated, and every scoring run—is recorded with a millisecond timestamp, action name, and user ID. This gives enterprises complete traceability and compliance.\n\n"
        "Now that we have a verified, structured candidate profile, the big question is: Are they actually ready for the corporate hiring bar? I will hand over to Aditya to show Stage 4.\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    doc.add_page_break()

    # ==========================================
    # PART 5: ADITYA (20:30 - 25:00)
    # ==========================================
    p_sec = doc.add_paragraph()
    r = p_sec.add_run("Part 5: Stage 4 Live Demo (Talent Check & What-If Simulator)\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(30, 58, 138)
    
    r_meta = p_sec.add_run("Speaker: Aditya (Role 4 — Talent Check) | Time: 20:30 – 25:00 (Duration: 4.5 Minutes)")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(107, 114, 128)
    
    t_p5 = doc.add_table(rows=1, cols=2)
    t_p5.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_styled_row(t_p5, ["Time & On-Screen Action", "Speaker & Spoken Script"], s_widths)

    add_script_row(t_p5,
        "TIME: 20:30 – 22:30\n\n"
        "ON SCREEN:\n"
        "• Click button: 'Proceed to Step 4: Talent Readiness Check'.\n"
        "• Company selector dropdown appears.\n"
        "• Select 'Google LLC'.\n"
        "• Show the readiness score ring: 68.2% (Status: 'Almost there').\n"
        "• Show the 12 Category breakdown bars:\n"
        "  - Green bars = Meets or exceeds required level\n"
        "  - Red/Yellow bars = Skill gap present.\n\n"
        "ACTION:\n"
        "Point to the gap in 'SQL & Databases' and 'Cloud Computing'.",
        "SPEAKER: Aditya\n\n"
        "\"Thank you, Aarush. Hello everyone, I am Aditya, and I built the Talent Check engine and our What-If Simulator.\n\n"
        "When candidates ask, 'Am I ready for Google or Amazon?', traditional career advice is uselessly generic: 'Work on your projects, practice LeetCode.' There is no standard benchmark.\n\n"
        "In GapMap, we loaded verified corporate hiring benchmarks for over 117 top companies from `talent_check_company_skillsets.json`. Each company profile defines exact target competency levels—from 1 to 10—across our 12 standardized categories.\n\n"
        "Here on screen, we selected Google LLC for our candidate Marcus. Look at his baseline score: **68.2%**, which gives him the status **'Almost there'**.\n\n"
        "In our scoring engine, **'Ready'** is defined strictly as reaching a cumulative weighted score of **80.0% or higher**. If you look at the category breakdown bars below, you can see exactly why Marcus is at 68%: he meets the bar in Software Engineering and Coding, but there is a clear deficit in SQL Databases and Cloud Computing.\"",
        bg_color="F9FAFB", col_widths=s_widths
    )

    add_script_row(t_p5,
        "TIME: 22:30 – 25:00\n\n"
        "ON SCREEN:\n"
        "Highlight Pillar 2: The What-If Simulator!\n"
        "• Focus on the 'Interactive Skill Sliders' panel.\n"
        "• Grab the slider for 'SQL and Databases' (currently at level 3).\n"
        "• Drag the slider slowly from level 3 up to level 7.\n"
        "• Watch the Readiness Score ring recalculate in real-time:\n"
        "  68.2% -> 74.0% -> 81.4%!\n"
        "• The status badge flips from yellow 'Almost there' to bright green 'READY'!\n"
        "• The 'Estimated Weeks to Ready' metric drops from 12 weeks to 3 weeks!\n\n"
        "ACTION:\n"
        "Keep hands on the slider for maximum visual impact.",
        "SPEAKER: Aditya\n\n"
        "\"Now let us look at our second core USP: **The What-If Simulator**.\n\n"
        "Instead of just telling Marcus that he is rejected, we give him an interactive sandbox to plan his career advancement. Look at the sliders on screen.\n\n"
        "Suppose Marcus wants to know: *'What happens if I dedicate the next three weeks to mastering SQL, relational databases, and query optimization, and raise my competency from level 3 to level 7?'*\n\n"
        "Watch the screen as I drag this SQL slider right now. As I move the slider from 3 to 7, the mathematical formula executes live in memory. The score climbs from 68.2% to 74%... and now crosses 81.4%! \n\n"
        "Notice what happened: The status indicator instantly flips from yellow 'Almost there' to vibrant green 'READY'! And look at the placement timeline below: his estimated time to meet the Google hiring bar drops from 12 weeks down to just 3 weeks.\n\n"
        "This completely removes guesswork. The candidate knows exactly which skill moves the needle the most, how many points it adds, and how long it will take. Now, let us see how this translates into specific job matching. I will hand over to Anjali for Stage 5.\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    doc.add_page_break()

    # ==========================================
    # PART 6: ANJALI (25:00 - 28:00)
    # ==========================================
    p_sec = doc.add_paragraph()
    r = p_sec.add_run("Part 6: Stage 5 Live Demo (Skill Matching Engine & 4x6 Heatmap)\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(30, 58, 138)
    
    r_meta = p_sec.add_run("Speaker: Anjali (Role 5 — Skill Matching) | Time: 25:00 – 28:00 (Duration: 3.0 Minutes)")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(107, 114, 128)
    
    t_p6 = doc.add_table(rows=1, cols=2)
    t_p6.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_styled_row(t_p6, ["Time & On-Screen Action", "Speaker & Spoken Script"], s_widths)

    add_script_row(t_p6,
        "TIME: 25:00 – 26:30\n\n"
        "ON SCREEN:\n"
        "• Click button: 'Proceed to Step 5: Skill Matching Engine'.\n"
        "• Match Results card displays Match Score (e.g. 76.0%).\n"
        "• Scroll to 'Deterministic Scoring Breakdown' box showing the formula:\n"
        "  Score = 100 * Sum(Weight * Credit) / Sum(Weight)\n"
        "• Point to the Matched Skills table with badges:\n"
        "  - Layer 1: Exact Match (Credit: 1.0)\n"
        "  - Layer 2: Alias Match (Credit: 0.9)\n"
        "  - Layer 3: Semantic Match (Credit: 0.8 * Cosine).\n\n"
        "ACTION:\n"
        "Highlight the layer badges in the table.",
        "SPEAKER: Anjali\n\n"
        "\"Thank you, Aditya. Hello everyone, my name is Anjali, and I developed the Skill Matching Engine and our Prerequisite Learning Graph.\n\n"
        "In Stage 5, we compare the candidate's profile against the target Job Description we parsed in Stage 1. This brings us to our third core USP: **Explainable 3-Layer Matching**.\n\n"
        "As you can see in the Deterministic Scoring card, our score is computed strictly by mathematical formula:\n"
        "$$\\text{Match Score} = 100 \\times \\frac{\\sum (w_i \\cdot c_i)}{\\sum w_i}$$\n"
        "We never ask an LLM to guess a score. Every point is calculated deterministically across three layers:\n\n"
        "Look at the badges in our Matched Skills table:\n"
        "First, 'Python' matched with a full 1.0 credit through Layer 1 Exact Match.\n"
        "Second, 'PostgreSQL' matched with a 0.9 credit through Layer 2 Alias Match—our system knows through `aliases.json` that PostgreSQL satisfies the SQL database requirement.\n"
        "Third, 'Distributed Systems' matched through Layer 3 Semantic Cosine Similarity. Using local 256-dimensional vector embeddings, our engine computed a cosine similarity of 0.86, awarding a credit of 0.8 times the similarity.\n\n"
        "Every single match is 100% explainable. The candidate and the recruiter know exactly which layer matched the skill and why.\"",
        bg_color="F9FAFB", col_widths=s_widths
    )

    add_script_row(t_p6,
        "TIME: 26:30 – 28:00\n\n"
        "ON SCREEN:\n"
        "• Scroll down to 'Prerequisite-Ordered Learning Plan':\n"
        "  Point out that Docker is ranked #1 (Learn First), before Kubernetes.\n"
        "• Click button: 'View 4×6 Candidate Fit Heatmap Matrix'.\n"
        "• The 4×6 Heatmap modal pops up:\n"
        "  Show 4 Candidates (Alex, Priya, Marcus, Sofia) across 6 Roles (Google SWE, Amazon DevOps, etc.).\n"
        "• Show high contrast: Sofia leads in Data, Alex in SWE, Priya in Oracle.\n\n"
        "ACTION:\n"
        "Point cursor across the varied scores in the heatmap matrix.",
        "SPEAKER: Anjali\n\n"
        "\"Now look at the Missing Skills section below. When a candidate has gaps, other tools just dump an alphabetical list. But learning is sequential: you cannot learn Kubernetes if you do not understand containers.\n\n"
        "GapMap uses Kahn's topological sort algorithm to construct a **Prerequisite Dependency Graph**. As you can see, our roadmap orders missing skills logically: it tells the candidate to learn *Docker Containerization* first, before moving on to *Kubernetes Orchestration*, and shows the exact point impact each skill adds.\n\n"
        "Finally, look at our **4×6 Candidate Heatmap Matrix** on screen. We benchmarked four different candidates across six corporate roles. Notice the variance:\n"
        "Alex Chen scores 83.3% on Google Software Engineer, but only 40.8% on Cloud Architect. In contrast, Sofia Rodriguez scores 86.7% on Data Engineer, but only 59.1% on pure SWE.\n\n"
        "This proves that GapMap is not a blunt, one-size-fits-all grading tool. It recognizes individual domain specialization with total mathematical fidelity. I will now hand back to Aarush for our quality evidence and closing summary.\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    doc.add_page_break()

    # ==========================================
    # PART 7: AARUSH (28:00 - 30:00)
    # ==========================================
    p_sec = doc.add_paragraph()
    r = p_sec.add_run("Part 7: Measured Quality Evidence, Retrospective & Closing Pitch\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(30, 58, 138)
    
    r_meta = p_sec.add_run("Speaker: Aarush (Scrum Master Wrap-Up) | Time: 28:00 – 30:00 (Duration: 2.0 Minutes)")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(107, 114, 128)
    
    t_p7 = doc.add_table(rows=1, cols=2)
    t_p7.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_styled_row(t_p7, ["Time & On-Screen Action", "Speaker & Spoken Script"], s_widths)

    add_script_row(t_p7,
        "TIME: 28:00 – 29:15\n\n"
        "ON SCREEN:\n"
        "Switch back to Presentation Slides:\n"
        "Slide 13 & Slide 14:\n"
        "'Quality Evidence & Robustness Testing'\n"
        "• Table showing Ground Truth metrics:\n"
        "  - Google SWE: 94.7% Precision\n"
        "  - Alex Chen: 95.7% Precision\n"
        "  - Overall Average: 93.0% Precision, 96.8% Recall.\n"
        "• Slide 14: 6 Robustness tests (All Pass / Graceful).\n"
        "• Highlight badge: '135/135 Automated Pytest Tests Passing in 7.3s'.\n\n"
        "ACTION:\n"
        "Direct judge attention to the measured numbers.",
        "SPEAKER: Aarush\n\n"
        "\"Thank you, Anjali. To conclude our presentation, let us look at the verified evidence of our work on Slides 13, 14, and 15.\n\n"
        "In Section 7 of our solution document, we measured our extraction accuracy against human-annotated ground truth across four documents: Google SWE, Microsoft Data Analyst, Alex Chen, and Marcus Vance.\n\n"
        "GapMap achieved an average **Precision of 93.0% and an average Recall of 96.8%**. When early runs struggled with composite phrases like 'CI/CD automated pipelines', we refined our prompt boundaries and added canonical normalization, boosting our precision significantly.\n\n"
        "On Slide 14, you see our 6 Robustness Stress Tests: our parser extracts identical skills from PDF and DOCX formats; same JDs produce identical outputs via SHA-256 caching; messy two-column layouts are handled cleanly; unlisted skills map gracefully to the 'OTHER' category; and scanned image PDFs return a clean user warning without crashing.\n\n"
        "Furthermore, our automated test suite contains **135 automated pytest tests that pass in 7.3 seconds with a 100% pass rate**, covering contract validation, multi-LLM consensus, and scoring formulas.\"",
        bg_color="F9FAFB", col_widths=s_widths
    )

    add_script_row(t_p7,
        "TIME: 29:15 – 30:00\n\n"
        "ON SCREEN:\n"
        "Slide 17 & Slide 18 (Closing Slide):\n"
        "'GapMap: The Future of Transparent, Fair Hiring'\n"
        "• Definition of Done: All 5 Checkboxes [X] Marked.\n"
        "• QR Code & Link to GitHub Repository and Live Demo.\n"
        "• All 5 team members visible on screen or in frame.\n\n"
        "ACTION:\n"
        "Aarush delivers closing sentence with conviction and opens for jury Q&A.",
        "SPEAKER: Aarush\n\n"
        "\"To summarize:\n"
        "GapMap replaces the black-box ATS keyword lottery with verifiable proof.\n\n"
        "We verify proof-backed evidence so honest candidates shine. We penalize keyword stuffing so dishonest shortcuts fail. We benchmark candidates against 117+ corporate hiring bars with a live What-If simulator. And we build prerequisite-ordered roadmaps so candidates know exactly how to bridge their gaps.\n\n"
        "Our team has fulfilled 100% of the Definition of Done. The code is clean, fully containerized with Docker, verified by 135 tests, and ready for deployment.\n\n"
        "Thank you so much for your time and attention. We are Team GapMap, and we are now eager to take your questions!\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    doc.add_page_break()

    # ==========================================
    # APPENDIX: JUDGE Q&A CHEAT SHEET
    # ==========================================
    p_sec = doc.add_paragraph()
    r = p_sec.add_run("Appendix: Top 5 Anticipated Judge Q&A Defenses\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(30, 58, 138)
    
    r_meta = p_sec.add_run("Quick-reference guide for the team to handle tough technical questions during the Q&A session.")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(107, 114, 128)
    
    qa_list = [
        ("Q1: Why did you build your own 3-layer matching math instead of letting an LLM calculate the match score?",
         "Defense: Because LLMs are non-deterministic and suffer from numerical hallucination. If you prompt an LLM five times with the same resume and JD, you can get scores varying between 65% and 85%. That is catastrophic for fairness and legal compliance. In GapMap, we use LLMs solely for semantic extraction, and we delegate 100% of the scoring to deterministic mathematical formulas: Exact (1.0), Alias (0.9), and Semantic Cosine (0.8 x Cos). It is 100% reproducible and explainable."),
        ("Q2: How exactly does your anti-stuffing detector work without flagging legitimate short skill names like 'Go' or 'C'?",
         "Defense: A naive substring regex searching for 'Go' will match 'Google' or 'Going'. We implemented strict word-boundary tokenization (\\bGo\\b) combined with section-aware contextual parsing. Furthermore, GapMap checks whether the skill appears in the candidate's actual narrative—under professional experience or projects—alongside an action verb. If 'Go' only appears in an isolated header comma-separated list without project reference, our system flags stuffing_flag: True and applies STUFFING_PENALTY = 0.5, halving its scoring credit."),
        ("Q3: What happens if Gemini or Mistral goes down, or if evaluators test your code offline without API keys?",
         "Defense: GapMap is engineered with zero single points of failure. First, we use a dual-LLM parallel consensus architecture with fallback triggers. Second, our SHA-256 prompt cache instantly serves previously analyzed documents without making a network call. Third, if API keys are absent or the system is completely offline, our backend automatically activates built-in deterministic mock fallbacks based on our pre-seeded ground-truth fixtures in backend/data/. The app never crashes, and evaluators can verify the entire flow offline."),
        ("Q4: How did you establish the corporate hiring benchmarks for 117+ companies?",
         "Defense: Our dataset in talent_check_company_skillsets.json standardizes corporate hiring bars across 12 distinct domains—such as Coding, System Design, Cloud, and Data Structures. Each company tier reflects calibrated competency levels (from 1 to 10) based on verified industry technical interview rubrics. For example, Google and Amazon require level 8 to 9 in System Design and DSA for L5 roles, while specialized enterprise firms like Oracle emphasize high SQL and Application Support. Our Talent Check engine evaluates the gap against these exact numeric targets."),
        ("Q5: How does your system protect candidate privacy and comply with enterprise data governance?",
         "Defense: Enterprise governance was built in from Day 1 as System 08 of our Talencia architecture. Before any resume text is sent to an LLM or stored, our regex PII scrubber strips phone numbers, email addresses, and physical locations. All database operations are logged with timestamps in our Section F audit trail, and candidate GitHub verification is strictly opt-in using public repository metadata without accessing private code.")
    ]
    
    t_qa = doc.add_table(rows=1, cols=2)
    t_qa.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_styled_row(t_qa, ["Question", "Recommended Speaker & Bulletproof Technical Defense"], [2.2, 4.8])
    for q, ans in qa_list:
        row = t_qa.add_row()
        row.cells[0].text = q
        row.cells[1].text = ans
        set_cell_background(row.cells[0], "F9FAFB")
        set_cell_background(row.cells[1], "FFFFFF")
        set_cell_margins(row.cells[0], top=90, bottom=90, left=110, right=110)
        set_cell_margins(row.cells[1], top=90, bottom=90, left=120, right=120)
        p0 = row.cells[0].paragraphs[0]
        p0.runs[0].font.name = "Calibri"
        p0.runs[0].font.size = Pt(9)
        p0.runs[0].font.bold = True
        p1 = row.cells[1].paragraphs[0]
        p1.runs[0].font.name = "Calibri"
        p1.runs[0].font.size = Pt(9.5)
        row.cells[0].width = Inches(2.2)
        row.cells[1].width = Inches(4.8)

    # Save
    out_path = r"c:\Users\Aarush\OneDrive\Desktop\GapMap\GapMap_30Min_Master_Demo_Script.docx"
    doc.save(out_path)
    print(f"Document successfully created at {out_path}")

if __name__ == "__main__":
    build_complete_document()

