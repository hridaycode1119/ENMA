import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs('docs/figures/flowcharts', exist_ok=True)

def get_font(size=20, bold=False):
    # Try standard system truetype fonts
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_rounded_box(draw, xy, fill, outline, width=2, radius=12):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=int(width))

def draw_arrow(draw, start, end, fill='#475569', width=3, arrow_size=12, label=""):
    x1, y1 = start
    x2, y2 = end
    draw.line([x1, y1, x2, y2], fill=fill, width=int(width))
    
    # Arrow head
    if x1 == x2: # Vertical
        if y2 > y1: # Downward
            draw.polygon([(x2, y2), (x2 - arrow_size, y2 - arrow_size * 1.5), (x2 + arrow_size, y2 - arrow_size * 1.5)], fill=fill)
        else: # Upward
            draw.polygon([(x2, y2), (x2 - arrow_size, y2 + arrow_size * 1.5), (x2 + arrow_size, y2 + arrow_size * 1.5)], fill=fill)
    elif y1 == y2: # Horizontal
        if x2 > x1: # Rightward
            draw.polygon([(x2, y2), (x2 - arrow_size * 1.5, y2 - arrow_size), (x2 - arrow_size * 1.5, y2 + arrow_size)], fill=fill)
        else: # Leftward
            draw.polygon([(x2, y2), (x2 + arrow_size * 1.5, y2 - arrow_size), (x2 + arrow_size * 1.5, y2 + arrow_size)], fill=fill)

    if label:
        font = get_font(15, bold=True)
        mid_x = (x1 + x2) // 2 + 10
        mid_y = (y1 + y2) // 2 - 10
        draw.text((mid_x, mid_y), label, fill='#0f172a', font=font)

def create_flowchart1_cognitive_loop():
    W, H = 1600, 950
    img = Image.new('RGB', (W, H), color='#ffffff')
    draw = ImageDraw.Draw(img)

    f_title = get_font(28, bold=True)
    f_sub = get_font(18, bold=False)
    f_box_h = get_font(18, bold=True)
    f_box_b = get_font(14, bold=False)

    # Title header banner
    draw_rounded_box(draw, [40, 30, W-40, 110], fill='#881337', outline='#4c0519', width=2, radius=14)
    draw.text((70, 48), "Flowchart 1: Cognitive Perception-Action Loop & Intent Disambiguation Engine", fill='#ffffff', font=f_title)
    draw.text((70, 82), "Deterministic Regex Pre-Filtering, Dual Semantic-Context Intent Scoring, and State Machine Routing", fill='#fecdd3', font=f_sub)

    # Box 1: Input
    draw_rounded_box(draw, [80, 160, 420, 290], fill='#f8fafc', outline='#94a3b8', width=3)
    draw.text((105, 175), "1. User Multimodal Input", fill='#881337', font=f_box_h)
    draw.text((105, 205), "• Natural Language Prompt\n• Real-Time Audio / Voice Input\n• Reactive UI Button Triggers", fill='#334155', font=f_box_b)

    # Arrow 1 -> 2
    draw_arrow(draw, (420, 225), (490, 225), fill='#881337', label="")

    # Box 2: Perception Pre-Filter
    draw_rounded_box(draw, [490, 160, 850, 290], fill='#fdf2f8', outline='#f43f5e', width=3)
    draw.text((515, 175), "2. Perception & Pre-Filter", fill='#9f1239', font=f_box_h)
    draw.text((515, 205), "• Temporal Regex (Date/Time)\n• Email Token Extractor\n• Team Member Entity Matching", fill='#334155', font=f_box_b)

    # Arrow 2 -> 3
    draw_arrow(draw, (850, 225), (920, 225), fill='#881337', label="")

    # Box 3: Dual Semantic Scoring
    draw_rounded_box(draw, [920, 160, 1520, 290], fill='#f0fdf4', outline='#22c55e', width=3)
    draw.text((945, 175), "3. Dual-Vector Intent Scoring (CAC-IP)", fill='#15803d', font=f_box_h)
    draw.text((945, 205), "• Score(I_k) = α · S_semantic(Q) + (1 - α) · S_context(H_t)\n• Candidate Ranking & Argmax Optimal Intent Resolution\n• Confidence Thresholding: Score(I*) ≥ Γ_threshold", fill='#1e293b', font=f_box_b)

    # Arrow from 3 Downward to Decision Diamond
    draw_arrow(draw, (1220, 290), (1220, 360), fill='#881337')

    # Decision Box
    draw_rounded_box(draw, [1020, 360, 1420, 470], fill='#fefce8', outline='#eab308', width=3)
    draw.text((1050, 380), "4. Confidence Threshold Check", fill='#854d0e', font=f_box_h)
    draw.text((1050, 410), "Is Score(I*) ≥ Γ_threshold\nand Schema Validated?", fill='#713f12', font=f_box_b)

    # Branch: NO (Leftward -> Clarification Modal)
    draw_arrow(draw, (1020, 415), (780, 415), fill='#e11d48', label="NO (< Γ)")
    draw_rounded_box(draw, [420, 360, 780, 470], fill='#fff1f2', outline='#e11d48', width=3)
    draw.text((445, 380), "Clarification & HITL Modal", fill='#be123c', font=f_box_h)
    draw.text((445, 410), "Prompt user to select candidate intent\nor refine missing parameters", fill='#475569', font=f_box_b)

    # Re-route from Clarification back to Orchestrator
    draw_arrow(draw, (600, 470), (600, 560), fill='#be123c')

    # Branch: YES (Downward -> Cognitive Orchestrator)
    draw_arrow(draw, (1220, 470), (1220, 560), fill='#15803d', label="YES (High Conf)")

    # Box 5: Cognitive Orchestrator Core
    draw_rounded_box(draw, [250, 560, 1450, 710], fill='#fdf4ff', outline='#a855f7', width=3)
    draw.text((280, 580), "5. Cognitive Orchestrator & State-Machine Core (DAG Plan Generator)", fill='#6b21a8', font=f_box_h)
    draw.text((280, 615), "• Maintains Global State Tuple S_t = <H_t, C_t, D_t, M_t> and Task Execution Sandbox\n• Binds Parameter Schema Models via Pydantic v2 Type Invariants\n• Generates Directed Acyclic Graph (DAG) of Specialized Functional Actions", fill='#334155', font=f_box_b)

    # Arrow Downward to Tool Execution Grid
    draw_arrow(draw, (850, 710), (850, 770), fill='#881337')

    # Box 6: Tool Execution Grid
    draw_rounded_box(draw, [80, 770, 400, 900], fill='#eff6ff', outline='#3b82f6', width=2)
    draw.text((100, 785), "Google Calendar v3", fill='#1d4ed8', font=f_box_h)
    draw.text((100, 815), "• Schedule Events\n• Conflict Resolution\n• Google Meet URL", fill='#334155', font=f_box_b)

    draw_rounded_box(draw, [440, 770, 760, 900], fill='#eff6ff', outline='#3b82f6', width=2)
    draw.text((460, 785), "Resend Email Studio", fill='#1d4ed8', font=f_box_h)
    draw.text((460, 815), "• LLM Body Generator\n• Recipient Auto-Suggest\n• Multi-Recipient Dispatch", fill='#334155', font=f_box_b)

    draw_rounded_box(draw, [800, 770, 1120, 900], fill='#eff6ff', outline='#3b82f6', width=2)
    draw.text((820, 785), "Document AST Studio", fill='#1d4ed8', font=f_box_h)
    draw.text((820, 815), "• PDF / DOCX / CSV\n• Tabular Grid Preservation\n• Semantic Transmutation", fill='#334155', font=f_box_b)

    draw_rounded_box(draw, [1160, 770, 1520, 900], fill='#eff6ff', outline='#3b82f6', width=2)
    draw.text((1180, 785), "Team Directory DB", fill='#1d4ed8', font=f_box_h)
    draw.text((1180, 815), "• Supabase PostgreSQL\n• Prefix Graph Search\n• 1-Click Action Triggers", fill='#334155', font=f_box_b)

    img.save('docs/figures/flowcharts/flowchart1_cognitive_loop.png')
    print("Saved flowchart 1")

def create_flowchart2_system_architecture():
    W, H = 1600, 950
    img = Image.new('RGB', (W, H), color='#ffffff')
    draw = ImageDraw.Draw(img)

    f_title = get_font(28, bold=True)
    f_sub = get_font(18, bold=False)
    f_box_h = get_font(18, bold=True)
    f_box_b = get_font(14, bold=False)

    # Title header banner
    draw_rounded_box(draw, [40, 30, W-40, 110], fill='#881337', outline='#4c0519', width=2, radius=14)
    draw.text((70, 48), "Flowchart 2: Four-Tier System Architecture & Communication Topology", fill='#ffffff', font=f_title)
    draw.text((70, 82), "Decoupled Layers for Perception, Cognitive Orchestration, Tool Execution, and Reactive Presentation", fill='#fecdd3', font=f_sub)

    # 4 Tier Horizontal Bands
    tiers = [
        ("Tier 1: Perception & Disambiguation", "#fdf2f8", "#f43f5e", [
            ("Multimodal Ingestion", "Raw Text, Voice Audio Streams, Reactive UI Clicks"),
            ("Regex Pre-Filtering", "Temporal Entity Extractor, Regex Patterns"),
            ("Semantic Intent Scorer", "Cosine Similarity against Enterprise Intent Embeddings"),
            ("Ambiguity Gate", "Human-in-the-Loop Clarification Dialog Trigger")
        ]),
        ("Tier 2: Cognitive Orchestration Core", "#fdf4ff", "#a855f7", [
            ("State Machine Engine", "Synchronizes State Tuple S_t = <H_t, C_t, D_t, M_t>"),
            ("DAG Execution Planner", "Decomposes Multi-Step Complex Goals into Action Graphs"),
            ("SH-EFC Fallback Controller", "Manages Exponential Backoff & Dynamic Error Repair"),
            ("Memory Sandboxing", "Zero-Data Retention Ephemeral Execution Context")
        ]),
        ("Tier 3: Action & Tool Registry Layer", "#eff6ff", "#3b82f6", [
            ("Pydantic v2 Type Registry", "Rust-Backed Schema Serialization & Strict Type Constraints"),
            ("Google Calendar API v3", "Bidirectional OAuth Event Creation & Conflict Detection"),
            ("Resend Email Studio", "Transactional Deliverability & Structured Tone Synthesis"),
            ("Document AST Parser", "Multi-Format Parser Factory (PDF, Word, Excel, CSV)")
        ]),
        ("Tier 4: Presentation & Synchronization Layer", "#fff1f2", "#e11d48", [
            ("Streamlit Reactive Engine", "Stateful UI Rendering with Zero-Flicker Session State"),
            ("Dark Wine Glassmorphic CSS", "Custom Theme Palette (#1a0b12 Canvas, #f43f76 Ruby)"),
            ("FastAPI Edge Microservice", "Asynchronous OpenAPI Endpoints for Serverless Edge (Vercel)"),
            ("Supabase PostgreSQL Store", "Relational Persistence for Roster, Events & Audit Trails")
        ])
    ]

    y_start = 140
    for idx, (tier_title, fill_c, border_c, boxes) in enumerate(tiers):
        y_top = y_start + idx * 195
        draw_rounded_box(draw, [60, y_top, W-60, y_top + 175], fill=fill_c, outline=border_c, width=2)
        draw.text((80, y_top + 12), tier_title, fill='#881337', font=f_box_h)

        # 4 Inner Boxes per Tier
        for b_idx, (b_title, b_desc) in enumerate(boxes):
            bx1 = 80 + b_idx * 360
            bx2 = bx1 + 330
            by1 = y_top + 45
            by2 = y_top + 155
            draw_rounded_box(draw, [bx1, by1, bx2, by2], fill='#ffffff', outline='#cbd5e1', width=2)
            draw.text((bx1 + 12, by1 + 12), b_title, fill='#0f172a', font=get_font(15, bold=True))
            draw.text((bx1 + 12, by1 + 42), b_desc, fill='#475569', font=get_font(12, bold=False))

    img.save('docs/figures/flowcharts/flowchart2_system_architecture.png')
    print("Saved flowchart 2")

def create_flowchart3_fallback_cascade():
    W, H = 1600, 950
    img = Image.new('RGB', (W, H), color='#ffffff')
    draw = ImageDraw.Draw(img)

    f_title = get_font(28, bold=True)
    f_sub = get_font(18, bold=False)
    f_box_h = get_font(18, bold=True)
    f_box_b = get_font(14, bold=False)

    # Title header banner
    draw_rounded_box(draw, [40, 30, W-40, 110], fill='#881337', outline='#4c0519', width=2, radius=14)
    draw.text((70, 48), "Flowchart 3: Self-Healing Execution & Fallback Cascade (SH-EFC)", fill='#ffffff', font=f_title)
    draw.text((70, 82), "Multi-Tier Fault Tolerance Guaranteeing Bounded Recovery from Upstream API and LLM Failures", fill='#fecdd3', font=f_sub)

    # Box 1: Inbound Tool Call
    draw_rounded_box(draw, [80, 160, 450, 270], fill='#f8fafc', outline='#64748b', width=3)
    draw.text((105, 175), "1. Tool Invocation Target", fill='#881337', font=f_box_h)
    draw.text((105, 205), "• Target: T_m (e.g. Google Calendar)\n• Raw Parameters: P*\n• Max Retries: R_max = 3", fill='#334155', font=f_box_b)

    draw_arrow(draw, (450, 215), (550, 215), fill='#881337')

    # Box 2: Pydantic Validation
    draw_rounded_box(draw, [550, 160, 950, 270], fill='#eff6ff', outline='#3b82f6', width=3)
    draw.text((575, 175), "2. Pydantic Schema Validation", fill='#1d4ed8', font=f_box_h)
    draw.text((575, 205), "• Check mandatory fields\n• Type coercion & date normalization\n• Reject corrupted payloads", fill='#334155', font=f_box_b)

    draw_arrow(draw, (950, 215), (1050, 215), fill='#881337')

    # Box 3: Primary API Execution
    draw_rounded_box(draw, [1050, 160, 1520, 270], fill='#f0fdf4', outline='#22c55e', width=3)
    draw.text((1075, 175), "3. Primary API Dispatch", fill='#15803d', font=f_box_h)
    draw.text((1075, 205), "• Direct HTTPS REST Request\n• OAuth Bearer Token Auth\n• Timeout Constraint: 3000ms", fill='#334155', font=f_box_b)

    # Outcome branch from Primary API
    draw_arrow(draw, (1285, 270), (1285, 360), fill='#881337')

    # Decision Diamond: Success vs Failure
    draw_rounded_box(draw, [1100, 360, 1470, 470], fill='#fefce8', outline='#eab308', width=3)
    draw.text((1125, 380), "4. Primary API Status?", fill='#854d0e', font=f_box_h)
    draw.text((1125, 410), "HTTP 200 OK vs Network / Auth / Rate-Limit Error", fill='#713f12', font=f_box_b)

    # YES branch -> Return Success
    draw_arrow(draw, (1470, 415), (1550, 415), fill='#15803d', label="OK")
    draw_rounded_box(draw, [1300, 560, 1550, 680], fill='#f0fdf4', outline='#16a34a', width=3)
    draw.text((1320, 580), "Success State", fill='#15803d', font=f_box_h)
    draw.text((1320, 610), "Return valid payload\nUpdate session state S_t", fill='#1e293b', font=f_box_b)
    draw_arrow(draw, (1425, 470), (1425, 560), fill='#15803d')

    # NO branch -> Self-Healing Cascade (Leftward)
    draw_arrow(draw, (1100, 415), (850, 415), fill='#dc2626', label="API Error")

    # Box 5: LLM Parameter Auto-Repair & Backoff
    draw_rounded_box(draw, [450, 360, 850, 470], fill='#fef2f2', outline='#ef4444', width=3)
    draw.text((475, 380), "5. Auto-Repair & Backoff", fill='#b91c1c', font=f_box_h)
    draw.text((475, 410), "• LLM repairs missing schema fields\n• Sleep(2^r) exponential backoff\n• Retry counter: r = r + 1", fill='#334155', font=f_box_b)

    # Arrow Downward to Deterministic Local Fallback Engine
    draw_arrow(draw, (650, 470), (650, 560), fill='#dc2626')

    # Box 6: Deterministic Local Fallback Engine
    draw_rounded_box(draw, [350, 560, 950, 710], fill='#fdf2f8', outline='#f43f5e', width=3)
    draw.text((375, 580), "6. Deterministic Local Fallback Engine (Zero-Failure Guarantee)", fill='#9f1239', font=f_box_h)
    draw.text((375, 615), "• Generates local mock reference ID (e.g. 'cal-evt-fallback-local')\n• Caches transaction in Supabase / SQLite offline queue\n• Dispatches success signal with fallback warning flag to UI", fill='#334155', font=f_box_b)

    # Final Convergence
    draw_arrow(draw, (650, 710), (650, 780), fill='#881337')
    draw_rounded_box(draw, [250, 780, 1050, 890], fill='#f8fafc', outline='#64748b', width=2)
    draw.text((280, 800), "7. User Notification & Non-Blocking State Resolution", fill='#0f172a', font=f_box_h)
    draw.text((280, 830), "• System logs complete trace with fallback indicator\n• UI displays operation confirmed without crashing or stalling session", fill='#475569', font=f_box_b)

    img.save('docs/figures/flowcharts/flowchart3_fallback_cascade.png')
    print("Saved flowchart 3")

def create_flowchart4_document_ast():
    W, H = 1600, 950
    img = Image.new('RGB', (W, H), color='#ffffff')
    draw = ImageDraw.Draw(img)

    f_title = get_font(28, bold=True)
    f_sub = get_font(18, bold=False)
    f_box_h = get_font(18, bold=True)
    f_box_b = get_font(14, bold=False)

    # Title header banner
    draw_rounded_box(draw, [40, 30, W-40, 110], fill='#881337', outline='#4c0519', width=2, radius=14)
    draw.text((70, 48), "Flowchart 4: Multimodal Document AST Ingestion & In-Memory Transmutation", fill='#ffffff', font=f_title)
    draw.text((70, 82), "Preserving Tabular Topologies, Hierarchy Trees, and Executing Deterministic In-Memory Rewrites", fill='#fecdd3', font=f_sub)

    # Ingestion Sources
    formats = [
        ("PDF Documents", "PyPDF Stream Ingestion\nExtract Page Geometries"),
        ("Word Files (.docx)", "python-docx Stream\nExtract Paragraph Trees"),
        ("Excel & CSV Data", "Pandas Tabular Matrix\nPreserve Cell Coordinates"),
        ("Markdown / Text", "UTF-8 Stream Tokenizer\nPreserve Code & Headers")
    ]

    for idx, (f_name, f_desc) in enumerate(formats):
        x1 = 80 + idx * 360
        x2 = x1 + 330
        draw_rounded_box(draw, [x1, 160, x2, 270], fill='#eff6ff', outline='#3b82f6', width=2)
        draw.text((x1 + 15, 175), f_name, fill='#1d4ed8', font=f_box_h)
        draw.text((x1 + 15, 205), f_desc, fill='#475569', font=f_box_b)
        draw_arrow(draw, ((x1 + x2)//2, 270), ((x1 + x2)//2, 350), fill='#881337')

    # Central AST Root Node Box
    draw_rounded_box(draw, [80, 350, W-80, 490], fill='#fdf4ff', outline='#a855f7', width=3)
    draw.text((110, 370), "Unified Abstract Syntax Tree (AST) Document Representation (Omega)", fill='#6b21a8', font=f_box_h)
    draw.text((110, 405), "• Document Root -> [Metadata Node | Header Node | Paragraph Node | Table Node (M x N Grid)]\n• Preserves Cell Spans, Bold/Italic Font Weights, Bullet Hierarchies, and Formulaic Fields\n• Calculates Exact Word Count and Complexity Index Deterministically", fill='#334155', font=f_box_b)

    draw_arrow(draw, (W//2, 490), (W//2, 560), fill='#881337')

    # Cognitive Semantic Transmutation Layer
    draw_rounded_box(draw, [180, 560, W-180, 690], fill='#fdf2f8', outline='#f43f5e', width=3)
    draw.text((210, 580), "Cognitive Semantic Transmutation Engine (Algorithm 3)", fill='#9f1239', font=f_box_h)
    draw.text((210, 615), "• Traverses AST Nodes in Depth-First Order\n• Applies User Prompt Instruction Tau (e.g. 'Summarize executive risks', 'Convert to formal tone')\n• Reconstructs Node Values while Maintaining Surrounding Structural Geometry", fill='#334155', font=f_box_b)

    draw_arrow(draw, (W//2, 690), (W//2, 760), fill='#881337')

    # Export & Download Pipeline
    draw_rounded_box(draw, [280, 760, W-280, 880], fill='#f0fdf4', outline='#22c55e', width=3)
    draw.text((310, 780), "High-Fidelity Serialization & Export Pipeline", fill='#15803d', font=f_box_h)
    draw.text((310, 810), "• Re-serializes AST into Target Binary (.docx, .pdf, .csv, .md)\n• In-Memory Download Ready with Zero Server Disk Footprint (Ephemeral Security Guarantee)", fill='#1e293b', font=f_box_b)

    img.save('docs/figures/flowcharts/flowchart4_document_ast.png')
    print("Saved flowchart 4")

if __name__ == "__main__":
    create_flowchart1_cognitive_loop()
    create_flowchart2_system_architecture()
    create_flowchart3_fallback_cascade()
    create_flowchart4_document_ast()
    print("All 4 paper flowcharts successfully created in docs/figures/flowcharts/")
