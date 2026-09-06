import requests, json, re

print('=== Hugging Face datasets search ===')
for q in ['tr2016','tac-kbp','entity linking multilingual','mgenre tr2016','kbp 2016']:
    try:
        u=f'https://huggingface.co/api/datasets?search={requests.utils.quote(q)}&limit=50'
        r=requests.get(u,timeout=30)
        print('\nQUERY',q,'STATUS',r.status_code)
        if r.status_code!=200:
            continue
        data=r.json()
        names=[d.get('id','') for d in data if isinstance(d,dict)]
        hits=[n for n in names if any(k in n.lower() for k in ['tr2016','kbp','tac','mgenre','mewsli'])]
        for h in hits[:20]:
            print('  ',h)
    except Exception as e:
        print('ERR',q,e)

print('\n=== Wayback TAC-KBP 2016 page ===')
cdx='https://web.archive.org/cdx/search/cdx?url=tac.nist.gov/2016/KBP/EntityLinking/&output=json'
r=requests.get(cdx,timeout=30)
print('CDX_STATUS',r.status_code)
print(r.text[:1000])

print('\n=== Wayback snapshot content (if any) ===')
if r.status_code==200 and r.text.strip().startswith('['):
    try:
        arr=r.json()
        if len(arr)>1:
            # pick latest snapshot
            ts=arr[-1][1]
            wb=f'https://web.archive.org/web/{ts}/https://tac.nist.gov/2016/KBP/EntityLinking/'
            rr=requests.get(wb,timeout=30)
            print('SNAP_STATUS',rr.status_code,'LEN',len(rr.text))
            # print candidate links
            links=re.findall(r'href=[\"\']([^\"\']+)[\"\']',rr.text,flags=re.I)
            cand=[x for x in links if any(k in x.lower() for k in ['download','ldc','kbp','entity','tr2016','data'])]
            for x in cand[:80]:
                print('  ',x)
        else:
            print('No snapshots')
    except Exception as e:
        print('WAYBACK_PARSE_ERR',e)

print('\n=== GitHub code search via public API (path patterns) ===')
queries=[
    '"tr2016/de/test"',
    '"placeholder.mentions.new"',
    '"lang_title2wikidataID-normalized_with_redirect"',
    '".mentions.new" "tr2016"',
]
for q in queries:
    try:
        url='https://api.github.com/search/code'
        params={'q':q+' in:file', 'per_page':10}
        rr=requests.get(url,params=params,timeout=30)
        print('\nQ',q,'STATUS',rr.status_code)
        if rr.status_code!=200:
            print(rr.text[:200])
            continue
        js=rr.json()
        print('total_count',js.get('total_count'))
        for it in js.get('items',[])[:10]:
            print('  ',it.get('repository',{}).get('full_name'),'::',it.get('path'))
    except Exception as e:
        print('ERR',q,e)
