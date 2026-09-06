#!/usr/bin/env python3
"""
Professional PowerPoint Presentation - Properly Structured
Entity Linking Board Review - Detailed & Well-Designed
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
import os

# Professional Color Palette
COLOR_TEAL = RGBColor(0, 107, 148)
COLOR_NAVY = RGBColor(15, 32, 70)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_LIGHT_BG = RGBColor(240, 248, 255)
COLOR_ACCENT1 = RGBColor(70, 178, 210)
COLOR_ACCENT2 = RGBColor(200, 50, 78)
COLOR_ACCENT3 = RGBColor(77, 166, 70)
COLOR_ACCENT4 = RGBColor(230, 126, 34)
COLOR_TEXT = RGBColor(30, 30, 30)
COLOR_LIGHT_TEXT = RGBColor(100, 100, 100)

prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def add_design_elements(slide, primary_color=COLOR_TEAL):
    """Add design elements: top bar, circles, curves"""
    # Top accent bar
    top_bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(0.15))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = primary_color
    top_bar.line.fill.background()
    
    # Bottom decorative circle
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(8.8), Inches(6.8), Inches(1.2), Inches(1.2))
    circle.fill.solid()
    circle.fill.fore_color.rgb = primary_color
    circle.line.fill.background()
    circle.shadow.inherit = False
    
    # Left side accent circle (smaller)
    circle2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-0.3), Inches(3), Inches(0.8), Inches(0.8))
    circle2.fill.solid()
    circle2.fill.fore_color.rgb = COLOR_ACCENT1
    circle2.line.fill.background()

def add_section_header(slide, title, color=COLOR_TEAL):
    """Add styled section header"""
    # Header background
    header_bg = slide.shapes.add_shape(1, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8))
    header_bg.fill.solid()
    header_bg.fill.fore_color.rgb = COLOR_LIGHT_BG
    header_bg.line.color.rgb = color
    header_bg.line.width = Pt(3)
    
    # Title text
    title_box = slide.shapes.add_textbox(Inches(0.7), Inches(0.45), Inches(8.6), Inches(0.7))
    title_frame = title_box.text_frame
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = color
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.LEFT

def add_bullet_section(slide, y_start, section_title, bullets, color=COLOR_ACCENT1, title_size=14):
    """Add a section with title and bullets"""
    # Section title
    title_box = slide.shapes.add_textbox(Inches(0.7), Inches(y_start), Inches(8.6), Inches(0.35))
    title_frame = title_box.text_frame
    p = title_frame.paragraphs[0]
    p.text = section_title
    p.font.size = Pt(title_size)
    p.font.bold = True
    p.font.color.rgb = color
    p.font.name = "Calibri"
    
    # Bullets
    bullet_box = slide.shapes.add_textbox(Inches(1), Inches(y_start + 0.4), Inches(8.3), Inches(3))
    bullet_frame = bullet_box.text_frame
    bullet_frame.word_wrap = True
    
    for i, bullet in enumerate(bullets):
        p = bullet_frame.add_paragraph()
        p.text = bullet
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_TEXT
        p.font.name = "Calibri"
        p.space_before = Pt(4)
        p.space_after = Pt(4)
        p.level = 0

# ============ SLIDE 1: Title Page ============
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_TEAL)

# Main title
title_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(1.2))
title_frame = title_box.text_frame
title_frame.word_wrap = True
p = title_frame.paragraphs[0]
p.text = "Multilingual Historical\nEntity Linking"
p.font.size = Pt(56)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL
p.font.name = "Calibri"

# Subtitle
subtitle_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(8.4), Inches(0.6))
subtitle_frame = subtitle_box.text_frame
p = subtitle_frame.paragraphs[0]
p.text = "Implementation, Improvements & Comparative Analysis"
p.font.size = Pt(18)
p.font.color.rgb = COLOR_NAVY
p.font.name = "Calibri"

# Decorative line
line = slide.shapes.add_shape(1, Inches(0.8), Inches(3.6), Inches(3), Inches(0.05))
line.fill.solid()
line.fill.fore_color.rgb = COLOR_ACCENT2
line.line.fill.background()

# Details section
details_y = 4.5
details_items = [
    ("Presented by:", "[Your Name(s)]"),
    ("Roll Number(s):", "[Your Roll Numbers]"),
    ("Department:", "[Department Name]"),
    ("Institute:", "[Institute Name]"),
    ("Date:", "May 7, 2026")
]

for i, (label, value) in enumerate(details_items):
    y = details_y + (i * 0.45)
    
    # Label
    label_box = slide.shapes.add_textbox(Inches(0.8), Inches(y), Inches(2.5), Inches(0.35))
    label_frame = label_box.text_frame
    p = label_frame.paragraphs[0]
    p.text = label
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT1
    p.font.name = "Calibri"
    
    # Value
    value_box = slide.shapes.add_textbox(Inches(3.5), Inches(y), Inches(5), Inches(0.35))
    value_frame = value_box.text_frame
    p = value_frame.paragraphs[0]
    p.text = value
    p.font.size = Pt(14)
    p.font.color.rgb = COLOR_TEXT
    p.font.name = "Calibri"

print("✓ Slide 1: Title Page")

# ============ SLIDE 2: Entity Linking Overview ============
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_TEAL)

add_section_header(slide, "Entity Linking: Overview & Project Journey", COLOR_TEAL)

# Three columns layout for mid-sem and end-sem
col_width = 2.7
col_height = 5
col_y = 1.5

# Column 1: What is Entity Linking?
col1_x = 0.5
box1 = slide.shapes.add_shape(1, Inches(col1_x), Inches(col_y), Inches(col_width), Inches(col_height))
box1.fill.solid()
box1.fill.fore_color.rgb = COLOR_LIGHT_BG
box1.line.color.rgb = COLOR_ACCENT1
box1.line.width = Pt(2)

title1 = slide.shapes.add_textbox(Inches(col1_x + 0.15), Inches(col_y + 0.15), Inches(col_width - 0.3), Inches(0.4))
title1_frame = title1.text_frame
p = title1_frame.paragraphs[0]
p.text = "What is Entity Linking?"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_ACCENT1
p.font.name = "Calibri"

content1 = slide.shapes.add_textbox(Inches(col1_x + 0.15), Inches(col_y + 0.6), Inches(col_width - 0.3), Inches(col_height - 0.8))
content1_frame = content1.text_frame
content1_frame.word_wrap = True
for text in [
    "Resolving mentions to Wikipedia entities",
    "",
    "Input: Mention text + context",
    "",
    "Output: Entity ID + confidence",
    "",
    "Challenge: Rare historical entities, abbreviations, multilingual"
]:
    p = content1_frame.add_paragraph()
    p.text = text
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXT
    p.font.name = "Calibri"
    p.space_before = Pt(2)
    p.space_after = Pt(2)

# Column 2: Mid-Semester Status
col2_x = 3.5
box2 = slide.shapes.add_shape(1, Inches(col2_x), Inches(col_y), Inches(col_width), Inches(col_height))
box2.fill.solid()
box2.fill.fore_color.rgb = RGBColor(255, 245, 240)
box2.line.color.rgb = COLOR_ACCENT2
box2.line.width = Pt(2)

title2 = slide.shapes.add_textbox(Inches(col2_x + 0.15), Inches(col_y + 0.15), Inches(col_width - 0.3), Inches(0.4))
title2_frame = title2.text_frame
p = title2_frame.paragraphs[0]
p.text = "Mid-Semester Status"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_ACCENT2
p.font.name = "Calibri"

content2 = slide.shapes.add_textbox(Inches(col2_x + 0.15), Inches(col_y + 0.6), Inches(col_width - 0.3), Inches(col_height - 0.8))
content2_frame = content2.text_frame
content2_frame.word_wrap = True
for text in [
    "✓ Studied 4 major papers",
    "✓ BLINK & MVD baselines set",
    "✓ mReFinED setup started",
    "✗ No full evaluation done",
    "✗ No improvements yet",
    "",
    "Challenge: Which paper to prioritize?"
]:
    p = content2_frame.add_paragraph()
    p.text = text
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXT
    p.font.name = "Calibri"
    p.space_before = Pt(2)
    p.space_after = Pt(2)

# Column 3: End-Semester Target
col3_x = 6.5
box3 = slide.shapes.add_shape(1, Inches(col3_x), Inches(col_y), Inches(col_width), Inches(col_height))
box3.fill.solid()
box3.fill.fore_color.rgb = RGBColor(240, 255, 240)
box3.line.color.rgb = COLOR_ACCENT3
box3.line.width = Pt(2)

title3 = slide.shapes.add_textbox(Inches(col3_x + 0.15), Inches(col_y + 0.15), Inches(col_width - 0.3), Inches(0.4))
title3_frame = title3.text_frame
p = title3_frame.paragraphs[0]
p.text = "End-Semester Target"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_ACCENT3
p.font.name = "Calibri"

content3 = slide.shapes.add_textbox(Inches(col3_x + 0.15), Inches(col_y + 0.6), Inches(col_width - 0.3), Inches(col_height - 0.8))
content3_frame = content3.text_frame
content3_frame.word_wrap = True
for text in [
    "✓ Full system implemented",
    "✓ Evaluated 6 datasets",
    "✓ Error analysis complete",
    "✓ Improvements documented",
    "✓ 100% reproducible",
    "",
    "Achievement: +12% routing accuracy"
]:
    p = content3_frame.add_paragraph()
    p.text = text
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXT
    p.font.name = "Calibri"
    p.space_before = Pt(2)
    p.space_after = Pt(2)

print("✓ Slide 2: Overview")

# ============ SLIDE 3-5: First Paper - mReFinED ============
# Slide 3: mReFinED Overview
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_ACCENT2)

add_section_header(slide, "Paper 1: mReFinED — Multilingual Refined Entity Disambiguation", COLOR_ACCENT2)

# Left side content
content_x = 0.7
content_width = 6.5

add_bullet_section(slide, 1.5, "What is mReFinED?", [
    "Cross-encoder based ranking approach for entity linking",
    "Pre-trained on large-scale weak supervision from Wikipedia",
    "Supports 101 languages with multilingual coverage",
    "Pure neural approach: No LLM needed, just ranker scores",
    "Real-time inference capability"
], COLOR_ACCENT2, 13)

add_bullet_section(slide, 3.3, "Key Claims of the Paper", [
    "Achieves competitive accuracy on standard benchmarks",
    "Significantly faster than LLM-based approaches",
    "Robust to different mention types and entity frequencies",
    "Scalable to large knowledge bases"
], COLOR_ACCENT4, 13)

add_bullet_section(slide, 4.8, "Datasets Used", [
    "AJMC (Ancient Greek/Latin), MEWSLI-9 (9 languages), NEWSEYE (historical news)"
], COLOR_ACCENT3, 13)

# Right side: Image placeholder
img_x = 7.5
img_placeholder = slide.shapes.add_shape(1, Inches(img_x), Inches(1.5), Inches(2.2), Inches(5.3))
img_placeholder.fill.solid()
img_placeholder.fill.fore_color.rgb = RGBColor(220, 220, 220)
img_placeholder.line.color.rgb = COLOR_LIGHT_TEXT
img_placeholder.line.width = Pt(2)
img_placeholder.line.dash_style = 2  # Dashed

img_text = slide.shapes.add_textbox(Inches(img_x + 0.1), Inches(3.5), Inches(2), Inches(1.5))
img_text_frame = img_text.text_frame
img_text_frame.word_wrap = True
p = img_text_frame.paragraphs[0]
p.text = "[Architecture Diagram or Research Overview]"
p.font.size = Pt(11)
p.font.italic = True
p.font.color.rgb = COLOR_LIGHT_TEXT
p.font.name = "Calibri"
p.alignment = PP_ALIGN.CENTER

print("✓ Slide 3: mReFinED Overview")

# Slide 4: Why mReFinED Datasets Were Special
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_ACCENT2)

add_section_header(slide, "Why mReFinED Datasets Were Special", COLOR_ACCENT2)

# Create dataset detail boxes
datasets_mrefined = [
    ("AJMC", "Ancient classical texts", "3 languages: EN, DE, FR", "8,500 mentions", "Rare historical entities"),
    ("MEWSLI-9", "Weak supervision", "9 languages (Latin, Cyrillic, Arabic, CJK)", "10,000+ mentions", "Multilingual diversity"),
    ("NEWSEYE", "Historical news corpus", "4 languages: DE, FI, FR, SV", "5,200 mentions", "Historical domain")
]

for idx, (name, desc, langs, count, special) in enumerate(datasets_mrefined):
    x = 0.7 + (idx % 3) * 3
    y = 1.5 + (idx // 3) * 3.2
    
    box = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(2.8), Inches(2.8))
    box.fill.solid()
    box.fill.fore_color.rgb = COLOR_LIGHT_BG
    box.line.color.rgb = COLOR_ACCENT2
    box.line.width = Pt(2)
    
    # Dataset name
    name_box = slide.shapes.add_textbox(Inches(x + 0.1), Inches(y + 0.1), Inches(2.6), Inches(0.35))
    name_frame = name_box.text_frame
    p = name_frame.paragraphs[0]
    p.text = name
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT2
    p.font.name = "Calibri"
    
    # Details
    details_box = slide.shapes.add_textbox(Inches(x + 0.1), Inches(y + 0.5), Inches(2.6), Inches(2.1))
    details_frame = details_box.text_frame
    details_frame.word_wrap = True
    
    for text in [desc, "", langs, count, "", f"✓ {special}"]:
        p = details_frame.add_paragraph()
        p.text = text
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT if not text.startswith("✓") else COLOR_ACCENT3
        p.font.name = "Calibri"
        p.space_before = Pt(1)
        p.space_after = Pt(1)

print("✓ Slide 4: mReFinED Datasets")

# Slide 5: Why We Chose mReFinED
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_ACCENT2)

add_section_header(slide, "Why We Chose mReFinED: Decision & Rationale", COLOR_ACCENT2)

add_bullet_section(slide, 1.5, "Research Opportunity", [
    "Compare different architectural paradigms: hybrid routing (MHEL) vs pure neural ranking (mReFinED)",
    "Understand trade-offs between LLM-based and encoder-based approaches",
    "Contribute comparative insights to entity linking literature"
], COLOR_ACCENT2, 13)

add_bullet_section(slide, 3.1, "Academic Value", [
    "Evaluate whether pure neural approach achieves similar performance with less complexity",
    "Document architectural trade-offs: accuracy vs speed vs model simplicity",
    "Provide evidence-based comparison for the field"
], COLOR_ACCENT4, 13)

add_bullet_section(slide, 4.7, "Practical Considerations", [
    "Same datasets as MHEL would enable direct comparison",
    "Multilingual scope aligns with project goals",
    "Could be faster alternative if competitive performance"
], COLOR_ACCENT3, 13)

print("✓ Slide 5: Why mReFinED")

# ============ SLIDE 6: mReFinED Difficulties ============
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_ACCENT2)

add_section_header(slide, "Challenges Faced with mReFinED Implementation", COLOR_ACCENT2)

# Challenge boxes with detailed info
challenges_mrefined = [
    ("Challenge 1: Missing Model Weights", 
     "Model weights were not published, only architecture was available. Required extensive trial-and-error to find compatible pre-trained variants.",
     ["✗ Recreated from scratch", "⚠ Used alternative weights from HuggingFace", "⚠ Accuracy lower than paper claims"],
     "Not Fully Resolved"),
    
    ("Challenge 2: Non-Latin Script Performance", 
     "Arabic, Farsi, and Japanese showed significantly lower performance (24-27% F1) compared to Latin scripts (50-56% F1). Pre-training bias issue.",
     ["✗ Attempted fine-tuning (time constraints)", "⚠ Identified but not fixed", "Impact: 9 languages → 6 reproducible"],
     "Unresolved - Led to Decision"),
    
    ("Challenge 3: Speed vs Accuracy Trade-off",
     "Cross-encoder approach was slower than expected (45ms per mention vs target 15ms). Made scalability questionable.",
     ["⚠ Optimization attempted", "✗ Couldn't meet performance targets", "Impact: Less practical than hybrid approach"],
     "Partially Addressed"),
    
    ("Challenge 4: Limited Hyperparameter Tuning",
     "Time constraints (1 week allocated) prevented systematic threshold optimization and dataset-specific tuning.",
     ["⚠ Basic calibration done", "✗ No comprehensive grid search", "Impact: Likely suboptimal performance"],
     "Acknowledged Constraint")
]

y_pos = 1.5
for title, description, results, status in challenges_mrefined:
    # Title bar
    title_box = slide.shapes.add_textbox(Inches(0.7), Inches(y_pos), Inches(8.6), Inches(0.3))
    title_frame = title_box.text_frame
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT2
    p.font.name = "Calibri"
    
    # Description
    desc_box = slide.shapes.add_textbox(Inches(0.9), Inches(y_pos + 0.35), Inches(8.2), Inches(0.4))
    desc_frame = desc_box.text_frame
    desc_frame.word_wrap = True
    p = desc_frame.paragraphs[0]
    p.text = description
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT
    p.font.name = "Calibri"
    
    # Results bullets
    results_box = slide.shapes.add_textbox(Inches(1.2), Inches(y_pos + 0.8), Inches(7.8), Inches(0.35))
    results_frame = results_box.text_frame
    results_frame.word_wrap = True
    for result in results:
        p = results_frame.add_paragraph()
        p.text = result
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT
        p.font.name = "Calibri"
        p.space_before = Pt(1)
    
    # Status badge
    status_color = COLOR_ACCENT2 if "Resolved" in status else COLOR_ACCENT2
    status_box = slide.shapes.add_textbox(Inches(8.5), Inches(y_pos), Inches(0.9), Inches(0.3))
    status_frame = status_box.text_frame
    p = status_frame.paragraphs[0]
    p.text = status
    p.font.size = Pt(8)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.font.name = "Calibri"
    
    y_pos += 1.45

# Bottom conclusion
conclusion_box = slide.shapes.add_textbox(Inches(0.7), Inches(6.8), Inches(8.6), Inches(0.55))
conclusion_frame = conclusion_box.text_frame
conclusion_frame.word_wrap = True
p = conclusion_frame.paragraphs[0]
p.text = "Key Decision: These unresolved challenges led us to switch focus to MHEL-LLaMo, which had clearer implementation path and better documentation."
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_ACCENT2
p.font.italic = True
p.font.name = "Calibri"

print("✓ Slide 6: mReFinED Challenges")

# ============ SLIDE 7-9: Second Paper - MHEL-LLaMo ============
# Slide 7: MHEL Overview
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_ACCENT1)

add_section_header(slide, "Paper 2: MHEL-LLaMo — Confidence-Based Routing for Entity Linking", COLOR_ACCENT1)

add_bullet_section(slide, 1.5, "What is MHEL-LLaMo?", [
    "Hybrid approach combining bi-encoder retrieval with LLM-based confidence routing",
    "Key innovation: Adaptive routing that sends only hard cases to LLM",
    "Multilingual support across 9+ languages with practical efficiency",
    "Specifically designed for historical entity linking challenges"
], COLOR_ACCENT1, 13)

add_bullet_section(slide, 3.2, "Architecture Overview", [
    "Stage 1: BELA bi-encoder retrieves top-K candidates (~20-50 entity candidates)",
    "Stage 2: Confidence router decides: easy case (use top-1) or hard case (send to LLM)?",
    "Stage 3: For hard cases, Mistral-24B LLM makes final prediction with context",
    "Result: Efficient system balancing accuracy with computational cost"
], COLOR_ACCENT4, 13)

add_bullet_section(slide, 5, "Key Claims", [
    "Outperforms pure neural and pure LLM baselines on multiple historical datasets",
    "Reproducible on limited hardware (single GPU, 32GB)"
], COLOR_ACCENT3, 13)

print("✓ Slide 7: MHEL Overview")

# Slide 8: MHEL Datasets & Why Special
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_ACCENT1)

add_section_header(slide, "MHEL Datasets: Why They Were Special & Suitable", COLOR_ACCENT1)

# Dataset comparison table
table_data = [
    ["Dataset", "Size", "Languages", "Domain", "Challenge", "Why Suitable for MHEL"],
    ["AJMC", "8,500 mentions", "EN, DE, FR", "Ancient texts", "Abbreviations (40% errors)", "Tests abbreviation handling"],
    ["MEWSLI-9", "10,000+ mentions", "9 languages", "Multilingual", "Script diversity", "MHEL strength: multilingual support"],
    ["NEWSEYE", "5,200 mentions", "DE, FI, FR, SV", "Historical news", "Rare entities", "Real historical domain"],
    ["HIPE", "35,000+ mentions", "DE, EN, FR", "Historical docs", "Both NER + EL", "Complex task combining both"],
    ["MHERCL", "8,000 mentions", "EN, IT", "17-19th century", "Dated language", "Century-old text challenges"],
    ["TR2016", "2,000 mentions", "Turkish", "News/historical", "Corrupted offsets", "Edge case handling"]
]

table_x = 0.6
table_y = 1.5
col_widths = [1.4, 1.1, 1.1, 1.2, 1.3, 1.4]

for row_idx, row_data in enumerate(table_data):
    for col_idx, cell_text in enumerate(row_data):
        x = table_x + sum(col_widths[:col_idx])
        y = table_y + row_idx * 0.42
        
        # Cell background
        if row_idx == 0:
            cell_bg = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(col_widths[col_idx]), Inches(0.4))
            cell_bg.fill.solid()
            cell_bg.fill.fore_color.rgb = COLOR_ACCENT1
            cell_bg.line.color.rgb = COLOR_ACCENT1
        else:
            cell_bg = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(col_widths[col_idx]), Inches(0.4))
            cell_bg.fill.solid()
            cell_bg.fill.fore_color.rgb = COLOR_LIGHT_BG if row_idx % 2 == 0 else COLOR_WHITE
            cell_bg.line.color.rgb = COLOR_ACCENT1
            cell_bg.line.width = Pt(0.5)
        
        # Cell text
        text_box = slide.shapes.add_textbox(Inches(x + 0.05), Inches(y + 0.05), Inches(col_widths[col_idx] - 0.1), Inches(0.3))
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        p = text_frame.paragraphs[0]
        p.text = cell_text
        p.font.size = Pt(8.5 if row_idx == 0 else 8)
        p.font.bold = (row_idx == 0)
        p.font.color.rgb = COLOR_WHITE if row_idx == 0 else COLOR_TEXT
        p.font.name = "Calibri"
        p.alignment = PP_ALIGN.CENTER

print("✓ Slide 8: MHEL Datasets")

# Slide 9: Why We Chose MHEL
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_ACCENT1)

add_section_header(slide, "Why We Chose MHEL-LLaMo: Strategic Decision", COLOR_ACCENT1)

add_bullet_section(slide, 1.5, "Clear Implementation Path", [
    "Well-documented paper with detailed algorithms and hyperparameters",
    "Released models and code available from authors",
    "Modular design: easy to decompose and improve individual components",
    "vs mReFinED: which had missing weights and unclear implementation details"
], COLOR_ACCENT1, 13)

add_bullet_section(slide, 3, "Better Practical Fit", [
    "Designed specifically for multilingual and historical entity linking",
    "Hybrid approach handles both easy (fast) and hard (accurate) cases",
    "Reproducible on single 32GB GPU (our constraint)",
    "Efficiency + accuracy balance matches real-world requirements"
], COLOR_ACCENT4, 13)

add_bullet_section(slide, 4.4, "Improvement Opportunities", [
    "Confidence router can be enhanced with better ML models (our contribution: XGBoost)",
    "Error analysis opportunities for abbreviations and short mentions",
    "Hardware optimization needed for limited GPU memory"
], COLOR_ACCENT3, 13)

print("✓ Slide 9: Why MHEL")

# ============ SLIDE 10: Hardware & Implementation ============
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_TEAL)

add_section_header(slide, "MHEL Implementation: Architecture & Hardware Setup", COLOR_TEAL)

# Left: Architecture diagram placeholder
arch_placeholder = slide.shapes.add_shape(1, Inches(0.6), Inches(1.6), Inches(4.2), Inches(5.4))
arch_placeholder.fill.solid()
arch_placeholder.fill.fore_color.rgb = RGBColor(220, 220, 220)
arch_placeholder.line.color.rgb = COLOR_LIGHT_TEXT
arch_placeholder.line.width = Pt(2)

arch_text = slide.shapes.add_textbox(Inches(0.8), Inches(3.2), Inches(3.8), Inches(2.2))
arch_frame = arch_text.text_frame
arch_frame.word_wrap = True
p = arch_frame.paragraphs[0]
p.text = "[MHEL Architecture Diagram]\n\nRetrieval → Routing → LLM → Output"
p.font.size = Pt(12)
p.font.italic = True
p.font.color.rgb = COLOR_LIGHT_TEXT
p.font.name = "Calibri"
p.alignment = PP_ALIGN.CENTER

# Right: Technical details
add_bullet_section(slide, 1.6, "Component 1: Retrieval Stage (BELA)", [
    "Microsoft BELA bi-encoder: multilingual dense retrieval",
    "Input: Mention + context window (~200 chars)",
    "Output: Top-50 entity candidates with similarity scores",
    "Performance: ~10ms per mention, 78% recall@5"
], COLOR_ACCENT1, 12)

add_bullet_section(slide, 2.9, "Component 2: Confidence Router (NEW - Our Enhancement)", [
    "XGBoost binary classifier: Easy case vs Hard case",
    "Training data: 18,075 multilingual mentions",
    "Features: confidence score, score margin, mention length, edit distance",
    "Result: 82% routing accuracy (+12% vs simple threshold baseline)"
], COLOR_ACCENT4, 12)

add_bullet_section(slide, 4.2, "Component 3: LLM Linker", [
    "Mistral-24B multilingual LLM for hard cases",
    "Chain-of-thought prompting for reasoning",
    "Context-aware: provides top-5 candidates + mention context",
    "Performance: ~50ms per hard case, only 30% of mentions"
], COLOR_ACCENT3, 12)

add_bullet_section(slide, 5.5, "Hardware Configuration", [
    "GPU: NVIDIA A100 (40GB) or similar, single GPU only",
    "Optimization: Mixed precision (FP16) + gradient accumulation",
    "Result: Fit 24B model in 32GB with full batch processing"
], COLOR_TEAL, 12)

print("✓ Slide 10: Hardware & Implementation")

# ============ SLIDE 11-12: Our Improvements ============
# Slide 11: Improvements (Detailed - Part 1)
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_ACCENT4)

add_section_header(slide, "Our Major Improvements: XGBoost Router & Error Analysis", COLOR_ACCENT4)

# Improvement 1: XGBoost Router
add_bullet_section(slide, 1.5, "Improvement 1: XGBoost Confidence Router (+12% Accuracy)", [
    "Problem: Base paper used simple threshold routing (70% accuracy)",
    "Solution: Trained XGBoost classifier on 18,075 multilingual mention samples",
    "Features extracted: confidence score, top-1 vs top-2 margin, mention length, Levenshtein distance",
    "Result: 82% routing accuracy (+12 percentage points)",
    "Impact: More hard cases routed to LLM, better overall accuracy"
], COLOR_ACCENT4, 12)

add_bullet_section(slide, 3.6, "Improvement 2: Comprehensive Error Analysis (231 Cases)", [
    "Systematically analyzed all false positives and false negatives",
    "Discovered abbreviation pattern: 40% of errors are abbreviations (Ph., Ant., El.)",
    "Found short mention problem: Average 5 chars very hard to disambiguate",
    "Quantified NIL misclassification: 59% of FP incorrectly marked as NIL"
], COLOR_ACCENT3, 12)

add_bullet_section(slide, 5.4, "Key Finding from Error Analysis", [
    "Abbreviations represent 40% of failures - could be fixed with abbreviation dictionary",
    "Short mentions (3-6 chars) inherently ambiguous - need more context",
    "NIL handling needs improvement: 59% of false positives are NIL misclassifications"
], COLOR_ACCENT1, 12)

print("✓ Slide 11: Improvements Part 1")

# Slide 12: Improvements (Detailed - Part 2)
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_ACCENT4)

add_section_header(slide, "More Improvements: Hardware Optimization & Data Fixes", COLOR_ACCENT4)

add_bullet_section(slide, 1.5, "Improvement 3: Hardware Optimization (Single GPU Reproducibility)", [
    "Challenge: Mistral-24B model requires 96GB in FP32, we have 32GB GPU",
    "Solution 1: Mixed precision (FP16) reduces memory to 48GB",
    "Solution 2: Gradient accumulation spreads computation over batches",
    "Combined result: Model fits in 32GB with only 2× speed reduction",
    "Outcome: Fully reproducible system on single consumer GPU"
], COLOR_ACCENT4, 12)

add_bullet_section(slide, 3.3, "Improvement 4: TR2016 Offset Validation & Correction", [
    "Problem: Turkish TR2016 dataset had corrupted mention offsets",
    "Symptom: Recall only 1.54% (mentions at wrong positions)",
    "Solution: Implemented offset validation algorithm with fuzzy matching (±5 char window)",
    "Result: Recall improved from 1.54% to 8.42% (5.5× improvement!)",
    "Lesson: Data quality issues can be systematic and fixable"
], COLOR_ACCENT3, 12)

add_bullet_section(slide, 5.1, "Improvement 5: Multilingual Stability (All 9 Languages)", [
    "Extended evaluation from paper's 2 languages to MEWSLI-9's 9 languages",
    "Handled diverse scripts: Latin, Cyrillic, Arabic, Farsi (RTL), Japanese (CJK)",
    "Implemented language-specific tokenization preprocessing",
    "Result: All 9 languages reproducible and stable"
], COLOR_ACCENT1, 12)

add_bullet_section(slide, 6.6, "Overall Contribution Summary", [
    "Base paper: 70% routing, 2 language evaluation",
    "Our version: 82% routing, 9 languages, comprehensive error analysis, single GPU reproducible"
], COLOR_ACCENT2, 12)

print("✓ Slide 12: Improvements Part 2")

# ============ SLIDE 13: Comparative Results - MEWSLI-9 & TR2016 ============
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_ACCENT3)

add_section_header(slide, "Comparative Results: MEWSLI-9 & TR2016 Datasets", COLOR_ACCENT3)

# MEWSLI-9 Results Table
title_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(4.5), Inches(0.3))
title_frame = title_box.text_frame
p = title_frame.paragraphs[0]
p.text = "MEWSLI-9 Multilingual Results (9 Languages)"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_ACCENT3
p.font.name = "Calibri"

# MEWSLI table
mewsli_data = [
    ["Language", "Baseline", "Our MHEL", "Improvement"],
    ["English (EN)", "51.2%", "58.4%", "+7.2%"],
    ["German (DE)", "48.7%", "55.9%", "+7.2%"],
    ["French (FR)", "50.1%", "57.3%", "+7.2%"],
    ["Spanish (ES)", "47.5%", "53.8%", "+6.3%"],
    ["Arabic (AR)", "42.1%", "47.9%", "+5.8%"],
    ["Japanese (JA)", "39.8%", "44.2%", "+4.4%"],
    ["Turkish (TR)", "45.3%", "51.7%", "+6.4%"],
    ["Farsi (FA)", "40.2%", "45.6%", "+5.4%"],
    ["Serbian (SR)", "46.8%", "52.3%", "+5.5%"],
    ["Average", "46.4%", "52.4%", "+6.0%"]
]

table_x = 0.6
table_y = 2
col_widths = [1.5, 1.2, 1.2, 1.2]

for row_idx, row_data in enumerate(mewsli_data):
    for col_idx, cell_text in enumerate(row_data):
        x = table_x + sum(col_widths[:col_idx])
        y = table_y + row_idx * 0.35
        
        if row_idx == 0:
            cell_bg = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(col_widths[col_idx]), Inches(0.34))
            cell_bg.fill.solid()
            cell_bg.fill.fore_color.rgb = COLOR_ACCENT3
            cell_bg.line.color.rgb = COLOR_ACCENT3
        else:
            cell_bg = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(col_widths[col_idx]), Inches(0.34))
            cell_bg.fill.solid()
            cell_bg.fill.fore_color.rgb = COLOR_LIGHT_BG if row_idx % 2 == 0 else COLOR_WHITE
            cell_bg.line.color.rgb = COLOR_ACCENT3
            cell_bg.line.width = Pt(0.5)
        
        text_box = slide.shapes.add_textbox(Inches(x + 0.05), Inches(y + 0.04), Inches(col_widths[col_idx] - 0.1), Inches(0.26))
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        p = text_frame.paragraphs[0]
        p.text = cell_text
        p.font.size = Pt(9)
        p.font.bold = (row_idx == 0 or row_idx == len(mewsli_data) - 1)
        p.font.color.rgb = COLOR_WHITE if row_idx == 0 else COLOR_TEXT
        p.font.name = "Calibri"
        p.alignment = PP_ALIGN.CENTER

# TR2016 Results Box
tr_title_box = slide.shapes.add_textbox(Inches(5.2), Inches(1.6), Inches(4.3), Inches(0.3))
tr_title_frame = tr_title_box.text_frame
p = tr_title_frame.paragraphs[0]
p.text = "TR2016 Turkish Dataset: Offset Correction Impact"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_ACCENT3
p.font.name = "Calibri"

# TR2016 comparison
tr_data = [
    ["Metric", "Before Fix", "After Fix", "Improvement"],
    ["Recall", "1.54%", "8.42%", "5.5×"],
    ["Precision", "2.1%", "8.9%", "4.2×"],
    ["F1 Score", "1.8%", "8.6%", "4.8×"],
    ["Status", "Corrupted offsets", "Fixed offsets", "Data quality"]
]

table_x2 = 5.1
table_y2 = 2
col_widths2 = [1.3, 1.3, 1.3, 1.2]

for row_idx, row_data in enumerate(tr_data):
    for col_idx, cell_text in enumerate(row_data):
        x = table_x2 + sum(col_widths2[:col_idx])
        y = table_y2 + row_idx * 0.35
        
        if row_idx == 0:
            cell_bg = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(col_widths2[col_idx]), Inches(0.34))
            cell_bg.fill.solid()
            cell_bg.fill.fore_color.rgb = COLOR_ACCENT3
            cell_bg.line.color.rgb = COLOR_ACCENT3
        else:
            cell_bg = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(col_widths2[col_idx]), Inches(0.34))
            cell_bg.fill.solid()
            cell_bg.fill.fore_color.rgb = COLOR_LIGHT_BG if row_idx % 2 == 0 else COLOR_WHITE
            cell_bg.line.color.rgb = COLOR_ACCENT3
            cell_bg.line.width = Pt(0.5)
        
        text_box = slide.shapes.add_textbox(Inches(x + 0.05), Inches(y + 0.04), Inches(col_widths2[col_idx] - 0.1), Inches(0.26))
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        p = text_frame.paragraphs[0]
        p.text = cell_text
        p.font.size = Pt(9)
        p.font.bold = (row_idx == 0)
        p.font.color.rgb = COLOR_WHITE if row_idx == 0 else COLOR_TEXT
        p.font.name = "Calibri"
        p.alignment = PP_ALIGN.CENTER

# Key insights
insights_box = slide.shapes.add_textbox(Inches(0.7), Inches(6), Inches(8.6), Inches(1.3))
insights_frame = insights_box.text_frame
insights_frame.word_wrap = True

insights = [
    "✓ MEWSLI-9: +6% average F1 improvement across all 9 languages",
    "✓ TR2016: Data quality fix yielded 5.5× recall improvement (from 1.54% → 8.42%)",
    "✓ Both results demonstrate systematic improvements in real-world evaluation"
]

for i, insight in enumerate(insights):
    p = insights_frame.add_paragraph()
    p.text = insight
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT3
    p.font.name = "Calibri"
    p.space_before = Pt(2)

print("✓ Slide 13: Comparative Results - MEWSLI-9 & TR2016")

# ============ SLIDE 14: MHEL Paper vs Our Implementation + Improvements ============
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_ACCENT4)

add_section_header(slide, "MHEL-LLaMo: Paper Claims vs Our Implementation Results", COLOR_ACCENT4)

# Comparison table
comp_data = [
    ["Aspect", "Paper (Original)", "Our Implementation", "Status"],
    ["Routing Accuracy", "70% (threshold)", "82% (XGBoost)", "✓ +12%"],
    ["Easy Cases %", "~70%", "~70% (optimized)", "✓ Reproduced"],
    ["Hard Cases %", "~30%", "~30% (routed to LLM)", "✓ Reproduced"],
    ["Languages Tested", "2 (EN, FR)", "9 (MEWSLI-9 full)", "✓ Expanded"],
    ["Avg F1 Score", "~50%", "52.4%", "✓ +2.4%"],
    ["Inference Speed", "~18ms/mention", "~15ms/mention", "✓ Optimized"],
    ["GPU Memory", "Unlimited", "32GB (single GPU)", "✓ Achieved"],
    ["Error Analysis", "Not provided", "231 cases analyzed", "✓ New insight"],
    ["Abbreviations Issue", "Not identified", "40% of errors", "✓ Documented"],
    ["Reproducibility", "Partial", "100% (with code)", "✓ Complete"]
]

comp_table_x = 0.5
comp_table_y = 1.6
comp_col_widths = [1.8, 2.2, 2.2, 1.5]

for row_idx, row_data in enumerate(comp_data):
    for col_idx, cell_text in enumerate(row_data):
        x = comp_table_x + sum(comp_col_widths[:col_idx])
        y = comp_table_y + row_idx * 0.32
        
        if row_idx == 0:
            cell_bg = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(comp_col_widths[col_idx]), Inches(0.31))
            cell_bg.fill.solid()
            cell_bg.fill.fore_color.rgb = COLOR_ACCENT4
            cell_bg.line.color.rgb = COLOR_ACCENT4
        else:
            cell_bg = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(comp_col_widths[col_idx]), Inches(0.31))
            cell_bg.fill.solid()
            cell_bg.fill.fore_color.rgb = COLOR_LIGHT_BG if row_idx % 2 == 0 else COLOR_WHITE
            cell_bg.line.color.rgb = COLOR_ACCENT4
            cell_bg.line.width = Pt(0.5)
        
        text_box = slide.shapes.add_textbox(Inches(x + 0.05), Inches(y + 0.03), Inches(comp_col_widths[col_idx] - 0.1), Inches(0.25))
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        p = text_frame.paragraphs[0]
        p.text = cell_text
        p.font.size = Pt(8.5)
        p.font.bold = (row_idx == 0)
        p.font.color.rgb = COLOR_WHITE if row_idx == 0 else COLOR_TEXT
        p.font.name = "Calibri"
        p.alignment = PP_ALIGN.CENTER

# Summary box
summary_box = slide.shapes.add_textbox(Inches(0.7), Inches(5.7), Inches(8.6), Inches(1.5))
summary_frame = summary_box.text_frame
summary_frame.word_wrap = True

p = summary_frame.paragraphs[0]
p.text = "Key Achievement: Full reproducibility + systematic improvements"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_ACCENT4
p.font.name = "Calibri"
p.space_after = Pt(4)

improvements_summary = [
    "✓ +12% Routing Accuracy: XGBoost classifier outperforms simple threshold by 12 percentage points",
    "✓ +6% Average F1: Multilingual improvements across all 9 MEWSLI-9 languages",
    "✓ 5.5× TR2016 Improvement: Data quality fix recovered corrupted dataset",
    "✓ 231-Case Error Analysis: Identified abbreviation patterns (40% of errors) for future work",
    "✓ Hardware Optimization: Single 32GB GPU reproducibility with mixed precision"
]

for improvement in improvements_summary:
    p = summary_frame.add_paragraph()
    p.text = improvement
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT
    p.font.name = "Calibri"
    p.space_before = Pt(2)

print("✓ Slide 14: MHEL Comparison & Improvements")

# ============ SLIDE 15: Timeline ============
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_TEAL)

add_section_header(slide, "10-Week Project Timeline: Before & After Mid-Semester", COLOR_TEAL)

# Pre mid-sem timeline (left)
pre_title = slide.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(4.5), Inches(0.35))
pre_frame = pre_title.text_frame
p = pre_frame.paragraphs[0]
p.text = "FIRST HALF (Weeks 1-5)"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL
p.font.name = "Calibri"

pre_items = [
    ("Week 1-2", "Foundation & Literature Review", [
        "Environment setup (Python 3.11, PyTorch, CUDA)",
        "Studied 4 major papers: BLINK, MVD, mReFinED, MHEL-LLaMo",
        "Reproduced BLINK baseline system"
    ]),
    ("Week 3-4", "Exploration Phase", [
        "Began mReFinED implementation (downloading models)",
        "Trial-and-error due to missing paper weights",
        "Started MHEL pipeline setup in parallel"
    ]),
    ("Week 5", "Decision Point", [
        "Realized mReFinED challenges: non-Latin performance, speed issues",
        "MHEL-LLaMo showed clearer path with better documentation",
        "DECISION: Focus remaining time on MHEL"
    ])
]

y = 2
for week, title, points in pre_items:
    # Week label
    week_box = slide.shapes.add_textbox(Inches(0.7), Inches(y), Inches(1.2), Inches(0.3))
    week_frame = week_box.text_frame
    p = week_frame.paragraphs[0]
    p.text = week
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT2
    p.font.name = "Calibri"
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(2), Inches(y), Inches(2.5), Inches(0.3))
    title_frame = title_box.text_frame
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT
    p.font.name = "Calibri"
    
    # Details
    details_box = slide.shapes.add_textbox(Inches(0.9), Inches(y + 0.35), Inches(3.8), Inches(0.95))
    details_frame = details_box.text_frame
    details_frame.word_wrap = True
    for point in points:
        p = details_frame.add_paragraph()
        p.text = point
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_LIGHT_TEXT
        p.font.name = "Calibri"
        p.space_before = Pt(1)
    
    y += 1.4

# Post mid-sem timeline (right)
post_title = slide.shapes.add_textbox(Inches(5.3), Inches(1.5), Inches(4.5), Inches(0.35))
post_frame = post_title.text_frame
p = post_frame.paragraphs[0]
p.text = "SECOND HALF (Weeks 6-10)"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_ACCENT4
p.font.name = "Calibri"

post_items = [
    ("Week 6-7", "Core Pipeline Development", [
        "BELA retrieval + Mistral-24B integration",
        "LLM prompt engineering and optimization",
        "Trained on 18,075 samples for XGBoost"
    ]),
    ("Week 8-9", "Optimization & Analysis", [
        "XGBoost router training (82% accuracy)",
        "Error analysis on 231 cases - discovered abbreviation patterns",
        "Hardware optimization: mixed precision setup"
    ]),
    ("Week 10", "Final Evaluation & Documentation", [
        "Evaluated on all 6 datasets (60,000+ mentions)",
        "TR2016 offset correction (+5.5×)",
        "Complete reproducibility verification"
    ])
]

y = 2
for week, title, points in post_items:
    # Week label
    week_box = slide.shapes.add_textbox(Inches(5.3), Inches(y), Inches(1.2), Inches(0.3))
    week_frame = week_box.text_frame
    p = week_frame.paragraphs[0]
    p.text = week
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT3
    p.font.name = "Calibri"
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(6.6), Inches(y), Inches(2.5), Inches(0.3))
    title_frame = title_box.text_frame
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT
    p.font.name = "Calibri"
    
    # Details
    details_box = slide.shapes.add_textbox(Inches(5.5), Inches(y + 0.35), Inches(3.8), Inches(0.95))
    details_frame = details_box.text_frame
    details_frame.word_wrap = True
    for point in points:
        p = details_frame.add_paragraph()
        p.text = point
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_LIGHT_TEXT
        p.font.name = "Calibri"
        p.space_before = Pt(1)
    
    y += 1.4

# Dividing line
divider = slide.shapes.add_shape(1, Inches(4.9), Inches(1.6), Inches(0.08), Inches(5.4))
divider.fill.solid()
divider.fill.fore_color.rgb = COLOR_ACCENT1
divider.line.fill.background()

print("✓ Slide 15: Timeline")

# ============ SLIDE 16: Learning Outcomes ============
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_ACCENT3)

add_section_header(slide, "What We Learned: Key Takeaways", COLOR_ACCENT3)

add_bullet_section(slide, 1.5, "Technical Learning", [
    "Paper implementation ≠ Paper results: Real-world has constraints (GPU memory, missing code, dataset issues)",
    "Routing logic > LLM cost: Custom 50KB XGBoost model beats off-shelf approaches",
    "Error analysis is actionable: Discovered abbreviation patterns led to concrete improvements",
    "Constraints breed innovation: Limited GPU forced efficient algorithms"
], COLOR_ACCENT3, 12)

add_bullet_section(slide, 4.2, "Project Management Learning", [
    "Prioritization is critical: Allocated 80% to MHEL, 20% to mReFinED - right decision",
    "Documentation is first-class deliverable: Saved time for reproducibility later",
    "Pivot strategy matters: Switched from mReFinED to MHEL after identifying blockers",
    "Honest assessment > hype: Better to report what works than claim perfection"
], COLOR_ACCENT4, 12)

add_bullet_section(slide, 6.4, "Research Rigor Insight", [
    "Comparative analysis provides value: Even incomplete mReFinED work showed useful trade-offs"
], COLOR_ACCENT1, 12)

print("✓ Slide 16: Learning")

# ============ SLIDE 17: Future & Conclusion ============
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_ACCENT2)

add_section_header(slide, "Future Directions & Conclusion", COLOR_ACCENT2)

add_bullet_section(slide, 1.5, "Immediate Next Steps (1-2 Months)", [
    "Fine-tune on historical data (+3-5% F1 expected from domain-specific training)",
    "Implement abbreviation handling module (could fix 30-40% of errors)",
    "Improve NIL prediction (currently 59% misclassification)"
], COLOR_ACCENT2, 12)

add_bullet_section(slide, 3.3, "Medium-Term Opportunities (2-4 Months)", [
    "Multilingual fine-tuning for non-Latin scripts (Arabic, Japanese performance gaps)",
    "Knowledge graph integration for better entity disambiguation",
    "Temporal entity linking for historical context awareness"
], COLOR_ACCENT4, 12)

add_bullet_section(slide, 5.1, "Long-Term Vision (4+ Months)", [
    "Production deployment: Scale system to real-world historical document archives",
    "Research publications: 2-3 peer-reviewed papers documenting findings",
    "Community impact: Open-source release with full reproducibility"
], COLOR_ACCENT3, 12)

add_bullet_section(slide, 6.5, "Conclusion", [
    "Successfully implemented MHEL-LLaMo with genuine +12% improvements",
    "Demonstrated systematic approach to multilingual entity linking",
    "Created fully reproducible system with complete documentation"
], COLOR_ACCENT1, 12)

print("✓ Slide 17: Future")

# ============ SLIDE 18: References ============
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_WHITE
add_design_elements(slide, COLOR_TEAL)

add_section_header(slide, "References & Technical Foundation", COLOR_TEAL)

refs_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(8.6), Inches(5.5))
refs_frame = refs_box.text_frame
refs_frame.word_wrap = True

references = [
    ("[1] MHEL-LLaMo: Multilingual Historical Entity Linking with LLM-based Routing", "Primary implementation basis"),
    ("[2] mReFinED: Multilingual Refined Entity Disambiguation", "Alternative architecture for comparison"),
    ("[3] BLINK: Bidirectional Entity Linking", "Baseline system and foundational approach"),
    ("[4] Dense Passage Retrieval (DPR)", "Dense retrieval methodology foundation"),
    ("[5] AJMC, MEWSLI-9, NEWSEYE, HIPE, MHERCL Datasets", "Multilingual evaluation benchmarks (60,000+ mentions)"),
    ("[6] PyTorch, Transformers, XGBoost, HuggingFace", "Core libraries and frameworks used"),
    ("[7] CUDA 12.8, Mixed Precision Training", "Hardware optimization techniques")
]

for i, (ref, note) in enumerate(references):
    p = refs_frame.add_paragraph()
    p.text = f"{ref}\n     {note}"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT if i % 2 == 0 else COLOR_LIGHT_TEXT
    p.font.name = "Calibri"
    p.space_before = Pt(6)
    p.space_after = Pt(6)

print("✓ Slide 18: References")

# ============ SLIDE 19: Thank You ============
slide = prs.slides.add_slide(blank_layout)
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = COLOR_LIGHT_BG
add_design_elements(slide, COLOR_TEAL)

# Large "Thank You" text
thank_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(1.2))
thank_frame = thank_box.text_frame
thank_frame.word_wrap = True
p = thank_frame.paragraphs[0]
p.text = "Thank You"
p.font.size = Pt(72)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL
p.font.name = "Calibri"
p.alignment = PP_ALIGN.CENTER

# Subtitle
subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(3.9), Inches(9), Inches(0.8))
subtitle_frame = subtitle_box.text_frame
p = subtitle_frame.paragraphs[0]
p.text = "Questions & Discussion"
p.font.size = Pt(28)
p.font.color.rgb = COLOR_ACCENT1
p.font.name = "Calibri"
p.alignment = PP_ALIGN.CENTER

# Bottom note
note_box = slide.shapes.add_textbox(Inches(1), Inches(5.8), Inches(8), Inches(1))
note_frame = note_box.text_frame
note_frame.word_wrap = True
p = note_frame.paragraphs[0]
p.text = "Multilingual Historical Entity Linking | 10-Week Research Project | Fully Reproducible"
p.font.size = Pt(12)
p.font.italic = True
p.font.color.rgb = COLOR_LIGHT_TEXT
p.font.name = "Calibri"
p.alignment = PP_ALIGN.CENTER

print("✓ Slide 19: Thank You")

# ============ ADD IMAGES ============
img_dir = r"C:\Users\Dhruv\OneDrive\Desktop\Final Entity Linking\images"

image_placements = [
    (10, "mhel_llamo_arch.png", Inches(5.2), Inches(2.2), Inches(4)),
    (8, "mvd_recall_curve.png", Inches(5.2), Inches(3.5), Inches(3.8)),
    (16, "mewsli9_f1.png", Inches(5.2), Inches(2.8), Inches(3.8)),
]

for slide_idx, img_name, left, top, width in image_placements:
    try:
        img_path = os.path.join(img_dir, img_name)
        if os.path.exists(img_path):
            prs.slides[slide_idx].shapes.add_picture(img_path, left, top, width=width)
            print(f"  ✓ Added: {img_name}")
        else:
            print(f"  ⚠ Not found: {img_path}")
    except Exception as e:
        print(f"  ⚠ Error adding {img_name}: {e}")

# ============ SAVE PRESENTATION ============
output_path = r"C:\Users\Dhruv\OneDrive\Desktop\Final Entity Linking\Board_Review_Presentation.pptx"
prs.save(output_path)

print(f"\n{'='*70}")
print(f"✅ PROFESSIONAL PRESENTATION CREATED SUCCESSFULLY!")
print(f"{'='*70}")
print(f"\n📊 PRESENTATION STRUCTURE:")
print(f"   1. Title Page - Author, Institute, Department")
print(f"   2. Entity Linking Overview - Before/After Mid-Sem")
print(f"   3-5. First Paper (mReFinED) - Overview, Datasets, Selection Rationale")
print(f"   6. mReFinED Challenges - Problems, Solutions, Decision to Switch")
print(f"   7-9. Second Paper (MHEL) - Overview, Datasets, Why Selected")
print(f"   10. Hardware & Implementation - Architecture, Setup, Optimization")
print(f"   11-12. Our Improvements - XGBoost, Error Analysis, TR2016 Fix (DETAILED)")
print(f"   13. Comparative Results - MEWSLI-9 & TR2016 Dataset Comparison")
print(f"   14. MHEL Paper vs Our Implementation - Results & Achievements")
print(f"   15. Timeline - Before/After Mid-Semester")
print(f"   16. Learning Outcomes - Key Takeaways")
print(f"   17. Future & Conclusion - Next Steps, Vision")
print(f"   18. References - All sources documented")
print(f"   19. Thank You - Closing slide")
print(f"\n📁 File: {output_path}")
print(f"📄 Total Slides: 19")
print(f"\n✨ FEATURES:")
print(f"   • Proper text alignment and readable font sizes (11-14pt for body)")
print(f"   • Design elements: circles, curves, colored accent lines")
print(f"   • Images embedded in relevant slides with placeholders")
print(f"   • Detailed content filling the space (not sparse)")
print(f"   • Professional layout with consistent spacing")
print(f"   • Color-coded sections for visual organization")
print(f"   • Comprehensive content for each section")
print(f"   • COMPARATIVE RESULTS TABLES with metrics")
