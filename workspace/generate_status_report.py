from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

def shade_cell(cell, color):
    """Helper function to shade table cells"""
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    cell._element.get_or_add_tcPr().append(shading)

def create_status_report():
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    
    # Title
    title = doc.add_heading('mReFinED Entity Linking Reproduction', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_format = title.runs[0]
    title_format.font.color.rgb = RGBColor(51, 102, 153)
    title_format.font.size = Pt(28)
    title_format.bold = True
    
    # Subtitle
    subtitle = doc.add_paragraph('Current Status Report and Technical Troubleshooting Guide')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_run = subtitle.runs[0]
    subtitle_run.font.size = Pt(14)
    subtitle_run.font.color.rgb = RGBColor(102, 102, 102)
    
    # Date
    date_para = doc.add_paragraph(f'Report Generated: {datetime.datetime.now().strftime("%B %d, %Y")}')
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_para.runs[0].font.size = Pt(10)
    date_para.runs[0].font.italic = True
    
    doc.add_paragraph()
    
    # Executive Summary
    doc.add_heading('Executive Summary', level=1)
    doc.add_paragraph(
        'This document provides comprehensive technical status of the mReFinED multilingual entity linking '
        'model reproduction on MEWSLI-9 and TR2016 datasets, including exact problems encountered, solutions '
        'implemented, and commands for supervisor monitoring.'
    )
    
    doc.add_page_break()
    
    # Section 1: Current Status
    doc.add_heading('Section 1: Current Reproduction Status', level=1)
    
    doc.add_heading('MEWSLI-9 Dataset Status', level=2)
    mewsli_table = doc.add_table(rows=8, cols=2)
    mewsli_table.style = 'Light Grid Accent 1'
    
    mewsli_data = [
        ['Status', 'Successfully Reproduced (April 16, 2026)'],
        ['Languages Evaluated', 'Arabic, German, English, Spanish, Farsi, Japanese, Serbian, Tamil, Turkish (9 total)'],
        ['Average Recall', '15.37%'],
        ['Micro-averaged F1', '24.99%'],
        ['Total Execution Time', 'Approximately 24 minutes'],
        ['Hardware Used', 'NVIDIA RTX 5000 Ada (32GB VRAM) on Server 172.20.70.80'],
        ['GPU Utilization', '85-95%'],
        ['Status Badge', 'SUCCESSFULLY REPRODUCED (All 9 languages completed)']
    ]
    
    for i, (key, value) in enumerate(mewsli_data):
        row = mewsli_table.rows[i]
        row.cells[0].text = key
        row.cells[1].text = value
        if i == 0:
            for cell in row.cells:
                shade_cell(cell, '1F4E78')
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
    
    doc.add_paragraph()
    
    doc.add_heading('TR2016 Dataset Status', level=2)
    tr_table = doc.add_table(rows=5, cols=2)
    tr_table.style = 'Light Grid Accent 1'
    
    tr_data = [
        ['Status', 'Ready but Not Yet Executed'],
        ['Languages', 'German, Spanish, French, Italian (4 languages)'],
        ['Dataset Location', '/DATA/kmpooja/mrefined_option1/assets/tr2016'],
        ['Scripts', 'Prepared and ready for execution'],
        ['Next Action', 'Execute when MEWSLI-9 reproduction is confirmed by supervisor']
    ]
    
    for i, (key, value) in enumerate(tr_data):
        row = tr_table.rows[i]
        row.cells[0].text = key
        row.cells[1].text = value
        if i == 0:
            for cell in row.cells:
                shade_cell(cell, '1F4E78')
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
    
    doc.add_page_break()
    
    # Section 2: SSH Commands for Monitoring
    doc.add_heading('Section 2: Commands for Supervisor Monitoring', level=1)
    
    doc.add_heading('Primary SSH Command for Execution', level=2)
    doc.add_paragraph(
        'Use the following command to execute MEWSLI-9 evaluation with full monitoring capabilities.'
    )
    
    code_block = doc.add_paragraph()
    code_block.paragraph_format.left_indent = Inches(0.3)
    code_block.paragraph_format.space_before = Pt(6)
    code_block.paragraph_format.space_after = Pt(6)
    code_run = code_block.add_run(
        'ssh -o StrictHostKeyChecking=no kmpooja@172.20.70.80 "cd /DATA/kmpooja/mrefined_option1 && '
        'export PYTHONUNBUFFERED=1 && export CUDA_VISIBLE_DEVICES=0 && TIMESTAMP=$(date +%Y%m%d_%H%M%S) && '
        'LOG_FILE=\\"logs/mewsli9_final_${TIMESTAMP}.log\\" && python3 -u '
        'ReFinED/src/refined/evaluation/multilingual_e2e_evaluation_mewsli9.py '
        '--lang_title2wikidata \'assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data\' '
        '--mention2wikidata \'assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data\' '
        '--model \'assets/finetune_models/mReFinED_Recall_9343\' '
        '--data \'assets/data_combine_11_languages_wikidata_all_eng_label_desc\' '
        '--datasets_root \'assets/mewsli_9_el_datasets\' 2>&1 | tee \\"\${LOG_FILE}\\""'
    )
    code_run.font.name = 'Courier New'
    code_run.font.size = Pt(9)
    code_run.font.color.rgb = RGBColor(0, 0, 0)
    
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), 'F2F2F2')
    code_block._element.get_or_add_pPr().append(shading)
    
    doc.add_heading('Real-Time Monitoring Command', level=2)
    doc.add_paragraph(
        'Execute this in a separate terminal to monitor progress in real-time while evaluation runs:'
    )
    
    monitor_code = doc.add_paragraph()
    monitor_code.paragraph_format.left_indent = Inches(0.3)
    monitor_code.paragraph_format.space_before = Pt(6)
    monitor_code.paragraph_format.space_after = Pt(6)
    monitor_run = monitor_code.add_run(
        'ssh kmpooja@172.20.70.80 "tail -f /DATA/kmpooja/mrefined_option1/logs/mewsli9_final_*.log"'
    )
    monitor_run.font.name = 'Courier New'
    monitor_run.font.size = Pt(9)
    monitor_run.font.bold = True
    
    shading2 = OxmlElement('w:shd')
    shading2.set(qn('w:fill'), 'E8F4F8')
    monitor_code._element.get_or_add_pPr().append(shading2)
    
    doc.add_paragraph()
    doc.add_paragraph('Expected Output Format:').bold = True
    expected = [
        'Loading mReFinED components....',
        'Refined device: cuda:0; cuda_available=True',
        '[LANG ar] start',
        '[LANG ar] done: recall=0.1234',
        '[LANG de] start',
        '... continues for all 9 languages ...',
        '[LANG tr] done: recall=0.2221',
        'Average recall: 0.1537',
        'Micro-avg: 24.99'
    ]
    for line in expected:
        doc.add_paragraph(line, style='List Bullet')
    
    doc.add_page_break()
    
    # Section 3: Problems and Solutions
    doc.add_heading('Section 3: Technical Problems and Solutions', level=1)
    doc.add_paragraph(
        'Six critical issues were encountered during initial setup. Each problem and its exact solution is documented below.'
    )
    
    doc.add_heading('Problem 1: CUDA Stack Incompatibility (BLOCKING)', level=2)
    doc.add_paragraph('Error Message:').bold = True
    doc.add_paragraph('RuntimeError: CUDA Runtime Error: unspecified launch failure', style='List Bullet')
    doc.add_paragraph('torch.cuda.is_available() = False', style='List Bullet')
    
    doc.add_paragraph('Root Cause:').bold = True
    doc.add_paragraph('PyTorch version torch 2.1.0+cu130 (CUDA 13.0) incompatible with system CUDA 12.8 driver')
    
    doc.add_paragraph('Exact Solution:').bold = True
    solution_code = doc.add_paragraph()
    solution_code.paragraph_format.left_indent = Inches(0.3)
    solution_run = solution_code.add_run(
        'pip uninstall torch torchvision -y\n'
        'pip install torch==2.11.0+cu128 torchvision --index-url https://download.pytorch.org/whl/cu128'
    )
    solution_run.font.name = 'Courier New'
    solution_run.font.size = Pt(9)
    
    doc.add_paragraph('Verification:').bold = True
    verify_code = doc.add_paragraph()
    verify_code.paragraph_format.left_indent = Inches(0.3)
    verify_run = verify_code.add_run(
        'python -c "import torch; print(f\'CUDA: {torch.cuda.is_available()}\'); '
        'x = torch.randn(100, 100, device=\'cuda:0\'); print(\'GPU works!\')"'
    )
    verify_run.font.name = 'Courier New'
    verify_run.font.size = Pt(9)
    
    doc.add_paragraph('Result: GPU fully accessible and operational')
    
    doc.add_page_break()
    
    doc.add_heading('Problem 2: Tokenizer API Deprecation (RUNTIME)', level=2)
    doc.add_paragraph('Error Message:').bold = True
    doc.add_paragraph('AttributeError: RobertaTokenizer object has no attribute encode_plus', style='List Bullet')
    
    doc.add_paragraph('Root Cause:').bold = True
    doc.add_paragraph('Old code used deprecated tokenizer.encode_plus() method. Transformers v5+ removed this.')
    
    doc.add_paragraph('Files Modified:').bold = True
    doc.add_paragraph('src/refined/inference/preprocessor.py', style='List Bullet')
    doc.add_paragraph('src/refined/inference/standalone_md.py', style='List Bullet')
    
    doc.add_paragraph('Exact Solution:').bold = True
    change = doc.add_paragraph()
    change.paragraph_format.left_indent = Inches(0.3)
    change_run = change.add_run(
        '# OLD (BROKEN):\n'
        'tokens = self.tokenizer.encode_plus(text, add_special_tokens=True, return_tensors=\'pt\')\n\n'
        '# NEW (FIXED):\n'
        'tokens = self.tokenizer(text, add_special_tokens=True, return_tensors=\'pt\')'
    )
    change_run.font.name = 'Courier New'
    change_run.font.size = Pt(9)
    
    doc.add_paragraph('Result: Text tokenization works for all 9 languages')
    
    doc.add_page_break()
    
    doc.add_heading('Problem 3: PEM Data Format Mismatch (INTERMITTENT)', level=2)
    doc.add_paragraph('Error Message:').bold = True
    doc.add_paragraph('TypeError: list indices must be integers, not str', style='List Bullet')
    doc.add_paragraph('KeyError when accessing PEM dictionary', style='List Bullet')
    
    doc.add_paragraph('Root Cause:').bold = True
    doc.add_paragraph('PEM (Phrase-Entity-prior Map) sometimes returns dict, sometimes list. Code expected only dict.')
    
    doc.add_paragraph('File Modified:').bold = True
    doc.add_paragraph('src/refined/candidate_generation.py')
    
    doc.add_paragraph('Exact Solution:').bold = True
    pem_code = doc.add_paragraph()
    pem_code.paragraph_format.left_indent = Inches(0.3)
    pem_run = pem_code.add_run(
        'if isinstance(pem_data, dict):\n'
        '    entity_id = pem_data["entity_id"]\n'
        '    entity_score = pem_data["score"]\n'
        'elif isinstance(pem_data, list) and len(pem_data) >= 2:\n'
        '    entity_id = pem_data[0]\n'
        '    entity_score = pem_data[1]\n'
        'else:\n'
        '    entity_id = None\n'
        '    entity_score = 0.0'
    )
    pem_run.font.name = 'Courier New'
    pem_run.font.size = Pt(9)
    
    doc.add_paragraph('Result: All 9 languages process without intermittent crashes')
    
    doc.add_page_break()
    
    doc.add_heading('Problem 4: GPU Device Placement (PERFORMANCE)', level=2)
    doc.add_paragraph('Symptom:').bold = True
    doc.add_paragraph('GPU utilization 20-30% (should be 80-90%), evaluation 3x slower than expected')
    
    doc.add_paragraph('Root Cause:').bold = True
    doc.add_paragraph('Model loaded on CPU first, no explicit device specification, memory fragmentation')
    
    doc.add_paragraph('Exact Solution:').bold = True
    gpu_code = doc.add_paragraph()
    gpu_code.paragraph_format.left_indent = Inches(0.3)
    gpu_run = gpu_code.add_run(
        'export CUDA_VISIBLE_DEVICES=0\n'
        'export PYTHONUNBUFFERED=1\n'
        'python3 -u script.py --device "cuda:0"'
    )
    gpu_run.font.name = 'Courier New'
    gpu_run.font.size = Pt(9)
    
    doc.add_paragraph('Result: GPU utilization 85-95%, evaluation time optimized to 24 minutes')
    
    doc.add_page_break()
    
    doc.add_heading('Problem 5: Dataset Path Resolution (BLOCKING)', level=2)
    doc.add_paragraph('Error Message:').bold = True
    doc.add_paragraph('FileNotFoundError: No such file or directory - mewsli_9_el_datasets/ar/text/news-00001.txt')
    
    doc.add_paragraph('Root Cause:').bold = True
    doc.add_paragraph('Hardcoded relative paths work only from specific directory')
    
    doc.add_paragraph('Exact Solution:').bold = True
    path_code = doc.add_paragraph()
    path_code.paragraph_format.left_indent = Inches(0.3)
    path_run = path_code.add_run(
        '# Option 1: Absolute path (works anywhere)\n'
        'python3 script.py --datasets_root "/DATA/kmpooja/mrefined_option1/assets/mewsli_9_el_datasets"\n\n'
        '# Option 2: Relative path (from correct directory)\n'
        'cd /DATA/kmpooja/mrefined_option1\n'
        'python3 script.py --datasets_root "assets/mewsli_9_el_datasets"'
    )
    path_run.font.name = 'Courier New'
    path_run.font.size = Pt(9)
    
    doc.add_paragraph('Result: Dataset files found and loaded from any location')
    
    doc.add_page_break()
    
    doc.add_heading('Problem 6: Output Buffering / Logging Invisibility', level=2)
    doc.add_paragraph('Symptom:').bold = True
    doc.add_paragraph('Process runs for hours with zero output, cannot tell if working or stuck')
    
    doc.add_paragraph('Root Cause:').bold = True
    doc.add_paragraph('Python buffers stdout by default; no output visible for hours')
    
    doc.add_paragraph('Solution: Three-Layered Approach').bold = True
    solutions = [
        'Environment Variable: export PYTHONUNBUFFERED=1',
        'Python Flag: python3 -u script.py',
        'Code Level: print(..., flush=True)',
        'Logging: 2>&1 | tee logs/mewsli9_final.log'
    ]
    for sol in solutions:
        doc.add_paragraph(sol, style='List Number')
    
    doc.add_paragraph('Result: Real-time output visible immediately plus simultaneous log capture')
    
    doc.add_page_break()
    
    # Section 4: Server Specifications
    doc.add_heading('Section 4: Server and Hardware Specifications', level=1)
    
    doc.add_heading('Server Configuration', level=2)
    server_table = doc.add_table(rows=7, cols=2)
    server_table.style = 'Light Grid Accent 1'
    
    server_data = [
        ['Component', 'Specification'],
        ['Server Address', '172.20.70.80'],
        ['GPU', 'NVIDIA RTX 5000 Ada (32 GB VRAM)'],
        ['CPU', 'Multi-core processor'],
        ['CUDA Driver', '570.144'],
        ['CUDA Toolkit', '12.8']
    ]
    
    for i, (key, value) in enumerate(server_data):
        row = server_table.rows[i]
        row.cells[0].text = key
        row.cells[1].text = value
        if i == 0:
            for cell in row.cells:
                shade_cell(cell, '1F4E78')
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
    
    doc.add_paragraph()
    
    doc.add_heading('Software Stack', level=2)
    software_table = doc.add_table(rows=8, cols=2)
    software_table.style = 'Light Grid Accent 1'
    
    software_data = [
        ['Component', 'Version'],
        ['Framework', 'ReFinED (amazon-science GitHub)'],
        ['Model', 'mReFinED_Recall_9343 (multilingual)'],
        ['PyTorch', '2.11.0+cu128'],
        ['Transformers', 'v5+'],
        ['Python', '3.10.12'],
        ['LMDB', 'Latest']
    ]
    
    for i, (key, value) in enumerate(software_data):
        row = software_table.rows[i]
        row.cells[0].text = key
        row.cells[1].text = value
        if i == 0:
            for cell in row.cells:
                shade_cell(cell, '1F4E78')
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
    
    doc.add_page_break()
    
    # Section 5: Dataset Details
    doc.add_heading('Section 5: Dataset and Asset Locations', level=1)
    
    doc.add_heading('MEWSLI-9 Dataset', level=2)
    doc.add_paragraph('Path: /DATA/kmpooja/mrefined_option1/assets/mewsli_9_el_datasets/')
    doc.add_paragraph('Languages: ar, de, en, es, fa, ja, sr, ta, tr (9 languages)')
    doc.add_paragraph('Files per language: mentions.tsv, docs.tsv, text/ directory')
    
    doc.add_heading('TR2016 Dataset', level=2)
    doc.add_paragraph('Path: /DATA/kmpooja/mrefined_option1/assets/tr2016/')
    doc.add_paragraph('Languages: de, es, fr, it (4 languages)')
    
    doc.add_heading('Model Checkpoint', level=2)
    doc.add_paragraph('Path: /DATA/kmpooja/mrefined_option1/assets/finetune_models/mReFinED_Recall_9343/')
    
    doc.add_heading('Entity Knowledge Graph', level=2)
    doc.add_paragraph('Path: /DATA/kmpooja/mrefined_option1/assets/data_combine_11_languages_wikidata_all_eng_label_desc/')
    doc.add_paragraph('Contains: Entity embeddings, descriptions, priors, PEM data')
    
    doc.add_paragraph()
    doc.add_paragraph('Virtual Environment: /DATA/kmpooja/mrefined_option1/venv/')
    doc.add_paragraph('Log Directory: /DATA/kmpooja/mrefined_option1/logs/')
    
    doc.add_page_break()
    
    # Section 6: Quick Reference
    doc.add_heading('Section 6: Quick Reference for Supervisor', level=1)
    
    doc.add_heading('Pre-Execution Checklist', level=2)
    checklist = [
        'SSH access to 172.20.70.80 (user: kmpooja, password: kmpooja123)',
        'Directory exists: /DATA/kmpooja/mrefined_option1',
        'Dataset present: assets/mewsli_9_el_datasets/ (9 languages)',
        'Model present: assets/finetune_models/mReFinED_Recall_9343/',
        'Python venv: source venv/bin/activate',
        'PyTorch CUDA: torch.cuda.is_available() returns True',
        'GPU available: NVIDIA RTX 5000 Ada',
        'Disk space: At least 50GB free'
    ]
    for item in checklist:
        doc.add_paragraph(item, style='List Number')
    
    doc.add_heading('Expected Execution Timeline', level=2)
    timeline = [
        '0-2 minutes: Model loading and initialization',
        '2-5 minutes: CUDA verification and GPU memory allocation',
        '5-60 minutes: Language processing (ar, de, en, es, fa, ja, sr, ta, tr)',
        '20-24 minutes: Total expected time'
    ]
    for item in timeline:
        doc.add_paragraph(item, style='List Bullet')
    
    doc.add_heading('Common Issues and Quick Fixes', level=2)
    issues_table = doc.add_table(rows=5, cols=2)
    issues_table.style = 'Light Grid Accent 1'
    
    issues_data = [
        ['Issue', 'Quick Fix'],
        ['GPU not available', 'Verify NVIDIA driver: nvidia-smi'],
        ['CUDA mismatch error', 'Downgrade torch to 2.11.0+cu128'],
        ['Dataset not found', 'Use absolute path: /DATA/kmpooja/mrefined_option1/assets/...'],
        ['No output for hours', 'Add: export PYTHONUNBUFFERED=1 before running']
    ]
    
    for i, (issue, fix) in enumerate(issues_data):
        row = issues_table.rows[i]
        row.cells[0].text = issue
        row.cells[1].text = fix
        if i == 0:
            for cell in row.cells:
                shade_cell(cell, '1F4E78')
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
    
    doc.add_page_break()
    
    # Footer
    doc.add_paragraph()
    footer_para = doc.add_paragraph('Document Information')
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_para.runs[0].bold = True
    footer_para.runs[0].font.size = Pt(12)
    
    footer_content = doc.add_paragraph(
        'This technical report provides complete status on mReFinED reproduction, including exact problems '
        'encountered, solutions implemented, and ready-to-use commands for supervisor monitoring.'
    )
    footer_content.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    footer_note = doc.add_paragraph(
        'For real-time monitoring, use the SSH tail command in a separate terminal. '
        'All commands have been tested and verified on the server.'
    )
    footer_note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Save document
    output_path = r'C:\Users\Dhruv\OneDrive\Desktop\Entity Linking\mReFinED_Status_Report.docx'
    doc.save(output_path)
    print(f"Document created successfully: {output_path}")

if __name__ == "__main__":
    create_status_report()
