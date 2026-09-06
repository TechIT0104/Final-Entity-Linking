#!/usr/bin/env python3
"""
Professional Minimalistic PowerPoint Presentation
Entity Linking Board Review - Premium Design
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
import os

# Professional Color Palette
COLOR_TEAL = RGBColor(0, 75, 92)          # Deep teal
COLOR_LIGHT_TEAL = RGBColor(200, 230, 235)  # Light teal (backgrounds)
COLOR_NAVY = RGBColor(0, 26, 51)          # Dark navy (text)
COLOR_WHITE = RGBColor(255, 255, 255)     # White
COLOR_LIGHT_GRAY = RGBColor(245, 245, 247)  # Very light gray
COLOR_ACCENT = RGBColor(212, 161, 54)     # Mustard (sparse accent)
COLOR_GREEN = RGBColor(40, 167, 69)       # Green checkmarks
COLOR_RED = RGBColor(220, 53, 69)         # Red warnings

# Create presentation
prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def add_subtle_accent_line(slide):
    """Add a thin accent line (left edge)"""
    line = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.08), Inches(7.5))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_TEAL
    line.line.fill.background()

def create_title_slide():
    """Slide 1: Title Slide - Minimalistic & Elegant"""
    slide = prs.slides.add_slide(blank_layout)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_WHITE
    
    # Add subtle accent line
    add_subtle_accent_line(slide)
    
    # Main title
    title_box = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(8), Inches(1.2))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    p = title_frame.paragraphs[0]
    p.text = "Multilingual Historical\nEntity Linking"
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.LEFT
    
    # Subtitle
    subtitle_box = slide.shapes.add_textbox(Inches(1), Inches(3.8), Inches(8), Inches(0.5))
    subtitle_frame = subtitle_box.text_frame
    p = subtitle_frame.paragraphs[0]
    p.text = "Implementation, Enhancement & Comparative Analysis"
    p.font.size = Pt(18)
    p.font.color.rgb = COLOR_NAVY
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.LEFT
    
    # Divider line
    divider = slide.shapes.add_shape(1, Inches(1), Inches(4.5), Inches(3), Inches(0.02))
    divider.fill.solid()
    divider.fill.fore_color.rgb = COLOR_ACCENT
    divider.line.fill.background()
    
    # Details at bottom
    details_box = slide.shapes.add_textbox(Inches(1), Inches(5.5), Inches(8), Inches(1.5))
    details_frame = details_box.text_frame
    details_frame.word_wrap = True
    
    for text_line in [
        "Presented by: [Your Name(s)]",
        "Roll No(s): [Roll Numbers]",
        "Date: May 6, 2026"
    ]:
        p = details_frame.add_paragraph()
        p.text = text_line
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_NAVY
        p.font.name = "Calibri"
        p.space_before = Pt(3)

def create_content_slide(title, content_points, use_columns=False):
    """Create professional content slide"""
    slide = prs.slides.add_slide(blank_layout)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_WHITE
    
    add_subtle_accent_line(slide)
    
    # Title with underline
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.4), Inches(8.5), Inches(0.6))
    title_frame = title_box.text_frame
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL
    p.font.name = "Calibri"
    
    # Underline
    underline = slide.shapes.add_shape(1, Inches(1), Inches(1.15), Inches(2.5), Inches(0.02))
    underline.fill.solid()
    underline.fill.fore_color.rgb = COLOR_ACCENT
    underline.line.fill.background()
    
    # Content
    if use_columns and len(content_points) > 6:
        # Two-column layout for many points
        col1_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(4), Inches(5.5))
        col1_frame = col1_box.text_frame
        col1_frame.word_wrap = True
        
        col2_box = slide.shapes.add_textbox(Inches(5.2), Inches(1.5), Inches(4), Inches(5.5))
        col2_frame = col2_box.text_frame
        col2_frame.word_wrap = True
        
        mid = len(content_points) // 2
        for i, point in enumerate(content_points):
            tf = col1_frame if i < mid else col2_frame
            
            if i == 0 or (i == mid):
                p = tf.paragraphs[0] if (i == 0 or len(tf.paragraphs) == 0) else tf.add_paragraph()
            else:
                p = tf.add_paragraph()
            
            if isinstance(point, tuple):
                p.text = point[0]
                p.font.bold = True
                p.font.color.rgb = COLOR_ACCENT
                p.font.size = Pt(12)
                p.space_before = Pt(8)
                p.space_after = Pt(4)
            else:
                p.text = point
                p.font.size = Pt(11)
                p.font.color.rgb = COLOR_NAVY
                p.space_before = Pt(3)
                p.space_after = Pt(3)
    else:
        # Single column
        content_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(5.5))
        content_frame = content_box.text_frame
        content_frame.word_wrap = True
        
        for i, point in enumerate(content_points):
            if i == 0:
                p = content_frame.paragraphs[0]
            else:
                p = content_frame.add_paragraph()
            
            if isinstance(point, tuple):
                p.text = point[0]
                p.font.bold = True
                p.font.color.rgb = COLOR_ACCENT
                p.font.size = Pt(13)
                p.space_before = Pt(12)
                p.space_after = Pt(6)
                p.level = 0
            else:
                # Handle bullet point levels
                text = point
                level = 0
                if text.startswith("  "):
                    text = text.strip()
                    level = 1
                
                p.text = text
                p.font.size = Pt(11)
                p.font.color.rgb = COLOR_NAVY
                p.level = level
                p.space_before = Pt(2)
                p.space_after = Pt(2)

# Slide 1: Title
create_title_slide()
print("✓ Slide 1: Title")

# Slide 2: Agenda
create_content_slide(
    "Presentation Overview",
    [
        "1. PROJECT FOUNDATION",
        "Entity Linking basics & project scope",
        "",
        "2. IMPLEMENTATION STRATEGY",
        "MHEL paper analysis & enhancement",
        "",
        "3. ALTERNATIVE EXPLORATION",
        "mReFinED implementation attempt",
        "",
        "4. COMPARATIVE ANALYSIS",
        "Cross-paper comparison & trade-offs",
        "",
        "5. PROJECT EXECUTION",
        "Timeline, results & observations",
        "",
        "6. LEARNING & FUTURE",
        "Key outcomes & future possibilities"
    ]
)
print("✓ Slide 2: Agenda")

# Slide 3: Entity Linking Foundation
create_content_slide(
    "Entity Linking Foundation",
    [
        ("CONCEPT", ""),
        "Input: Mention + context",
        "Output: Wikipedia entity ID + confidence",
        "Challenge: Disambiguate rare historical entities",
        "",
        ("MID-SEMESTER STATUS", ""),
        "✓ Literature review complete",
        "✓ BLINK & MVD baselines established",
        "✗ Full evaluation not complete",
        "",
        ("END-SEMESTER TARGET", ""),
        "✓ MHEL fully implemented & working",
        "✓ Evaluated on 6 datasets",
        "✓ Comprehensive error analysis",
        "✓ XGBoost improvements documented"
    ]
)
print("✓ Slide 3: Foundation")

# Slide 4: Motivation
create_content_slide(
    "Project Motivation & Overview",
    [
        ("WHY ENTITY LINKING?", ""),
        "Named entity disambiguation critical in NLP",
        "Historical texts present unique challenges",
        "  Abbreviations, rare entities, outdated references",
        "",
        ("WHY NOW?", ""),
        "Recent multilingual model advances (mReFinED, BELA)",
        "Practical need for historical document digitization",
        "",
        ("RESEARCH QUESTION", ""),
        "Can we build robust multilingual EL for historical texts",
        "balancing accuracy, coverage, and practical constraints?"
    ]
)
print("✓ Slide 4: Motivation")

# Slide 5: MHEL Paper Analysis
create_content_slide(
    "Paper 1: MHEL-LLaMo Analysis & Selection",
    [
        ("KEY CONTRIBUTIONS", ""),
        "Confidence-based routing approach (Easy/Hard cases)",
        "Multilingual support (9 languages tested)",
        "Evaluation on historical datasets",
        "",
        ("WHY WE SELECTED THIS PAPER", ""),
        "✓ Modularity: Clear pipeline decomposition",
        "✓ Multilingual: Directly addresses target problem",
        "✓ Feasibility: Implementable with available tools",
        "✓ Improvement: Routing logic can be enhanced",
        "✓ Benchmarks: Multiple datasets available"
    ]
)
print("✓ Slide 5: MHEL Paper")

# Slide 6: MHEL Success Path
create_content_slide(
    "Why MHEL Was the Successful Path",
    [
        ("CORE INSIGHT: Confidence-Based Routing", ""),
        "Input → BELA Retrieval → Confidence Router",
        "Easy cases (70%): Direct prediction",
        "Hard cases (30%): LLM query",
        "",
        ("SUCCESS FACTORS", ""),
        "✓ Modular design: Independent testable components",
        "✓ Multilingual: 101 languages via BELA",
        "✓ Resource efficient: Single 32GB GPU",
        "✓ Evaluation-friendly: Clear metrics"
    ]
)
print("✓ Slide 6: MHEL Success")

# Slide 7: Implementation Timeline
create_content_slide(
    "MHEL Implementation: Week-by-Week Progress",
    [
        ("WEEK 1-2: FOUNDATION", ""),
        "Environment setup, baseline models established",
        "",
        ("WEEK 3-4: CORE PIPELINE", ""),
        "Candidate retrieval, LLM integration, data pipeline",
        "",
        ("WEEK 5-6: ENHANCEMENT & TUNING", ""),
        "XGBoost router training (82% accuracy achieved)",
        "",
        ("WEEK 7-8: ERROR ANALYSIS", ""),
        "231 error cases analyzed, abbreviation patterns identified",
        "",
        ("WEEK 9-10: EVALUATION & DOCUMENTATION", ""),
        "All 6 datasets complete, full reproducibility verified"
    ]
)
print("✓ Slide 7: Timeline")

# Slide 8: Implementation Details
create_content_slide(
    "Implementation Architecture: Modules & Workflow",
    [
        ("MODULE 1: CANDIDATE GENERATION (BELA)", ""),
        "Dense retrieval, 10ms/mention, 78% recall@5",
        "",
        ("MODULE 2: CONFIDENCE ROUTER (XGBoost)", ""),
        "Binary classification, 82% accuracy, 50KB model",
        "",
        ("MODULE 3: ENTITY LINKER", ""),
        "Easy path: Top-1 candidate (70%)",
        "Hard path: Mistral-24B LLM (30%)",
        "",
        ("MODULE 4: EVALUATION ENGINE", ""),
        "9 languages, 6 datasets, comprehensive reports"
    ]
)
print("✓ Slide 8: Implementation")

# Slide 9: Challenges Overcome
create_content_slide(
    "Challenges Overcome in MHEL",
    [
        ("CHALLENGE 1: API Compatibility", ""),
        "✓ Solved: Compatibility wrapper for transformers v4.30+",
        "",
        ("CHALLENGE 2: Multilingual Tokenization", ""),
        "✓ Solved: Language-specific preprocessing module",
        "",
        ("CHALLENGE 3: GPU Memory (32GB)", ""),
        "✓ Solved: Mixed precision + gradient accumulation",
        "",
        ("CHALLENGE 4: TR2016 Offset Corruption", ""),
        "✓ Solved: Validation algorithm, 5.5x recall improvement (1.54% → 8.42%)"
    ]
)
print("✓ Slide 9: Challenges")

# Slide 10: Enhancements
create_content_slide(
    "Our Enhancements Beyond Base Paper",
    [
        ("1. XGBoost Confidence Router [NEW]", ""),
        "82% vs 70% accuracy (+12% improvement)",
        "",
        ("2. Comprehensive Error Analysis [NEW]", ""),
        "231 cases systematized, abbreviation patterns identified",
        "",
        ("3. Hardware Optimization [NEW]", ""),
        "24B model on 32GB GPU, 2x faster inference",
        "",
        ("4. Offset Validation for TR2016 [NEW]", ""),
        "5.5x recall improvement",
        "",
        ("5. Multi-Dataset Evaluation [ENHANCED]", ""),
        "6 datasets, 68,700+ mentions, 12+ languages"
    ]
)
print("✓ Slide 10: Enhancements")

# Slide 11: mReFinED Overview
create_content_slide(
    "Paper 2: mReFinED - Overview & Exploration Rationale",
    [
        ("KEY CONTRIBUTIONS", ""),
        "Cross-encoder based ranking (vs MHEL's hybrid approach)",
        "101-language multilingual coverage",
        "Real-time inference without LLM",
        "",
        ("WHY WE EXPLORED THIS PAPER", ""),
        "Compare different architectural approaches",
        "Gain insights into trade-offs",
        "Contribute to field understanding of strategies"
    ]
)
print("✓ Slide 11: mReFinED Overview")

# Slide 12: mReFinED Implementation
create_content_slide(
    "mReFinED Implementation Attempt",
    [
        ("APPROACH", ""),
        "Alternative pipeline: BELA → Cross-Encoder → Threshold",
        "",
        ("WHAT WE IMPLEMENTED", ""),
        "✓ Phase 1: Model setup & integration",
        "✓ Phase 2: Candidate scoring",
        "⚠ Phase 3: Partial multilingual eval (6/9 languages)",
        "⚠ Phase 4: Basic optimization",
        "",
        ("KEY DIFFERENCE FROM MHEL", ""),
        "MHEL: Adaptive routing vs mReFinED: Single ranker"
    ]
)
print("✓ Slide 12: mReFinED Impl")

# Slide 13: mReFinED Issues
create_content_slide(
    "mReFinED: Unresolved Issues (Honest Assessment)",
    [
        ("CHALLENGE 1: Computational Scalability", ""),
        "⚠ Cross-encoder: 45ms/mention (vs MHEL: 15ms)",
        "",
        ("CHALLENGE 2: Non-Latin Script Performance", ""),
        "⚠ Arabic/Farsi/Japanese: 24-27% F1 (vs Latin: 50-56%)",
        "",
        ("CHALLENGE 3: Hyperparameter Tuning", ""),
        "⚠ Limited time for optimization",
        "",
        ("RESOURCE CONSTRAINTS", ""),
        "10-week timeline, 1 week allocated for mReFinED",
        "Single shared GPU with MHEL development"
    ]
)
print("✓ Slide 13: mReFinED Issues")

# Slide 14: Comparative Analysis
create_content_slide(
    "Comparative Analysis: MHEL vs mReFinED",
    [
        ("MHEL-LLaMo Wins in Most Categories", ""),
        "✓ Performance: 50% vs 48% F1",
        "✓ Speed: 15ms vs 45ms per mention",
        "✓ Stability: 9/9 vs 6/9 languages reproducible",
        "✓ Completeness: 100% vs 75% implementation",
        "",
        ("COMPARATIVE VALUE", ""),
        "mReFinED partial work provided valuable insights",
        "Trade-offs clearly visible: complexity vs simplicity",
        "Justified exploratory investment in research"
    ]
)
print("✓ Slide 14: Comparison")

# Slide 15: Timeline
create_content_slide(
    "10-Week Project Timeline & Milestones",
    [
        ("WEEKS 1-2: Foundation", ""),
        "Environment, baselines established",
        "",
        ("WEEKS 3-4: Core Pipeline", ""),
        "MHEL functional on single language",
        "",
        ("WEEKS 5-6: Optimization", ""),
        "82% routing accuracy, 9 languages stable",
        "",
        ("WEEKS 7-8: Analysis", ""),
        "231 errors categorized, TR2016 improved 5.5x",
        "",
        ("WEEKS 9-10: Finalization", ""),
        "All 6 datasets evaluated, 100% reproducible"
    ]
)
print("✓ Slide 15: Timeline")

# Slide 16: Results
create_content_slide(
    "Results & Key Observations",
    [
        ("MHEL-LLaMo: COMPLETE", ""),
        "Full pipeline on 6 datasets, 68,700+ mentions evaluated",
        "",
        ("KEY METRICS", ""),
        "XGBoost Routing: 82% accuracy (+12% improvement)",
        "TR2016 Recall: 1.54% → 8.42% (+5.5x improvement)",
        "Multilingual: 9/9 languages reproducible",
        "",
        ("ERROR ANALYSIS FINDINGS", ""),
        "Top failure: Abbreviations (40% of false positives)",
        "Mention length effect: Shorter mentions more problematic",
        "NIL misclassification: 59% of false positives"
    ]
)
print("✓ Slide 16: Results")

# Slide 17: Learning Outcomes
create_content_slide(
    "Key Learning Outcomes",
    [
        ("TECHNICAL INSIGHTS", ""),
        "✓ Paper implementation ≠ paper results",
        "✓ Routing logic > LLM cost (custom model beats off-shelf)",
        "✓ Error analysis is actionable (patterns reveal solutions)",
        "✓ Constraints breed innovation (32GB GPU optimization)",
        "",
        ("PROJECT MANAGEMENT INSIGHTS", ""),
        "✓ Prioritization critical (80% MHEL, 20% mReFinED)",
        "✓ Documentation = first-class deliverable",
        "✓ Iterative improvement > perfection"
    ]
)
print("✓ Slide 17: Learning")

# Slide 18: Future Possibilities
create_content_slide(
    "Future Possibilities",
    [
        ("IMMEDIATE (1-2 months)", ""),
        "Fine-tuning on historical data (+3-5% F1)",
        "Abbreviation handling module",
        "NIL prediction improvement",
        "",
        ("MID-TERM (2-4 months)", ""),
        "Multilingual fine-tuning for non-Latin scripts",
        "Knowledge graph integration",
        "Temporal entity linking",
        "",
        ("LONG-TERM (4+ months)", ""),
        "Production deployment & benchmark expansion",
        "Research publications (2-3 papers expected)"
    ]
)
print("✓ Slide 18: Future")

# Slide 19: References
create_content_slide(
    "Primary References & Research Foundation",
    [
        "[1] MHEL-LLaMo: Multilingual Historical Entity Linking",
        "Core implementation basis for this project",
        "",
        "[2] mReFinED: Multilingual Refined Entity Disambiguation",
        "Alternative approach for comparative analysis",
        "",
        "[3] BLINK: Unified Framework for Entity Linking",
        "Baseline system and architecture reference",
        "",
        "[4] Datasets: AJMC, MEWSLI-9, NEWSEYE, HIPE, MHERCL, TR2016",
        "Multilingual evaluation benchmarks",
        "",
        "[5] Tools: PyTorch, Transformers, XGBoost, HuggingFace",
        "Essential libraries and frameworks"
    ]
)
print("✓ Slide 19: References")

# Slide 20: Closing
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_subtle_accent_line(slide)

# Main message
closing_box = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(8), Inches(2))
closing_frame = closing_box.text_frame
closing_frame.word_wrap = True

p = closing_frame.paragraphs[0]
p.text = "Summary"
p.font.size = Pt(40)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL
p.font.name = "Calibri"

p = closing_frame.add_paragraph()
p.text = "✓ Successfully implemented MHEL-LLaMo pipeline"
p.font.size = Pt(12)
p.font.color.rgb = COLOR_NAVY
p.font.name = "Calibri"
p.space_before = Pt(12)

p = closing_frame.add_paragraph()
p.text = "✓ +12% routing accuracy, 100% reproducible with full documentation"
p.font.size = Pt(12)
p.font.color.rgb = COLOR_NAVY

p = closing_frame.add_paragraph()
p.text = "✓ Rigorous evaluation (68,700+ mentions, 6 datasets, 12+ languages)"
p.font.size = Pt(12)
p.font.color.rgb = COLOR_NAVY

p = closing_frame.add_paragraph()
p.text = "✓ Comprehensive error analysis & honest assessment of trade-offs"
p.font.size = Pt(12)
p.font.color.rgb = COLOR_NAVY

# Thank you
thank_box = slide.shapes.add_textbox(Inches(1), Inches(6), Inches(8), Inches(1))
thank_frame = thank_box.text_frame
p = thank_frame.paragraphs[0]
p.text = "Thank You — Questions?"
p.font.size = Pt(28)
p.font.bold = True
p.font.color.rgb = COLOR_ACCENT
p.font.name = "Calibri"
p.alignment = PP_ALIGN.CENTER

print("✓ Slide 20: Closing")

# Try to add images
img_dir = r"C:\Users\Dhruv\OneDrive\Desktop\Final Entity Linking\images"
image_placements = [
    (7, "mhel_llamo_arch.png", Inches(5.5), Inches(2.5), Inches(3.8)),
    (15, "mewsli9_f1.png", Inches(5.5), Inches(2.5), Inches(3.8)),
    (2, "blink_benchmark_bar.png", Inches(5.2), Inches(3.0), Inches(3.5)),
    (3, "mvd_recall_curve.png", Inches(5.2), Inches(3.0), Inches(3.5))
]

for slide_idx, img_name, left, top, width in image_placements:
    try:
        img_path = os.path.join(img_dir, img_name)
        if os.path.exists(img_path):
            prs.slides[slide_idx].shapes.add_picture(img_path, left, top, width=width)
            print(f"  → Added image: {img_name}")
    except Exception as e:
        print(f"  ⚠ Could not add {img_name}: {e}")

# Save presentation
output_path = r"C:\Users\Dhruv\OneDrive\Desktop\Final Entity Linking\Board_Review_Presentation.pptx"
prs.save(output_path)

print(f"\n✅ Professional Minimalistic PPTX Created!")
print(f"📊 Total slides: {len(prs.slides)}")
print(f"📁 Saved to: {output_path}")
print(f"\n🎯 Professional design with:")
print(f"  • Clean minimalistic aesthetic")
print(f"  • Elegant typography (Calibri)")
print(f"  • Subtle teal accent line (left edge)")
print(f"  • Professional color palette")
print(f"  • Proper whitespace and hierarchy")
print(f"  • Full content from specifications")
