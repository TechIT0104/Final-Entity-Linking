import re
import requests

pdf_url='https://aclanthology.org/N16-1072.pdf'
r=requests.get(pdf_url,timeout=30,headers={'User-Agent':'Mozilla/5.0'})
print('download',r.status_code,'bytes',len(r.content))
open('__N16_1072.pdf','wb').write(r.content)

import pypdf
reader=pypdf.PdfReader('__N16_1072.pdf')
text='\n'.join((p.extract_text() or '') for p in reader.pages)
open('__N16_1072.txt','w',encoding='utf-8').write(text)
print('text chars',len(text))

# Print lines around likely clues
lines=text.splitlines()
keys=['dataset','data set','TR2016','wikification','eval','TAC','KBP','LDC','available','download','http','www.','cross-lingual','benchmark','hard','source code']
for i,line in enumerate(lines,1):
    low=line.lower()
    if any(k.lower() in low for k in keys):
        if len(line.strip())>0:
            print(f'{i}: {line}')

# Try URL extraction from text body
urls=sorted(set(re.findall(r'https?://[^\s)\]}>"\']+', text)))
print('\nurls',len(urls))
for u in urls:
    print(u)
