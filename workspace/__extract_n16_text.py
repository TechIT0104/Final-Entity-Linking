import requests

url = 'https://aclanthology.org/N16-1075.pdf'
pdf_path = '__N16_1075.pdf'
r = requests.get(url, timeout=30)
print('download', r.status_code, len(r.content))
open(pdf_path, 'wb').write(r.content)

import pypdf
reader = pypdf.PdfReader(pdf_path)
text = '\n'.join((p.extract_text() or '') for p in reader.pages)
open('__N16_1075.txt', 'w', encoding='utf-8').write(text)
print('chars', len(text))

keys = ['http', 'www.', 'dataset', 'data', 'available', 'release', 'benchmark', 'TR2016', 'Tsai', 'Roth', 'TAC', 'LDC']
lines = text.splitlines()
for i, line in enumerate(lines, 1):
    low = line.lower()
    if any(k.lower() in low for k in keys):
        if len(line.strip()) > 0:
            print(f'{i}: {line}')
