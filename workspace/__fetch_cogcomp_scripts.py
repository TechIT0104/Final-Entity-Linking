import requests
import re
from urllib.parse import urljoin

base='https://cogcomp.seas.upenn.edu/page/publication_view/810'
r=requests.get(base,timeout=30,headers={'User-Agent':'Mozilla/5.0'})
print('pub status',r.status_code,'len',len(r.text), 'url', r.url)
open('__cogcomp_pub_810.html','w',encoding='utf-8',errors='ignore').write(r.text)

scripts=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', r.text, flags=re.I)
print('scripts',len(scripts))
for s in scripts:
    full=urljoin(r.url,s)
    print(' ',s,'=>',full)

for s in scripts:
    full=urljoin(r.url,s)
    if 'ajax.googleapis.com' in full:
        continue
    try:
        rr=requests.get(full,timeout=30,headers={'User-Agent':'Mozilla/5.0'})
        print(' fetch',full,'status',rr.status_code,'len',len(rr.text))
        if rr.status_code==200:
            name='__cogcomp_'+re.sub(r'[^a-zA-Z0-9]+','_',full)
            if name.endswith('_'):
                name += 'txt'
            open(name,'w',encoding='utf-8',errors='ignore').write(rr.text)
    except Exception as ex:
        print(' ERR',full,ex)
