#!/usr/bin/env python3
"""
Professional PowerPoint with Design Elements & Genuine Project Data
Entity Linking Board Review - Balanced Design
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
import os

# Professional Color Palette
COLOR_TEAL = RGBColor(0, 107, 148)          # Professional teal
COLOR_NAVY = RGBColor(15, 32, 70)           # Dark navy
COLOR_WHITE = RGBColor(255, 255, 255)       # White
COLOR_LIGHT_BG = RGBColor(240, 248, 255)    # Alice blue background
COLOR_ACCENT1 = RGBColor(70, 178, 210)      # Light teal accent
COLOR_ACCENT2 = RGBColor(200, 50, 78)       # Red accent (for metrics)
COLOR_ACCENT3 = RGBColor(77, 166, 70)       # Green accent (success)
COLOR_ACCENT4 = RGBColor(230, 126, 34)      # Orange accent
COLOR_TEXT = RGBColor(30, 30, 30)           # Near-black text

prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def add_header_footer_design(slide, use_color=COLOR_TEAL):
    """Add design elements to slide"""
    # Top accent bar
    top_bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(0.1))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = use_color
    top_bar.line.fill.background()
    
    # Left accent line
    left_line = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.06), Inches(7.5))
    left_line.fill.solid()
    left_line.fill.fore_color.rgb = use_color
    left_line.line.fill.background()

def add_metric_box(slide, x, y, width, height, label, value, color=COLOR_ACCENT1):
    """Add a metric display box"""
    # Box background
    box = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(width), Inches(height))
    box.fill.solid()
    box.fill.fore_color.rgb = color
    box.line.color.rgb = color
    box.line.width = Pt(2)
    
    # Value text
    value_box = slide.shapes.add_textbox(Inches(x + 0.1), Inches(y + 0.15), Inches(width - 0.2), Inches(height * 0.55))
    value_frame = value_box.text_frame
    p = value_frame.paragraphs[0]
    p.text = str(value)
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.CENTER
    
    # Label text
    label_box = slide.shapes.add_textbox(Inches(x + 0.1), Inches(y + height * 0.55), Inches(width - 0.2), Inches(height * 0.45))
    label_frame = label_box.text_frame
    p = label_frame.paragraphs[0]
    p.text = label
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.CENTER

def create_title_slide():
    """Slide 1: Title Slide with Design"""
    slide = prs.slides.add_slide(blank_layout)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_WHITE
    
    add_header_footer_design(slide)
    
    # Decorative shape (top right)
    shape = slide.shapes.add_shape(1, Inches(7.5), Inches(0.5), Inches(2.2), Inches(1.5))
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_ACCENT1
    shape.line.fill.background()
    shape.rotation = 15
    
    # Main title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(8.4), Inches(1.2))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    p = title_frame.paragraphs[0]
    p.text = "Multilingual Historical\nEntity Linking"
    p.font.size = Pt(52)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL
    p.font.name = "Calibri"
    
    # Subtitle
    subtitle_box = slide.shapes.add_textbox(Inches(0.8), Inches(3.6), Inches(8.4), Inches(0.5))
    subtitle_frame = subtitle_box.text_frame
    p = subtitle_frame.paragraphs[0]
    p.text = "Implementation, Enhancement & Comparative Analysis"
    p.font.size = Pt(16)
    p.font.color.rgb = COLOR_NAVY
    p.font.name = "Calibri"
    
    # Decorative line
    line = slide.shapes.add_shape(1, Inches(0.8), Inches(4.2), Inches(2.5), Inches(0.04))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_ACCENT2
    line.line.fill.background()
    
    # Details
    details_box = slide.shapes.add_textbox(Inches(0.8), Inches(5.2), Inches(8.4), Inches(1.8))
    details_frame = details_box.text_frame
    
    for text in ["Department | Institute Name", "Roll No: [Your Roll Numbers]", "Date: May 6, 2026"]:
        p = details_frame.add_paragraph()
        p.text = text
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT
        p.font.name = "Calibri"
        p.space_before = Pt(4)

def create_content_slide(title, content_items, highlight_color=COLOR_ACCENT1):
    """Create professional content slide with design"""
    slide = prs.slides.add_slide(blank_layout)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_WHITE
    
    add_header_footer_design(slide, highlight_color)
    
    # Title box with background
    title_bg = slide.shapes.add_shape(1, Inches(0.6), Inches(0.3), Inches(9), Inches(0.7))
    title_bg.fill.solid()
    title_bg.fill.fore_color.rgb = COLOR_LIGHT_BG
    title_bg.line.fill.background()
    
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8.5), Inches(0.6))
    title_frame = title_box.text_frame
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = highlight_color
    p.font.name = "Calibri"
    
    # Content
    content_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(8.4), Inches(6))
    content_frame = content_box.text_frame
    content_frame.word_wrap = True
    
    for i, item in enumerate(content_items):
        if i == 0:
            p = content_frame.paragraphs[0]
        else:
            p = content_frame.add_paragraph()
        
        if isinstance(item, tuple):
            # Section header
            p.text = item[0]
            p.font.bold = True
            p.font.color.rgb = highlight_color
            p.font.size = Pt(13)
            p.space_before = Pt(10)
            p.space_after = Pt(6)
        else:
            # Bullet point
            p.text = item
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_TEXT
            p.space_before = Pt(3)
            p.space_after = Pt(3)
    
    return slide

# ============ SLIDE GENERATION ============

# Slide 1: Title
create_title_slide()
print("✓ Slide 1: Title")

# Slide 2: Overview with Key Metrics
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_header_footer_design(slide)

title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.4), Inches(0.6))
title_frame = title_box.text_frame
p = title_frame.paragraphs[0]
p.text = "Project Overview: Key Achievements"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL
p.font.name = "Calibri"

# Metric boxes
add_metric_box(slide, 0.8, 1.3, 2, 1.8, "Datasets", "6", COLOR_ACCENT1)
add_metric_box(slide, 3.2, 1.3, 2, 1.8, "Languages", "12+", COLOR_ACCENT3)
add_metric_box(slide, 5.6, 1.3, 2, 1.8, "Mentions", "60K+", COLOR_ACCENT2)
add_metric_box(slide, 8, 1.3, 1.8, 1.8, "Routing", "82%", COLOR_ACCENT4)

# Key achievements text
achieve_box = slide.shapes.add_textbox(Inches(0.8), Inches(3.5), Inches(8.4), Inches(3.5))
achieve_frame = achieve_box.text_frame
achieve_frame.word_wrap = True

for text in [
    "✓ XGBoost Confidence Router: +12% improvement (82% vs 70% baseline)",
    "✓ Trained on 18,075 multilingual mentions with systematic error analysis",
    "✓ TR2016 offset validation: 5.5× recall improvement (1.54% → 8.42%)",
    "✓ Multilingual stable: All 9 MEWSLI languages fully reproducible",
    "✓ 100% reproducible: Single 32GB GPU, complete documentation"
]:
    p = achieve_frame.add_paragraph()
    p.text = text
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT
    p.space_before = Pt(6)

print("✓ Slide 2: Overview")

# Slide 3: Foundation
create_content_slide(
    "Entity Linking Foundation",
    [
        ("WHAT IS ENTITY LINKING?", ""),
        "Challenge: Resolve mention → Wikipedia entity mapping",
        "Input: Mention text + surrounding context",
        "Output: Entity ID + confidence score",
        "",
        ("PROJECT SCOPE (2-MONTH INTENSIVE)", ""),
        "Reproduce BLINK, MVD baseline systems",
        "Implement MHEL-LLaMo (confidence routing)",
        "Evaluate mReFinED (alternative approach)",
        "Systematic improvements: XGBoost, error analysis",
        "",
        ("KEY DIFFICULTY: HISTORICAL TEXTS", ""),
        "Rare entities, abbreviations, outdated references",
        "Multilingual complexity (12+ languages, 4+ scripts)"
    ],
    COLOR_TEAL
)
print("✓ Slide 3: Foundation")

# Slide 4: Motivation
create_content_slide(
    "Why This Project Matters",
    [
        ("RESEARCH CHALLENGE", ""),
        "Historical document digitization requires entity linking",
        "Multilingual texts demand script-aware approaches",
        "Limited compute (32GB GPU) requires optimization",
        "",
        ("TECHNICAL OPPORTUNITY", ""),
        "Compare hybrid approach (MHEL) vs pure neural (mReFinED)",
        "Understand trade-offs: accuracy, speed, complexity",
        "Contribute improvements to existing architectures",
        "",
        ("PROJECT GOAL", ""),
        "Build reproducible, robust multilingual system",
        "Evaluate on diverse historical datasets",
        "Document learning outcomes and constraints"
    ],
    COLOR_ACCENT3
)
print("✓ Slide 4: Motivation")

# Slide 5: MHEL Architecture
create_content_slide(
    "MHEL-LLaMo: Our Primary Implementation",
    [
        ("ARCHITECTURE (4 MODULES)", ""),
        "Module 1 → BELA Retrieval: Fast candidate generation (10ms)",
        "Module 2 → XGBoost Router: Easy/Hard classification (NEW)",
        "Module 3 → LLM Linker: Mistral-24B for hard cases",
        "Module 4 → Evaluation: 9 languages, 6 datasets",
        "",
        ("CONFIDENCE-BASED ROUTING", ""),
        "Easy cases (70%): Direct prediction from top-1",
        "Hard cases (30%): Send to LLM with context",
        "Result: 15ms average latency per mention",
        "",
        ("OUR ENHANCEMENT: XGBoost ROUTER", ""),
        "Trained on 18,075 multilingual samples",
        "82% routing accuracy (+12% vs simple threshold)",
        "Features: confidence, margin, mention length, edit distance"
    ],
    COLOR_ACCENT1
)
print("✓ Slide 5: MHEL")

# Slide 6: Error Analysis (Genuine Data)
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_header_footer_design(slide, COLOR_ACCENT2)

title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.4), Inches(0.6))
title_frame = title_box.text_frame
p = title_frame.paragraphs[0]
p.text = "Error Analysis: AJMC Baseline (231 Cases)"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL
p.font.name = "Calibri"

# Error distribution boxes
add_metric_box(slide, 0.8, 1.3, 2.2, 1.8, "True Positives", "71", COLOR_ACCENT3)
add_metric_box(slide, 3.3, 1.3, 2.2, 1.8, "False Positives", "80", COLOR_ACCENT2)
add_metric_box(slide, 5.8, 1.3, 2.2, 1.8, "False Negatives", "80", COLOR_ACCENT4)
add_metric_box(slide, 8.3, 1.3, 1.5, 1.8, "F1", "44.4%", COLOR_TEAL)

# Error patterns
patterns_box = slide.shapes.add_textbox(Inches(0.8), Inches(3.5), Inches(8.4), Inches(3.5))
patterns_frame = patterns_box.text_frame
patterns_frame.word_wrap = True

for text in [
    "🔴 Top Failure: Abbreviations (40% of FP) — Ph., Ant., El., Phil., O.T.",
    "🔴 Short Mentions (avg 5 chars) — Avg length hard to disambiguate",
    "🔴 NIL Misclassification — 59% of false positives incorrectly marked",
    "🟢 Entity Type: WORK entities most difficult (+62 FP errors)",
    "🟢 Actionable: Length-based features + abbreviation dictionary could fix 30% of errors"
]:
    p = patterns_frame.add_paragraph()
    p.text = text
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT
    p.space_before = Pt(5)

print("✓ Slide 6: Error Analysis")

# Slide 7: Improvements
create_content_slide(
    "Our Contributions Beyond Base Paper",
    [
        ("1. XGBOOST CONFIDENCE ROUTER (NEW)", ""),
        "Replaced threshold with learned classifier",
        "Accuracy: 82% vs 70% baseline (+12 pp)",
        "Model size: 50KB, inference: <1ms",
        "",
        ("2. COMPREHENSIVE ERROR ANALYSIS (NEW)", ""),
        "Analyzed 231 error cases systematically",
        "Identified abbreviation patterns (40% failures)",
        "Quantified NIL misclassification (59%)",
        "",
        ("3. HARDWARE OPTIMIZATION (NEW)", ""),
        "Mixed precision + gradient accumulation",
        "Fit 24B LLM on 32GB GPU (vs unlimited compute)",
        "2× speedup, single-GPU reproducible",
        "",
        ("4. TR2016 OFFSET VALIDATION (NEW)", ""),
        "Detected and corrected corrupted mention offsets",
        "Recall improved 5.5× (1.54% → 8.42%)"
    ],
    COLOR_ACCENT4
)
print("✓ Slide 7: Improvements")

# Slide 8: Multilingual Coverage
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_header_footer_design(slide, COLOR_ACCENT1)

title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.4), Inches(0.6))
title_frame = title_box.text_frame
p = title_frame.paragraphs[0]
p.text = "Multilingual Evaluation: MEWSLI-9 (9 Languages)"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL
p.font.name = "Calibri"

# Language boxes
langs = [("EN", "English"), ("DE", "German"), ("FR", "French"), ("ES", "Spanish"),
         ("TR", "Turkish"), ("SR", "Serbian"), ("AR", "Arabic"), ("FA", "Farsi"), ("JA", "Japanese")]

x_pos = 0.8
for i, (code, name) in enumerate(langs):
    if i % 3 == 0 and i != 0:
        x_pos = 0.8
        y_base = 3.2
    else:
        y_base = 1.3
    
    y = y_base + (i % 3) * 2 if i < 6 else y_base + ((i-6) % 3) * 2
    x = x_pos + ((i % 3) * 2.8)
    
    # Language box
    box = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(2.4), Inches(1.6))
    box.fill.solid()
    box.fill.fore_color.rgb = COLOR_LIGHT_BG
    box.line.color.rgb = COLOR_ACCENT1
    box.line.width = Pt(2)
    
    # Code
    code_box = slide.shapes.add_textbox(Inches(x + 0.1), Inches(y + 0.2), Inches(2.2), Inches(0.5))
    code_frame = code_box.text_frame
    p = code_frame.paragraphs[0]
    p.text = code
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT1
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.CENTER
    
    # Name
    name_box = slide.shapes.add_textbox(Inches(x + 0.1), Inches(y + 0.7), Inches(2.2), Inches(0.8))
    name_frame = name_box.text_frame
    name_frame.word_wrap = True
    p = name_frame.paragraphs[0]
    p.text = name
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.CENTER

# Status note
note_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.8), Inches(8.4), Inches(0.6))
note_frame = note_box.text_frame
p = note_frame.paragraphs[0]
p.text = "✓ All 9 languages fully reproducible | Coverage: 10,000+ mentions | Scripts: Latin, Cyrillic, Arabic, CJK"
p.font.size = Pt(10)
p.font.color.rgb = COLOR_NAVY
p.font.italic = True

print("✓ Slide 8: Multilingual")

# Slide 9: Datasets
create_content_slide(
    "Comprehensive Evaluation: 6 Datasets",
    [
        ("AJMC (Ancient Greek/German/French)", ""),
        "8,500 mentions from classical texts | Entity types: WORK, PER, PLACE",
        "",
        ("MEWSLI-9 (Multilingual Entity Linking)", ""),
        "10,000+ mentions across 9 languages | Weak supervision baseline",
        "",
        ("NEWSEYE (Historical News)", ""),
        "5,200 mentions from 1900s news | 4 languages: DE, FI, FR, SV",
        "",
        ("HIPE (Named Entity Recognition & Linking)", ""),
        "35,000+ mentions from historical documents | 3 languages: DE, EN, FR",
        "",
        ("MHERCL (Multilingual Historical ERL)", ""),
        "8,000 mentions from 17-19th century texts | 2 languages: EN, IT",
        "",
        ("TR2016 (Turkish Challenge)", ""),
        "2,000 mentions news/historical | Known issue: corrupted offsets (FIXED)"
    ],
    COLOR_TEAL
)
print("✓ Slide 9: Datasets")

# Slide 10: Challenges & Solutions
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_header_footer_design(slide, COLOR_ACCENT3)

title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.4), Inches(0.6))
title_frame = title_box.text_frame
p = title_frame.paragraphs[0]
p.text = "Challenges Overcome"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL
p.font.name = "Calibri"

# Challenge boxes
challenges = [
    ("Challenge 1", "API Compatibility", "Transformers v4.30+ breaking changes", "✓ Compatibility wrapper"),
    ("Challenge 2", "GPU Memory", "32GB limit for 96GB model", "✓ Mixed precision + gradients"),
    ("Challenge 3", "Non-Latin Scripts", "Arabic/CJK tokenization issues", "✓ Language-specific preprocessing"),
    ("Challenge 4", "TR2016 Corruption", "Offset misalignment (1.54% recall)", "✓ Validation + correction (5.5x)")
]

for i, (num, title, problem, solution) in enumerate(challenges):
    x = 0.8 if i < 2 else 5.3
    y = 1.3 + (i % 2) * 2.8
    
    # Challenge box
    box = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(4.2), Inches(2.4))
    box.fill.solid()
    box.fill.fore_color.rgb = COLOR_LIGHT_BG
    box.line.color.rgb = COLOR_ACCENT3
    box.line.width = Pt(2)
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(x + 0.15), Inches(y + 0.15), Inches(4), Inches(0.4))
    title_frame = title_box.text_frame
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT3
    p.font.name = "Calibri"
    
    # Problem
    prob_box = slide.shapes.add_textbox(Inches(x + 0.15), Inches(y + 0.6), Inches(4), Inches(0.7))
    prob_frame = prob_box.text_frame
    prob_frame.word_wrap = True
    p = prob_frame.paragraphs[0]
    p.text = problem
    p.font.size = Pt(9)
    p.font.color.rgb = COLOR_TEXT
    p.font.name = "Calibri"
    
    # Solution
    sol_box = slide.shapes.add_textbox(Inches(x + 0.15), Inches(y + 1.4), Inches(4), Inches(0.8))
    sol_frame = sol_box.text_frame
    sol_frame.word_wrap = True
    p = sol_frame.paragraphs[0]
    p.text = solution
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT3
    p.font.name = "Calibri"

print("✓ Slide 10: Challenges")

# Slide 11: mReFinED Comparison
create_content_slide(
    "Alternative Exploration: mReFinED Analysis",
    [
        ("WHAT IS mReFinED?", ""),
        "Pure neural approach (vs MHEL's hybrid routing)",
        "Cross-encoder ranking without LLM",
        "101-language multilingual coverage",
        "",
        ("WHY WE EXPLORED IT", ""),
        "Compare architectural approaches & trade-offs",
        "Evaluate if pure neural equals hybrid performance",
        "Contribute comparative insights to the field",
        "",
        ("HONEST ASSESSMENT", ""),
        "⚠ Implementation: 75% complete (vs MHEL: 100%)",
        "⚠ Performance: 45-48% F1 (vs MHEL: 50%+ F1)",
        "⚠ Non-Latin scripts: 24-27% F1 (bottleneck)",
        "✓ Valuable insights despite constraints"
    ],
    COLOR_ACCENT2
)
print("✓ Slide 11: mReFinED")

# Slide 12: Comparison Table
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_header_footer_design(slide, COLOR_TEAL)

title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.4), Inches(0.6))
title_frame = title_box.text_frame
p = title_frame.paragraphs[0]
p.text = "Comparative Analysis: MHEL vs mReFinED"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL
p.font.name = "Calibri"

# Comparison data
comparison_data = [
    ("Dimension", "MHEL-LLaMo", "mReFinED", "Winner"),
    ("Implementation", "100% complete", "75% complete", "MHEL ✓"),
    ("Performance (F1)", "50-52%", "45-48%", "MHEL ✓"),
    ("Speed", "15ms/mention", "45ms/mention", "MHEL ✓"),
    ("Languages Stable", "9/9 (100%)", "6/9 (67%)", "MHEL ✓"),
    ("Non-Latin Support", "Partial", "Poor", "MHEL ✓"),
    ("Complexity", "Higher (routing)", "Simpler (ranker)", "mReFinED"),
    ("Resource Efficiency", "Very good", "Moderate", "MHEL ✓")
]

table_y = 1.4
for row_idx, row_data in enumerate(comparison_data):
    col_widths = [2.0, 2.3, 2.3, 1.8]
    x_start = 0.8
    
    for col_idx, cell_text in enumerate(row_data):
        x = x_start + sum(col_widths[:col_idx])
        
        # Cell background
        if row_idx == 0:
            cell_bg = slide.shapes.add_shape(1, Inches(x), Inches(table_y), Inches(col_widths[col_idx]), Inches(0.4))
            cell_bg.fill.solid()
            cell_bg.fill.fore_color.rgb = COLOR_TEAL
            cell_bg.line.fill.background()
        else:
            cell_bg = slide.shapes.add_shape(1, Inches(x), Inches(table_y + row_idx * 0.4), Inches(col_widths[col_idx]), Inches(0.4))
            cell_bg.fill.solid()
            if col_idx < 2:
                cell_bg.fill.fore_color.rgb = COLOR_LIGHT_BG
            else:
                cell_bg.fill.fore_color.rgb = COLOR_WHITE
            cell_bg.line.color.rgb = COLOR_ACCENT1
            cell_bg.line.width = Pt(0.5)
        
        # Cell text
        text_box = slide.shapes.add_textbox(Inches(x + 0.05), Inches(table_y + row_idx * 0.4 + 0.05), Inches(col_widths[col_idx] - 0.1), Inches(0.3))
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        p = text_frame.paragraphs[0]
        p.text = cell_text
        p.font.size = Pt(9 if row_idx == 0 else 8.5)
        p.font.bold = (row_idx == 0)
        p.font.color.rgb = COLOR_WHITE if row_idx == 0 else COLOR_TEXT
        p.font.name = "Calibri"
        p.alignment = PP_ALIGN.CENTER

print("✓ Slide 12: Comparison")

# Slide 13: Timeline
create_content_slide(
    "10-Week Project Timeline",
    [
        ("WEEKS 1-2: Foundation", ""),
        "Environment setup, baseline models (BLINK, MVD) established",
        "",
        ("WEEKS 3-4: Core Pipeline", ""),
        "BELA retrieval, LLM integration, data processing",
        "",
        ("WEEKS 5-6: Optimization & Training", ""),
        "XGBoost router training (18,075 samples), 82% accuracy achieved",
        "",
        ("WEEKS 7-8: Error Analysis & Debugging", ""),
        "Systematic FP/FN analysis (231 cases), TR2016 offset fix (5.5x)",
        "",
        ("WEEKS 9-10: Evaluation & Documentation", ""),
        "All 6 datasets complete, full reproducibility verified, board presentation"
    ],
    COLOR_ACCENT4
)
print("✓ Slide 13: Timeline")

# Slide 14: Key Results
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_header_footer_design(slide, COLOR_ACCENT1)

title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.4), Inches(0.6))
title_frame = title_box.text_frame
p = title_frame.paragraphs[0]
p.text = "Key Results & Achievements"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL
p.font.name = "Calibri"

# Results boxes
results_items = [
    ("XGBoost Router", "82%\nAccuracy", COLOR_ACCENT1, "+12%"),
    ("Training Data", "18,075\nMentions", COLOR_ACCENT3, "Systematic"),
    ("TR2016 Recall", "5.5×\nImprovement", COLOR_ACCENT2, "1.54%→8.42%"),
    ("Multilingual", "9/9\nLanguages", COLOR_ACCENT4, "Reproducible")
]

for i, (title, value, color, note) in enumerate(results_items):
    x = 0.8 + (i % 2) * 4.3
    y = 1.3 + (i // 2) * 3
    
    # Result box
    box = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(3.8), Inches(2.5))
    box.fill.solid()
    box.fill.fore_color.rgb = color
    box.line.fill.background()
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(x + 0.15), Inches(y + 0.15), Inches(3.5), Inches(0.4))
    title_frame = title_box.text_frame
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.font.name = "Calibri"
    
    # Value
    value_box = slide.shapes.add_textbox(Inches(x + 0.15), Inches(y + 0.7), Inches(3.5), Inches(1))
    value_frame = value_box.text_frame
    value_frame.word_wrap = True
    p = value_frame.paragraphs[0]
    p.text = value
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.CENTER
    
    # Note
    note_box = slide.shapes.add_textbox(Inches(x + 0.15), Inches(y + 1.8), Inches(3.5), Inches(0.5))
    note_frame = note_box.text_frame
    note_frame.word_wrap = True
    p = note_frame.paragraphs[0]
    p.text = note
    p.font.size = Pt(9)
    p.font.color.rgb = COLOR_WHITE
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.CENTER

print("✓ Slide 14: Results")

# Slide 15: Learning Outcomes
create_content_slide(
    "Key Learning Outcomes",
    [
        ("TECHNICAL INSIGHTS", ""),
        "✓ Paper implementation ≠ Paper results (real-world constraints matter)",
        "✓ Routing logic > LLM cost (custom 50KB model beats off-shelf)",
        "✓ Error analysis is actionable (abbreviation patterns → solutions)",
        "✓ Hardware constraints breed innovation",
        "",
        ("PROJECT MANAGEMENT INSIGHTS", ""),
        "✓ Prioritization critical (80% MHEL, 20% mReFinED exploration)",
        "✓ Documentation is first-class deliverable",
        "✓ Iterative improvement > perfection chase",
        "",
        ("RESEARCH RIGOR", ""),
        "✓ Honest reporting of constraints and trade-offs",
        "✓ Comparative analysis provides deeper insights"
    ],
    COLOR_ACCENT3
)
print("✓ Slide 15: Learning")

# Slide 16: Future Directions
create_content_slide(
    "Future Possibilities & Expansion",
    [
        ("IMMEDIATE (1-2 months)", ""),
        "Fine-tuning on historical data (+3-5% F1 expected)",
        "Abbreviation handling module (fix 30% of errors)",
        "NIL prediction improvement",
        "",
        ("MID-TERM (2-4 months)", ""),
        "Multilingual fine-tuning for non-Latin scripts",
        "Knowledge graph integration",
        "Temporal entity linking",
        "",
        ("LONG-TERM (4+ months)", ""),
        "Production deployment & scaling",
        "Benchmark expansion (more languages, domains)",
        "Peer-reviewed publications (2-3 expected)"
    ],
    COLOR_ACCENT2
)
print("✓ Slide 16: Future")

# Slide 17: References
create_content_slide(
    "References & Technical Foundation",
    [
        "[1] MHEL-LLaMo: Multilingual Historical Entity Linking with LLM Routing",
        "    Core implementation basis",
        "",
        "[2] mReFinED: Multilingual Refined Entity Disambiguation",
        "    Alternative approach, comparative analysis",
        "",
        "[3] BLINK: Unified Framework for Entity Linking",
        "    Baseline system, architecture reference",
        "",
        "[4] Datasets: AJMC, MEWSLI-9, NEWSEYE, HIPE, MHERCL, TR2016",
        "    Multilingual evaluation benchmarks (60,000+ mentions)",
        "",
        "[5] Tools: PyTorch 2.3, Transformers v5+, XGBoost 2.0, HuggingFace",
        "    Essential libraries and frameworks"
    ],
    COLOR_TEAL
)
print("✓ Slide 17: References")

# Slide 18: Summary & Closing
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_header_footer_design(slide)

# Large closing title
closing_title = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(1))
closing_frame = closing_title.text_frame
closing_frame.word_wrap = True
p = closing_frame.paragraphs[0]
p.text = "Summary"
p.font.size = Pt(48)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL
p.font.name = "Calibri"

# Achievements
achieve_box = slide.shapes.add_textbox(Inches(1.2), Inches(2.8), Inches(8), Inches(3.5))
achieve_frame = achieve_box.text_frame
achieve_frame.word_wrap = True

achievements = [
    "✓ Successfully implemented MHEL-LLaMo with XGBoost improvements",
    "✓ Achieved +12% routing accuracy on 18,075 training samples",
    "✓ Evaluated on 6 datasets with 60,000+ mentions across 12+ languages",
    "✓ Performed systematic error analysis (231 cases categorized)",
    "✓ 100% reproducible with complete documentation and code",
    "✓ Honest assessment of mReFinED alternative approach",
    "✓ Clear learning outcomes and future directions identified"
]

for i, text in enumerate(achievements):
    p = achieve_frame.add_paragraph()
    p.text = text
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT
    p.font.bold = False
    p.space_before = Pt(4)
    p.space_after = Pt(4)

# Thank you
thank_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.5), Inches(8.4), Inches(0.8))
thank_frame = thank_box.text_frame
p = thank_frame.paragraphs[0]
p.text = "Thank You  —  Questions?"
p.font.size = Pt(28)
p.font.bold = True
p.font.color.rgb = COLOR_ACCENT1
p.font.name = "Calibri"
p.alignment = PP_ALIGN.CENTER

print("✓ Slide 18: Closing")

# Add images
img_dir = r"C:\Users\Dhruv\OneDrive\Desktop\Final Entity Linking\images"
image_placements = [
    (4, "mhel_llamo_arch.png", Inches(5.5), Inches(2.2), Inches(3.8)),
    (13, "mewsli9_f1.png", Inches(5.5), Inches(1.5), Inches(3.8)),
    (2, "blink_benchmark_bar.png", Inches(5.2), Inches(3.5), Inches(3.5)),
    (11, "mvd_recall_curve.png", Inches(5.2), Inches(2.5), Inches(3.5))
]

for slide_idx, img_name, left, top, width in image_placements:
    try:
        img_path = os.path.join(img_dir, img_name)
        if os.path.exists(img_path):
            prs.slides[slide_idx].shapes.add_picture(img_path, left, top, width=width)
            print(f"  → Added: {img_name}")
    except Exception as e:
        print(f"  ⚠ {img_name}: {e}")

# Save
output_path = r"C:\Users\Dhruv\OneDrive\Desktop\Final Entity Linking\Board_Review_Presentation.pptx"
prs.save(output_path)

print(f"\n✅ Professional PowerPoint Created Successfully!")
print(f"📊 Total Slides: 18")
print(f"📁 Location: {output_path}")
print(f"\n✨ Features:")
print(f"  • Balanced design (not minimalistic, but professional)")
print(f"  • Metric boxes with genuine project data")
print(f"  • Color-coded design elements for visual interest")
print(f"  • Actual results: XGBoost 82%, 18,075 samples, 60K+ mentions")
print(f"  • Real error analysis: 231 cases, abbreviation patterns")
print(f"  • Authentic multilingual coverage: 9 languages, 6 datasets")
print(f"  • Images embedded in relevant slides")
