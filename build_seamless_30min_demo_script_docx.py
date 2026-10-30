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

def add_header_styled_row(table, headers, col_widths=None, bg_color="0B1120"):
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], bg_color)
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=130, right=130)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(0, 240, 249) # Cyan accent from PPT
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
        if any(tag in run.text for tag in ["ON SCREEN:", "TIME:", "ACTION:", "SPEAKER:"]):
            run.font.bold = True
            
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
        if run.text.startswith("SPEAKER:"):
            run.font.bold = True

    if col_widths:
        row.cells[0].width = Inches(col_widths[0])
        row.cells[1].width = Inches(col_widths[1])

def add_callout(doc, text, title=None, alert_type="info"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(7.0)
    
    bg_map = {
        "info": "F0FDFA",     # Cyan Tint
        "warning": "FEF3C7",  # Amber
        "tip": "ECFDF5",      # Emerald
        "navy": "0B1120"      # Midnight Dark
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
        if alert_type == "navy":
            r_title.font.color.rgb = RGBColor(0, 240, 249) # Cyan
        else:
            r_title.font.color.rgb = RGBColor(15, 118, 110)
            
    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(9.5)
    if alert_type == "navy":
        r_text.font.color.rgb = RGBColor(241, 245, 249)
    else:
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
    r = p_hdr.add_run("RADIX Talent Match Hackathon • Official 30-Minute Master Video Pitch\n")
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(107, 114, 128)
    
    p_title = doc.add_paragraph()
    r_main = p_title.add_run("GapMap: 30-Minute Master Pitch Script\n")
    r_main.font.size = Pt(22)
    r_main.font.bold = True
    r_main.font.color.rgb = RGBColor(11, 17, 32)
    
    r_sub = p_title.add_run("Seamless Integration of Your Attached 10-Slide Deck, GitHub Architecture Flowcharts & Live Software Demo")
    r_sub.font.size = Pt(12.5)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(0, 168, 180)
    
    add_callout(doc, 
        "Production & Recording Architecture:\n"
        "• Aesthetic & Visuals: Powered directly by your attached 10-slide PowerPoint ('GapMap Hackathon Pitch.pptx').\n"
        "• Engineering Proof: Showcases the GitHub repository (README.md flowcharts, 135 passing tests badge, and CI pipeline).\n"
        "• Interactive Proof: Complete live software demonstration on http://localhost:5173 across all 5 modules.\n"
        "• Language Style: Simple, conversational, easy-to-pronounce English tailored for smooth pacing across exactly 30 minutes.\n"
        "• Team Distribution: All 5 members present their respective modules with natural transitions.",
        title="EXECUTIVE OVERVIEW FOR TEAM GAPMAP",
        alert_type="info"
    )

    # Master Team Roster Table
    p_team_hdr = doc.add_paragraph()
    r = p_team_hdr.add_run("30-Minute Sequence & Speaker Allocation Table")
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor(11, 17, 32)
    
    t_team = doc.add_table(rows=1, cols=4)
    t_team.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_w = [1.2, 1.8, 1.3, 2.7]
    add_header_styled_row(t_team, ["Time", "Presenter", "Assigned Role", "Screen Segment & Focus"], c_w)
    
    roster_rows = [
        ("00:00 – 04:30 (4.5m)", "Aarush (Lead)", "Scrum Master", "SLIDES 1 to 4: Hook, The Keyword Lottery & Stuffing Cheat, The Solution & 5-Stage Pipeline."),
        ("04:30 – 07:30 (3.0m)", "Samiksha", "Role 1: JD Analytics", "SLIDES 5 & 6: The 8 TalenciaGlobal Systems (01-08) Architecture Deep Dive."),
        ("07:30 – 10:00 (2.5m)", "Aarush", "Scrum Master", "GITHUB REPOSITORY: README.md Flowcharts, 135 Tests Passing Badge, Pydantic Contract, CI/CD."),
        ("10:00 – 12:30 (2.5m)", "Samiksha", "Role 1: JD Analytics", "LIVE APP DEMO: Stage 1 (JD Analytics) with Google SWE JD, Dual LLM extraction, SHA-256 Cache."),
        ("12:30 – 16:00 (3.5m)", "Arushi", "Role 2: Resume Parsing", "LIVE APP DEMO: Stage 2 (Resume Parsing), PII scrubbing, Evidence quote drawer, Anti-Stuffing penalty."),
        ("16:00 – 18:00 (2.0m)", "Aarush", "Role 3: Profile Contract", "LIVE APP DEMO: Stage 3 (Profile Contract), Pydantic v2 model, Supabase sync + offline JSON failover, Audit logs."),
        ("18:00 – 20:30 (2.5m)", "Aditya", "Role 4: Talent Check", "LIVE APP DEMO: Stage 4 (Talent Check), 12 categories, Google bar, Live What-If Slider Score Deltas."),
        ("20:30 – 23:00 (2.5m)", "Anjali", "Role 5: Skill Matching", "LIVE APP DEMO: Stage 5 (Skill Matching), 3-Layer Math Waterfall, Prerequisite Graph, 4x6 Heatmap."),
        ("23:00 – 24:30 (1.5m)", "Arushi", "Role 2: Resume Parsing", "SLIDE 7: Core Innovation 1 (Proof-Backed Skills & Anti-Stuffing Engine Architecture)."),
        ("24:30 – 26:00 (1.5m)", "Aditya", "Role 4: Talent Check", "SLIDE 8: Core Innovation 2 (What-If Readiness Simulator & Mathematical Formula)."),
        ("26:00 – 27:30 (1.5m)", "Anjali", "Role 5: Skill Matching", "SLIDE 9: Core Innovation 3 (3-Layer Matching Model & 4x6 Heatmap Matrix Breakdown)."),
        ("27:30 – 30:00 (2.5m)", "Aarush", "Scrum Master Wrap-Up", "SLIDE 10: Technical Architecture, 135/135 Test Suite, Definition of Done, and Closing Pitch.")
    ]
    for r_data in roster_rows:
        row = t_team.add_row()
        for i, val in enumerate(r_data):
            row.cells[i].text = val
            set_cell_background(row.cells[i], "F8FAFC" if i % 2 == 0 else "FFFFFF")
            set_cell_margins(row.cells[i], top=70, bottom=70, left=100, right=100)
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
        "1. Open Presentation: Open 'GapMap Hackathon Pitch.pptx' in PowerPoint.\n"
        "2. Open GitHub Tab: Open your GitHub repository (https://github.com/aarushgoel025/GapMap) showing the README.md.\n"
        "3. Open Web App: Ensure backend server (port 8000) and frontend (port 5173) are running -> open http://localhost:5173.\n"
        "4. Ready Files Folder: Keep desktop folder open with:\n"
        "   • Google LLC - Software Engineer.pdf\n"
        "   • candidate_4_systems_engineer.pdf (Marcus Vance - for anti-stuffing penalty demo)\n"
        "   • aarush_sharma_cv.pdf (or candidate_1_all_rounder.pdf)",
        title="3-SCREEN SETUP CHECKLIST BEFORE RECORDING",
        alert_type="warning"
    )

    doc.add_page_break()

    s_widths = [2.5, 4.5]

    # ========================================================
    # ACT 1: PRESENTATION SLIDES (00:00 - 07:30)
    # ========================================================
    p_act = doc.add_paragraph()
    r = p_act.add_run("Act 1: Setting the Foundation (Slides 1 to 6)\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(11, 17, 32)
    
    r_meta = p_act.add_run("Time: 00:00 – 07:30 | Presentation Deck: GapMap Hackathon Pitch.pptx")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(107, 114, 128)
    
    t_act1 = doc.add_table(rows=1, cols=2)
    t_act1.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_styled_row(t_act1, ["Time & On-Screen Action", "Speaker & Spoken Script"], s_widths)

    add_script_row(t_act1,
        "TIME: 00:00 – 01:30\n\n"
        "ON SCREEN:\n"
        "Slide 1 (Cover Slide):\n"
        "• Title: 'GapMap: Know your gap. Prove your skills.'\n"
        "• Subtitle: 'Next-Gen Evidence-Driven ATS & 3-Layer Skill Gap Analytics'\n"
        "• Badges: SKILL SIGNALS | ROLE READINESS | GAP INTELLIGENCE\n\n"
        "ACTION:\n"
        "Full screen display of Slide 1. Aarush opens with confident, clear delivery.",
        "SPEAKER: Aarush (Lead / Scrum Master)\n\n"
        "\"Good afternoon, respected judges, mentors, and fellow engineers. Welcome to our final presentation of Team GapMap for the RADIX Talent Match Hackathon.\n\n"
        "My name is Aarush, and I am the Scrum Master for our team. Today, I am joined by my four teammates: Samiksha, Arushi, Aditya, and Anjali. Together, we built GapMap. Our guiding motto is right here on our opening slide: 'Know your gap. Prove your skills.'\n\n"
        "Over the next 30 minutes, we are going to show you why traditional hiring software is broken, walk you through the engineering architecture on GitHub that solves it, demonstrate our live software running end-to-end, and prove how GapMap turns hiring from an opaque guessing game into a fair, evidence-based science.\"",
        bg_color="F8FAFC", col_widths=s_widths
    )

    add_script_row(t_act1,
        "TIME: 01:30 – 03:00\n\n"
        "ON SCREEN:\n"
        "Transition to Slide 2:\n"
        "'The Problem with Traditional ATS'\n"
        "• Point to the graphic: 'KEYWORD LOTTERY' (Networking vs Computer Networks).\n"
        "• Point to 'STUFFING CHEAT' (Expert, Advanced, Certified buzzwords).\n"
        "• Point to 'BLACK BOX' (No feedback to candidates).\n\n"
        "ACTION:\n"
        "Use mouse cursor to highlight the Keyword Lottery and Stuffing Cheat columns.",
        "SPEAKER: Aarush (Lead / Scrum Master)\n\n"
        "\"Let us start with Slide 2: The real problem with modern hiring.\n\n"
        "Today, over 75% of qualified engineering candidates are rejected by Applicant Tracking Systems before a human recruiter ever sees their resume. Why? Because existing ATS software acts like a keyword lottery.\n\n"
        "As you see on the left of this slide, if a company asks for 'Computer Networks' and an applicant writes 'Networking' or 'LAN Administration', the legacy ATS rejects them simply because the exact words do not match. Qualified candidates get filtered out for valid synonyms.\n\n"
        "Even worse is what you see in the middle: 'The Stuffing Cheat.' Applicants quickly learn that legacy ATS systems are naive. They copy 50 buzzwords—Expert, Advanced, Leadership, Docker, Kubernetes—into their resume summary or hidden text. The ATS sees those words, checks the box, and moves them forward, even if they never wrote a single line of code in those tools.\n\n"
        "And on the right is 'The Black Box': rejected candidates get generic rejection emails. They never learn why they failed or what skills they need to improve. It wastes talent and increases hiring risk for companies.\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    add_script_row(t_act1,
        "TIME: 03:00 – 04:30\n\n"
        "ON SCREEN:\n"
        "Transition to Slide 3 & Slide 4:\n"
        "• Slide 3: 'The GapMap Evidence-Driven Solution'\n"
        "  (Quote-backed extraction, Anti-cheat detection, 117+ corporate bars, Learning path: Linux -> Docker -> Kubernetes).\n"
        "• Slide 4: 'The 5-Stage End-to-End Pipeline'\n"
        "  (1. JD Analytics -> 2. Resume Parsing -> 3. Profile Contract -> 4. Talent Check -> 5. Skill Matching).\n\n"
        "ACTION:\n"
        "Show Slide 3 briefly, then move to Slide 4 to outline the 5 pipeline stages.",
        "SPEAKER: Aarush (Lead / Scrum Master)\n\n"
        "\"Slide 3 and Slide 4 show how GapMap solves this.\n\n"
        "Instead of counting keywords, GapMap is an evidence engine. Every skill must be backed by a verbatim sentence quote from the resume. If someone claims a skill without project proof, our anti-stuffing detector cuts their score credit in half. We benchmark candidates against 117+ corporate hiring bars, and we build sequential learning paths—telling you to learn Linux before Docker, and Docker before Kubernetes.\n\n"
        "To make this work reliably, look at Slide 4. We built a 5-stage automated pipeline:\n"
        "Stage 1 analyzes the Job Description and separates Must-Have skills from Nice-to-Have skills.\n"
        "Stage 2 parses the resume, scrubs private contact info, pulls proof quotes, and checks for keyword stuffing.\n"
        "Stage 3 creates our unified Profile Contract, saved with database and offline storage.\n"
        "Stage 4 benchmarks the candidate against corporate hiring bars with our live What-If simulator.\n"
        "And Stage 5 performs 3-layer matching and builds the prerequisite learning roadmap.\n\n"
        "Now, to explain the 8 Talencia systems that power this pipeline under the hood, I will hand over to Samiksha.\"",
        bg_color="F8FAFC", col_widths=s_widths
    )

    add_script_row(t_act1,
        "TIME: 04:30 – 07:30\n\n"
        "ON SCREEN:\n"
        "Transition to Slide 5 & Slide 6:\n"
        "'The 8 Talencia Global Systems'\n"
        "• Slide 5: Systems 01 to 04 (Parameter Discovery, Database Normalization, Test Automation, Agentic Research).\n"
        "• Slide 6: Systems 05 to 08 (Agentic Ecosystem, DevOps & Cloud, Vector DBs, Enterprise Governance).\n\n"
        "ACTION:\n"
        "Samiksha presents clearly, pointing to each numbered system card on the slides.",
        "SPEAKER: Samiksha (Role 1 — JD Analytics)\n\n"
        "\"Thank you, Aarush. Hello everyone, I am Samiksha.\n\n"
        "On Slides 5 and 6, you see the 8 Talencia Global Systems that form our engineering foundation. We made sure that every single one of these systems is actively running in our codebase:\n\n"
        "System 01 is Parameter Discovery. We standardized all engineering skills into 12 core category codes—like Coding, Cloud, and Databases—so there is zero ambiguity between a job description and a resume.\n\n"
        "System 02 is Database Normalization. We use a 3NF relational schema in Supabase PostgreSQL, paired with an automatic local JSON fallback so the app works 100% offline.\n\n"
        "System 03 is Test Automation. We wrote 135 automated pytest tests that pass in just 7.3 seconds with a 100% pass rate.\n\n"
        "System 04 is Agentic Research. Instead of trusting one AI, we query Google Gemini 2.5 and Mistral in parallel and audit any disagreements.\n\n"
        "Moving to Slide 6:\n"
        "System 05 is our Agentic Ecosystem, using Pydantic v2 schemas with a self-correcting retry loop if an AI produces malformed data.\n\n"
        "System 06 is DevOps and Cloud Architecture, containerized with Docker multi-stage builds and automated by GitHub Actions.\n\n"
        "System 07 is Vector Databases and ML, using local 256-dimensional embeddings for fast cosine similarity without external API costs.\n\n"
        "And System 08 is Enterprise Architecture and Governance, featuring automatic PII scrubbing, keyword stuffing detection, and a Section F audit trail.\n\n"
        "Now, to see these systems directly in our code and repository flowcharts, Aarush will show our GitHub repository.\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    doc.add_page_break()

    # ========================================================
    # ACT 2: GITHUB REPO & FLOWCHARTS (07:30 - 10:00)
    # ========================================================
    p_act = doc.add_paragraph()
    r = p_act.add_run("Act 2: GitHub Architecture & Engineering Governance\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(11, 17, 32)
    
    r_meta = p_act.add_run("Time: 07:30 – 10:00 | Screen: GitHub Repository (README.md & Flowcharts)")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(107, 114, 128)
    
    t_act2 = doc.add_table(rows=1, cols=2)
    t_act2.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_styled_row(t_act2, ["Time & On-Screen Action", "Speaker & Spoken Script"], s_widths)

    add_script_row(t_act2,
        "TIME: 07:30 – 10:00\n\n"
        "ON SCREEN:\n"
        "Switch Screen to Browser: GitHub Repository\n"
        "URL: https://github.com/aarushgoel025/GapMap\n"
        "• Top README Badges visible:\n"
        "  - 'pytest: 135 passed (emerald)'\n"
        "  - 'python: 3.11 | 3.14'\n"
        "  - 'React 19.3' & 'FastAPI'\n"
        "• Scroll down to 'End-to-End 5-Stage Pipeline' Mermaid flowchart diagram.\n"
        "• Scroll briefly to 'shared/schemas.py' showing Pydantic models.\n\n"
        "ACTION:\n"
        "Point cursor to the 135 passing tests badge, then trace the Mermaid diagram.",
        "SPEAKER: Aarush (Lead / Scrum Master)\n\n"
        "\"Thank you, Samiksha. Now we switch our screen to our live GitHub repository at github.com/aarushgoel025/GapMap.\n\n"
        "Right at the top of our README, you can see our verified badges: 135 automated pytest tests passing, built on Python 3.14 and FastAPI on the backend, and React 19 with TypeScript on the frontend.\n\n"
        "Look at this architecture flowchart in our README. This diagram shows how data flows across our five stages and our trust layer:\n"
        "When a Job Description enters Stage 1, it connects to our SHA-256 cache. When a resume enters Stage 2, it redacts PII and logs to our Section F audit logger. When the profile is built in Stage 3, it saves to our 3NF database with local JSON backup. In Stage 4, Talent Check queries our 117 corporate benchmarks. And in Stage 5, our matching engine uses our local vector index.\n\n"
        "Notice our contract-first design: before writing a single endpoint, we locked down our data models in `shared/schemas.py`. This meant all five team members could build their modules simultaneously without breaking changes.\n\n"
        "Now, let us move from GitHub to the actual running application. Samiksha will take us into Stage 1 on our live web platform.\"",
        bg_color="F8FAFC", col_widths=s_widths
    )

    doc.add_page_break()

    # ========================================================
    # ACT 3: LIVE SOFTWARE DEMO (10:00 - 23:00)
    # ========================================================
    p_act = doc.add_paragraph()
    r = p_act.add_run("Act 3: Live End-to-End Product Demonstration\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(11, 17, 32)
    
    r_meta = p_act.add_run("Time: 10:00 – 23:00 | Screen: Live Web App (http://localhost:5173)")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(107, 114, 128)
    
    t_act3 = doc.add_table(rows=1, cols=2)
    t_act3.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_styled_row(t_act3, ["Time & On-Screen Action", "Speaker & Spoken Script"], s_widths)

    add_script_row(t_act3,
        "TIME: 10:00 – 12:30\n\n"
        "ON SCREEN:\n"
        "Switch to Browser: http://localhost:5173\n"
        "Stage 1: Job Description Analytics\n"
        "• Click 'Launch Pipeline (Step 1: Upload JD)'.\n"
        "• Select file: 'Google LLC - Software Engineer.pdf'.\n"
        "• Click 'Analyze Job Description'.\n"
        "• Table loads in ~1.2s.\n"
        "• Point to:\n"
        "  - Category Codes (COD, DSA, SWE, CLOUD)\n"
        "  - Importance Column ('Must-Have' vs 'Nice-to-Have')\n"
        "  - Consensus Badge (Gemini + Mistral Agree)\n"
        "  - SHA-256 Cache badge.\n\n"
        "ACTION:\n"
        "Hover over the 'Must-Have' tags and consensus indicators.",
        "SPEAKER: Samiksha (Role 1 — JD Analytics)\n\n"
        "\"Here we are on our live GapMap application running on port 5173. Let us click 'Launch Pipeline' to start Stage 1: Job Description Analytics.\n\n"
        "I am uploading the official Google Software Engineer Job Description. When I click 'Analyze Job Description', watch how fast it loads: in just 1.2 seconds, the full extraction is complete.\n\n"
        "This speed comes from our SHA-256 prompt cache. Because this job description was processed previously, GapMap recognizes its hash and instantly serves the verified payload.\n\n"
        "Now look at the extracted table:\n"
        "First, every skill is mapped to our 12 categories—like COD for Python, DSA for Algorithms, and CLOUD for Kubernetes.\n"
        "Second, look at the Importance column: core requirements like Python, C++, and System Design are marked as 'Must-Have', while auxiliary tools are marked 'Nice-to-Have'. In our downstream scoring engine, Must-Have skills receive double weight—a 2.0 multiplier. This ensures that missing a fundamental skill drops the score significantly, while missing a bonus tool does not disqualify a great candidate.\n\n"
        "Third, our multi-LLM consensus flag confirms that both Gemini 2.5 and Mistral agreed on these skills. Now that our target job requirements are extracted, Arushi will take us to Stage 2 to parse the candidate's resume.\"",
        bg_color="F8FAFC", col_widths=s_widths
    )

    add_script_row(t_act3,
        "TIME: 12:30 – 16:00\n\n"
        "ON SCREEN:\n"
        "Stage 2: Resume Parsing & Evidence Engine\n"
        "• Click 'Proceed to Step 2: Resume Parsing'.\n"
        "• Upload 'candidate_4_systems_engineer.pdf' (Marcus Vance).\n"
        "• Click 'Extract & Verify Resume'.\n"
        "• Point out Top Header: Phone, email, and address are masked as [REDACTED].\n"
        "• Click 'View Evidence' on 'Docker' -> drawer opens showing verbatim quote.\n"
        "• Scroll to 'Kubernetes' -> amber badge 'Keyword Stuffing Detected (50% Penalty Applied)'.\n\n"
        "ACTION:\n"
        "Highlight the quote box, then highlight the anti-stuffing penalty badge.",
        "SPEAKER: Arushi (Role 2 — Resume Parsing)\n\n"
        "\"Thank you, Samiksha. Welcome to Stage 2: Resume Parsing and our Evidence Engine.\n\n"
        "I am uploading candidate Marcus Vance. The first thing you see at the top of the screen is our automatic PII scrubber in action: Marcus's telephone number, private email, and home address are completely masked before any AI processing, satisfying enterprise privacy rules.\n\n"
        "Now, let us demonstrate our core motto: 'Do not just claim it. Prove it.'\n\n"
        "When I click on 'Docker', look at the Evidence Drawer that opens on the right. GapMap extracts the verbatim sentence directly from Marcus's resume: *'Containerized 4 microservices with Docker Compose and managed CI/CD pipelines.'* Because this skill has real project evidence, our engine assigns it High Confidence and verifies it.\n\n"
        "Now look at what happens with 'Kubernetes' and 'GraphQL'. Marcus listed these skills in his top summary list to pass keyword filters. But our anti-stuffing regex audited his actual job history and project details and found zero practical mentions. \n\n"
        "Notice what GapMap does: it immediately flags `stuffing_flag = True`, displays an amber warning badge, lowers the confidence to Low, and cuts its score credit by 50%. Honest candidates who actually built projects are protected, while keyword-stuffers are penalized.\n\n"
        "Now, Aarush will show how this data forms our unified Profile Contract in Stage 3.\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    add_script_row(t_act3,
        "TIME: 16:00 – 18:00\n\n"
        "ON SCREEN:\n"
        "Stage 3: Profile Contract & Persistence\n"
        "• Click 'Proceed to Step 3: Candidate Profile'.\n"
        "• Form loads pre-filled with Name, Education, and Categorized Skills.\n"
        "• Make a quick inline edit: Adjust candidate level or add a certification.\n"
        "• Click 'Save Profile' -> green success toast appears.\n"
        "• Open Section F Audit Logs drawer on the right side of the screen.\n\n"
        "ACTION:\n"
        "Scroll through the timestamped audit log entries.",
        "SPEAKER: Aarush (Lead / Scrum Master)\n\n"
        "\"Thank you, Arushi. Welcome to Stage 3: The Profile Builder.\n\n"
        "Here on screen, all parsed information is structured into our unified Pydantic v2 `Profile` schema. An applicant can review their parsed profile, verify their education, and make adjustments. If I want to update an estimated level or add a certification, I can edit it directly in the UI.\n\n"
        "When I click 'Save Profile', watch what happens behind the scenes: the record is validated and saved to our Supabase PostgreSQL relational database. But if the network ever drops during an interview or demo, our backend automatically falls back to local JSON persistence in `backend/data/profiles/`. It is 100% resilient and will never fail due to connection issues.\n\n"
        "Furthermore, look at the Section F Audit Trail drawer on the right. Every single profile modification, scoring run, and timestamp is immutably logged for complete compliance.\n\n"
        "Now that we have a structured candidate profile, the big question is: Are they ready for the corporate hiring bar? Aditya will show Stage 4.\"",
        bg_color="F8FAFC", col_widths=s_widths
    )

    add_script_row(t_act3,
        "TIME: 18:00 – 20:30\n\n"
        "ON SCREEN:\n"
        "Stage 4: Talent Check & What-If Simulator\n"
        "• Click 'Proceed to Step 4: Talent Readiness Check'.\n"
        "• Select company: 'Google LLC'.\n"
        "• Readiness score ring shows 68.2% ('Almost there').\n"
        "• Show category breakdown bars (SQL & Cloud have gaps).\n"
        "• FOCUS ON WHAT-IF SLIDERS: Drag 'SQL and Databases' from Level 3 to Level 7.\n"
        "• Watch score ring recalculate live to 81.4%!\n"
        "• Status flips to green 'READY'!\n"
        "• Estimated weeks-to-ready drops from 12 weeks to 3 weeks!\n\n"
        "ACTION:\n"
        "Keep mouse on the slider to highlight live real-time reactivity.",
        "SPEAKER: Aditya (Role 4 — Talent Check)\n\n"
        "\"Thank you, Aarush. Hello everyone, I am Aditya.\n\n"
        "In Stage 4, we evaluate whether a candidate meets the hiring bar of over 117 top companies from our dataset. We selected Google LLC for our candidate Marcus. His baseline score is 68.2%, which categorizes him as 'Almost there.' In our engine, 'Ready' is strictly defined as reaching 80% or higher.\n\n"
        "Looking at the category bars, you can see why: Marcus is strong in Coding and Software Engineering, but has gaps in SQL Databases and Cloud Computing.\n\n"
        "Now look at our What-If Simulator in action. Suppose Marcus asks: *'What happens if I spend the next month mastering SQL and raise my level from 3 to 7?'*\n\n"
        "Watch the screen as I drag the SQL slider right now. As I move the slider from 3 to 7, the math recalculates in real-time: his readiness climbs from 68.2% to 81.4%! The badge instantly flips from yellow 'Almost there' to bright green 'READY'! And his estimated placement timeline drops from 12 weeks down to just 3 weeks.\n\n"
        "Candidates now have an exact, actionable roadmap to qualify. Now, Anjali will show Stage 5 to demonstrate our 3-layer job matching engine.\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    add_script_row(t_act3,
        "TIME: 20:30 – 23:00\n\n"
        "ON SCREEN:\n"
        "Stage 5: Skill Matching Engine & 4x6 Matrix\n"
        "• Click 'Proceed to Step 5: Skill Matching Engine'.\n"
        "• Match score card displays 76.0%.\n"
        "• Show Deterministic Scoring card with exact formula.\n"
        "• Expand Matched Skills table showing layer badges:\n"
        "  - Layer 1 Exact Match (1.0 credit)\n"
        "  - Layer 2 Alias Match (0.9 credit - PostgreSQL = SQL)\n"
        "  - Layer 3 Semantic Match (0.8xCos credit).\n"
        "• Scroll to Prerequisite Learning Plan: Docker is #1 before Kubernetes.\n"
        "• Click 'View 4x6 Candidate Fit Heatmap Matrix'.\n\n"
        "ACTION:\n"
        "Point cursor across the varied scores in the 4x6 matrix.",
        "SPEAKER: Anjali (Role 5 — Skill Matching)\n\n"
        "\"Thank you, Aditya. Hello everyone, I am Anjali.\n\n"
        "In Stage 5, we compare the candidate's profile against the target Job Description using our Explainable 3-Layer Matching algorithm:\n"
        "$$\\text{Match Score} = 100 \\times \\frac{\\sum (w_i \\cdot c_i)}{\\sum w_i}$$\n"
        "We never ask an LLM to guess a score. Look at our Matched Skills table:\n"
        "Python matched through Layer 1 Exact Match for full 1.0 credit. PostgreSQL matched through Layer 2 Alias Match for 0.9 credit, recognizing it as a SQL database. And Distributed Systems matched through Layer 3 Semantic Cosine Similarity for 0.8 credit using our local vector embeddings.\n\n"
        "Now look at the Missing Skills roadmap below. We don't just dump an alphabetical list. Using Kahn's topological sort algorithm, GapMap orders missing skills by prerequisites: it tells Marcus to learn Docker before attempting Kubernetes, and lists the exact point impact each skill adds.\n\n"
        "Finally, look at our 4x6 Candidate Heatmap Matrix. We ran four different candidates across six corporate roles. Alex Chen scores 83.3% on Google SWE, but only 40.8% on Cloud Architect, while Sofia Rodriguez scores 86.7% on Data Engineer. This proves GapMap provides true, candidate-specific differentiation.\n\n"
        "Now, we will return to our presentation slides for our architectural deep dive and closing summary.\"",
        bg_color="F8FAFC", col_widths=s_widths
    )

    doc.add_page_break()

    # ========================================================
    # ACT 4: DEEP DIVE SLIDES & CLOSING (23:00 - 30:00)
    # ========================================================
    p_act = doc.add_paragraph()
    r = p_act.add_run("Act 4: Technical Deep Dive & Closing (Slides 7 to 10)\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(11, 17, 32)
    
    r_meta = p_act.add_run("Time: 23:00 – 30:00 | Screen: Presentation Slides 7, 8, 9, 10 & Wrap-Up")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(107, 114, 128)
    
    t_act4 = doc.add_table(rows=1, cols=2)
    t_act4.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_styled_row(t_act4, ["Time & On-Screen Action", "Speaker & Spoken Script"], s_widths)

    add_script_row(t_act4,
        "TIME: 23:00 – 24:30\n\n"
        "ON SCREEN:\n"
        "Switch back to Presentation Slides:\n"
        "Slide 7: 'Core Innovation 1: Proof-Backed Skills & Anti-Stuffing Engine'\n"
        "• Highlight the 4 horizontal steps:\n"
        "  1. Skill Extraction (Python, SQL)\n"
        "  2. Verbatim Evidence ('Built ETL pipelines using Python and SQL')\n"
        "  3. Anti-Stuffing Checks (Word-boundary regex \\b prevents false matches)\n"
        "  4. GitHub Verification (public repo code confirmation).\n\n"
        "ACTION:\n"
        "Arushi walks through the 4 steps on the slide diagram.",
        "SPEAKER: Arushi (Role 2 — Resume Parsing)\n\n"
        "\"Now let us review our technical innovations on our slides.\n\n"
        "Slide 7 summarizes our Proof-Backed Skills and Anti-Stuffing Engine. In Step 1, skills are extracted from the text. In Step 2, each skill is anchored to the exact sentence where it appears. In Step 3, strict word-boundary regular expressions prevent false positives—for example, making sure the programming language 'Go' is not falsely matched inside the word 'Google' or 'Going'.\n\n"
        "And in Step 4, our optional GitHub integration checks public repositories to confirm actual code usage. This creates an evidence chain that recruiters can trust completely.\"",
        bg_color="F8FAFC", col_widths=s_widths
    )

    add_script_row(t_act4,
        "TIME: 24:30 – 26:00\n\n"
        "ON SCREEN:\n"
        "Transition to Slide 8:\n"
        "'Core Innovation 2: What-If Readiness Simulator'\n"
        "• Point to the graphic:\n"
        "  - Skill Level Tuning Sliders (Computer Networks, Advanced, Proficient)\n"
        "  - Readiness Score Ring (72% Good Match)\n"
        "  - Weeks-to-Ready card (14 weeks to meet Google hiring bar).\n\n"
        "ACTION:\n"
        "Aditya explains the math and visual structure of the simulator.",
        "SPEAKER: Aditya (Role 4 — Talent Check)\n\n"
        "\"Slide 8 highlights our What-If Readiness Simulator.\n\n"
        "As we saw in the live demo, our mathematical scoring compares candidate competency levels against company benchmarks across our 12 categories. By calculating the score delta dynamically, the simulator shows candidates exactly which skills add the most points and how many weeks of preparation are required.\n\n"
        "This transforms a static rejection into an actionable career growth plan.\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    add_script_row(t_act4,
        "TIME: 26:00 – 27:30\n\n"
        "ON SCREEN:\n"
        "Transition to Slide 9:\n"
        "'Core Innovation 3: 3-Layer Matching Model & 4x6 Heatmap Matrix'\n"
        "• Highlight the 3 Layer tiers: Exact (1.0), Alias (0.9), Semantic (0.8xCos).\n"
        "• Point to the 4x6 Heatmap Matrix table on the right side of the slide.\n\n"
        "ACTION:\n"
        "Anjali summarizes the explainability and matrix variance.",
        "SPEAKER: Anjali (Role 5 — Skill Matching)\n\n"
        "\"Slide 9 details our 3-Layer Matching Architecture.\n\n"
        "By enforcing Exact matching at 1.0, Alias matching at 0.9, and Semantic vector matching at 0.8, our system handles synonyms like 'Networking' versus 'Computer Networks' with complete mathematical explainability.\n\n"
        "And our 4x6 Heatmap Matrix proves that our scores reflect genuine candidate strengths rather than arbitrary grading.\"",
        bg_color="F8FAFC", col_widths=s_widths
    )

    add_script_row(t_act4,
        "TIME: 27:30 – 30:00\n\n"
        "ON SCREEN:\n"
        "Transition to Slide 10 (Closing Slide):\n"
        "'Technical Architecture & Impact Summary'\n"
        "• Show the 4 pillars: Frontend (React 19), Backend (Python 3.14/FastAPI), AI & Data (Gemini + Mistral + Supabase), Infrastructure (Docker).\n"
        "• Highlight the impact callout:\n"
        "  - 135/135 pytest tests passing in 7.3s (100% pass rate)\n"
        "  - 117+ corporate hiring bars covered\n"
        "  - Zero single-points-of-failure.\n\n"
        "ACTION:\n"
        "Aarush delivers the final closing statement with conviction.",
        "SPEAKER: Aarush (Lead / Scrum Master)\n\n"
        "\"Finally, Slide 10 summarizes our technical architecture and impact.\n\n"
        "GapMap is built for zero single-points-of-failure. With React 19, FastAPI, dual-LLM consensus, and Supabase with offline JSON fallback, our tool is resilient, scalable, and production-ready.\n\n"
        "In our testing, we verified an extraction precision of 93.0% and a recall of 96.8% on ground truth data. All 135 automated pytest tests pass in 7.3 seconds. And we have fulfilled 100% of the hackathon Definition of Done.\n\n"
        "GapMap eliminates the ATS keyword lottery. We verify real proof, penalize keyword stuffing, benchmark true corporate readiness, and give every candidate an actionable path to become ready for their dream job.\n\n"
        "Thank you so much for your time. We are Team GapMap, and we are now delighted to answer your questions!\"",
        bg_color="FFFFFF", col_widths=s_widths
    )

    doc.add_page_break()

    # ==========================================
    # APPENDIX: TOP 5 JUDGE Q&A DEFENSES
    # ==========================================
    p_sec = doc.add_paragraph()
    r = p_sec.add_run("Appendix: Top 5 Anticipated Judge Q&A Defenses\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(11, 17, 32)
    
    r_meta = p_sec.add_run("Quick-reference guide for the team to handle tough technical questions during the live jury evaluation.")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(107, 114, 128)
    
    qa_list = [
        ("Q1: Why did you build your own 3-layer matching math instead of letting an LLM calculate the match score?",
         "Defense (Anjali / Aarush): Because LLMs are non-deterministic and suffer from numerical hallucination. If you prompt an LLM five times with the same resume and JD, you can get scores varying between 65% and 85%. That is catastrophic for fairness and legal compliance. In GapMap, we use LLMs solely for semantic extraction, and we delegate 100% of the scoring to deterministic mathematical formulas: Exact (1.0), Alias (0.9), and Semantic Cosine (0.8 x Cos). It is 100% reproducible and explainable."),
        ("Q2: How exactly does your anti-stuffing detector work without flagging legitimate short skill names like 'Go' or 'C'?",
         "Defense (Arushi): A naive substring regex searching for 'Go' will match 'Google' or 'Going'. We implemented strict word-boundary tokenization (\\bGo\\b) combined with section-aware contextual parsing. Furthermore, GapMap checks whether the skill appears in the candidate's actual narrative—under professional experience or projects—alongside an action verb. If 'Go' only appears in an isolated header comma-separated list without project reference, our system flags stuffing_flag: True and applies STUFFING_PENALTY = 0.5, halving its scoring credit."),
        ("Q3: What happens if Gemini or Mistral goes down, or if evaluators test your code offline without API keys?",
         "Defense (Samiksha / Aarush): GapMap is engineered with zero single points of failure. First, we use a dual-LLM parallel consensus architecture with fallback triggers. Second, our SHA-256 prompt cache instantly serves previously analyzed documents without making a network call. Third, if API keys are absent or the system is completely offline, our backend automatically activates built-in deterministic mock fallbacks based on our pre-seeded ground-truth fixtures in backend/data/. The app never crashes, and evaluators can verify the entire flow offline."),
        ("Q4: How did you establish the corporate hiring benchmarks for 117+ companies?",
         "Defense (Aditya): Our dataset in talent_check_company_skillsets.json standardizes corporate hiring bars across 12 distinct domains—such as Coding, System Design, Cloud, and Data Structures. Each company tier reflects calibrated competency levels (from 1 to 10) based on verified industry technical interview rubrics. For example, Google and Amazon require level 8 to 9 in System Design and DSA for L5 roles, while specialized enterprise firms like Oracle emphasize high SQL and Application Support. Our Talent Check engine evaluates the gap against these exact numeric targets."),
        ("Q5: How does your system protect candidate privacy and comply with enterprise data governance?",
         "Defense (Aarush / Arushi): Enterprise governance was built in from Day 1 as System 08 of our Talencia architecture. Before any resume text is sent to an LLM or stored, our regex PII scrubber strips phone numbers, email addresses, and physical locations. All database operations are logged with timestamps in our Section F audit trail, and candidate GitHub verification is strictly opt-in using public repository metadata without accessing private code.")
    ]
    
    t_qa = doc.add_table(rows=1, cols=2)
    t_qa.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_styled_row(t_qa, ["Question", "Recommended Speaker & Bulletproof Technical Defense"], [2.2, 4.8])
    for q, ans in qa_list:
        row = t_qa.add_row()
        row.cells[0].text = q
        row.cells[1].text = ans
        set_cell_background(row.cells[0], "F8FAFC")
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
    out_path = r"c:\Users\Aarush\OneDrive\Desktop\GapMap\GapMap_30Min_Seamless_Demo_Script.docx"
    doc.save(out_path)
    print(f"Document successfully created at {out_path}")

if __name__ == "__main__":
    build_complete_document()

