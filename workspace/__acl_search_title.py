import re
import requests
from urllib.parse import quote_plus

q='Cross-lingual wikification using multilingual embeddings'
url='https://aclanthology.org/search/?q='+quote_plus(q)
r=requests.get(url,timeout=30,headers={'User-Agent':'Mozilla/5.0'})
print('status',r.status_code,'len',len(r.text))
open('__acl_search.html','w',encoding='utf-8').write(r.text)

if r.status_code==200:
    # collect anthology IDs and titles
    # entries often have href="/N16-XXXX/"
    ids=sorted(set(re.findall(r'href="/([A-Z0-9.-]+)/"', r.text)))
    print('ids sample',ids[:40])
    for m in re.finditer(r'<strong><a href="/([A-Z0-9.-]+)/">(.*?)</a></strong>', r.text):
        pid,title=m.group(1),re.sub('<.*?>','',m.group(2))
        print(pid,'::',title)

    # broad fallback: print lines containing Tsai or Roth
    txt=re.sub('<[^>]+>',' ',r.text)
    for pat in ['Tsai','Roth','wikification','multilingual embeddings','Cross-lingual']:
        if pat.lower() in txt.lower():
            print('contains',pat)
