import requests, re

def hf_search(q):
    u=f'https://huggingface.co/api/datasets?search={requests.utils.quote(q)}&limit=100'
    r=requests.get(u,timeout=40)
    print('HF',q,'status',r.status_code)
    if r.status_code!=200:
        print(r.text[:200]); return
    data=r.json()
    ids=[d.get('id','') for d in data if isinstance(d,dict)]
    print('  total',len(ids))
    keep=[i for i in ids if any(k in i.lower() for k in ['tr2016','tac','kbp','entity-link','entity_link','mewsli','mgenre','genre'])]
    for i in keep[:50]:
        print('   ',i)

print('=== HF ===')
for q in ['tr2016','tac-kbp','kbp','entity linking multilingual','mgenre']:
    try:
        hf_search(q)
    except Exception as e:
        print('HF_ERR',q,e)

print('\n=== GitHub code search API ===')
for q in ['"tr2016/de/test" in:path', '".mentions.new" tr2016 in:file', '"multilingual_e2e_evaluation_tr2016.py" in:file']:
    try:
        rr=requests.get('https://api.github.com/search/code',params={'q':q,'per_page':10},timeout=40,headers={'Accept':'application/vnd.github+json'})
        print('GH',q,'status',rr.status_code)
        if rr.status_code!=200:
            print('  body',rr.text[:250])
            continue
        js=rr.json(); print('  total',js.get('total_count'))
        for it in js.get('items',[])[:10]:
            print('   ',it.get('repository',{}).get('full_name'),'::',it.get('path'))
    except Exception as e:
        print('GH_ERR',q,e)

print('\n=== DuckDuckGo HTML search ===')
queries=['TR2016 multilingual entity linking dataset download','TAC KBP 2016 entity linking data','mGENRE preprocess_TR2016 dataset']
for q in queries:
    try:
        url='https://duckduckgo.com/html/'
        r=requests.get(url,params={'q':q},timeout=40,headers={'User-Agent':'Mozilla/5.0'})
        print('DDG',q,'status',r.status_code,'len',len(r.text))
        links=re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"',r.text)
        for l in links[:12]:
            print('   ',l)
    except Exception as e:
        print('DDG_ERR',q,e)

print('\n=== Wayback quick ping ===')
for u in ['https://web.archive.org/cdx/search/cdx?url=tac.nist.gov/2016/KBP/EntityLinking/&output=json&limit=5',
          'https://web.archive.org/web/20200101000000*/https://tac.nist.gov/2016/KBP/EntityLinking/']:
    try:
        r=requests.get(u,timeout=25,headers={'User-Agent':'Mozilla/5.0'})
        print('WB',u,'status',r.status_code,'len',len(r.text))
        print(r.text[:300])
    except Exception as e:
        print('WB_ERR',u,e)
