import re
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

MD_PATH = "FINAL_RESULTS_TABLES.md"
OUT_DOCX = "FINAL_RESULTS_TABLES.docx"

def parse_tables(lines):
    tables = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip().startswith('|'):
            start = i
            while i < n and lines[i].strip().startswith('|'):
                i += 1
            end = i
            tables.append((start, end))
        else:
            i += 1
    return tables

def split_row(row):
    parts = [c.strip() for c in row.strip().strip('|').split('|')]
    return parts

def main():
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)

    tables_idx = parse_tables(lines)
    table_starts = {s: (s,e) for s,e in tables_idx}

    i = 0
    n = len(lines)
    while i < n:
        if i in table_starts:
            s,e = table_starts[i]
            block = lines[s:e]
            # header is first row, separator second
            if len(block) >= 2 and re.match(r'^\|?\s*-', block[1]):
                header = split_row(block[0])
                rows = [split_row(r) for r in block[2:]]
            else:
                header = split_row(block[0])
                rows = [split_row(r) for r in block[1:]]

            # create table
            ncols = len(header)
            nrows = 1 + len(rows)
            table = doc.add_table(rows=nrows, cols=ncols)
            table.style = 'Light Grid Accent 1'
            
            # fill header
            hdr_cells = table.rows[0].cells
            for c, val in enumerate(header):
                if c < len(hdr_cells):
                    hdr_cells[c].text = val
                    # bold header
                    for paragraph in hdr_cells[c].paragraphs:
                        for run in paragraph.runs:
                            run.bold = True
            
            # fill rows
            for r_idx, row in enumerate(rows, start=1):
                cells = table.rows[r_idx].cells
                for c, val in enumerate(row):
                    if c < len(cells):
                        cells[c].text = val
                        # highlight AVERAGE row
                        if '**AVERAGE**' in val or '**' in val:
                            for paragraph in cells[c].paragraphs:
                                for run in paragraph.runs:
                                    run.bold = True
                                    run.font.color.rgb = RGBColor(0, 102, 0)  # dark green
            
            doc.add_paragraph('')
            i = e
            continue
        
        # non-table line
        line = lines[i].rstrip('\n')
        if line.startswith('# '):
            heading = doc.add_heading(line[2:].strip(), level=1)
            heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        elif line.startswith('## '):
            doc.add_heading(line[3:].strip(), level=2)
        elif line.startswith('### '):
            doc.add_heading(line[4:].strip(), level=3)
        elif line.strip() == '':
            doc.add_paragraph('')
        elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. ') or line.startswith('4. '):
            # bullet list
            doc.add_paragraph(line[3:].strip(), style='List Bullet')
        else:
            # normal paragraph
            if '**' in line:
                # parse bold
                p = doc.add_paragraph()
                parts = re.split(r'(\*\*.*?\*\*)', line)
                for part in parts:
                    if part.startswith('**') and part.endswith('**'):
                        run = p.add_run(part[2:-2])
                        run.bold = True
                    else:
                        p.add_run(part)
            else:
                doc.add_paragraph(line)
        i += 1

    doc.save(OUT_DOCX)
    print(f"✅ Wrote {OUT_DOCX}")

if __name__ == '__main__':
    main()
