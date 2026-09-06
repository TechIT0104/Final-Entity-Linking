import requests,re
from urllib.parse import urljoin

url='https://cogcomp.seas.upenn.edu/page/publications/'
r=requests.get(url,timeout=30,headers={'User-Agent':'Mozilla/5.0'})
print('status',r.status_code,'len',len(r.text),'url',r.url)
open('__cogcomp_publications.html','w',encoding='utf-8',errors='ignore').write(r.text)

scripts=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', r.text, flags=re.I)
print('scripts',len(scripts))
for s in scripts:
    full=urljoin(r.url,s)
    print(' ',s,'=>',full)
    if 'ajax.googleapis.com' in full:
        continue
    rr=requests.get(full,timeout=30,headers={'User-Agent':'Mozilla/5.0'})
    print('  fetch',rr.status_code,'len',len(rr.text))
    if rr.status_code==200:
        out='__cogcomp_'+re.sub(r'[^a-zA-Z0-9]+','_',full)
        with open(out,'w',encoding='utf-8',errors='ignore') as f:
            f.write(rr.text)
