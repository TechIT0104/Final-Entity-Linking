import requests
import json

HEAD={'User-Agent':'Mozilla/5.0'}
base='https://cogcomp.seas.upenn.edu'

# Load publication index JSON
u=f'{base}/page/publications/backend.php'
r=requests.get(u,timeout=60,headers=HEAD)
print('pub backend',r.status_code,'len',len(r.text))
open('__cogcomp_publications_backend.json','w',encoding='utf-8',errors='ignore').write(r.text)

if r.status_code!=200:
    raise SystemExit

data=r.json()
print('keys',list(data.keys()))
pubs=data.get('publications',[])
print('publications',len(pubs))

hits=[]
for p in pubs:
    txt=' '.join(str(p.get(k,'')) for k in ['title','author','journal','booktitle','year'])
    low=txt.lower()
    if ('cross-lingual wikification' in low and 'multilingual embeddings' in low) or ('chen-tse tsai' in low and 'dan roth' in low) or ('tsai' in low and 'roth' in low and 'wikification' in low):
        hits.append(p)

print('\nHITS',len(hits))
for h in hits:
    print(' id',h.get('id'),'year',h.get('year'))
    print(' title',h.get('title'))
    print(' author',h.get('author'))
    print(' url',h.get('url'))
    print(' proj_url',h.get('proj_url'))
    print(' github_url',h.get('github_url'))

# Also broad search for TR2016 mention on publication titles/abstract snippets if present
tr_hits=[]
for p in pubs:
    s=' '.join(str(v) for v in p.values()).lower()
    if 'tr2016' in s or 'wiki me' in s or 'wikime' in s or 'tac kbp2015' in s:
        tr_hits.append(p)
print('\nTR_RELATED_HITS',len(tr_hits))
for t in tr_hits[:30]:
    print(' id',t.get('id'),'year',t.get('year'),'title',t.get('title'))

# Query detailed publication backend for matched ids
for h in hits:
    pid=h.get('id')
    vu=f'{base}/page/publication_view/view-backend.php?id={pid}'
    vr=requests.get(vu,timeout=60,headers=HEAD)
    print('\nview backend',pid,'status',vr.status_code,'len',len(vr.text))
    out=f'__cogcomp_publication_view_{pid}.json'
    open(out,'w',encoding='utf-8',errors='ignore').write(vr.text)
    if vr.status_code!=200:
        continue
    j=vr.json()
    b=j.get('basic',{})
    print(' basic.title',b.get('title'))
    print(' basic.url',b.get('url'))
    print(' basic.proj_url',b.get('proj_url'))
    print(' basic.github_url',b.get('github_url'))

    for k in ['supp','poster','presentation','data','software','demo','model','projects','people']:
        arr=j.get(k)
        if arr:
            print(' ',k,':',arr)
