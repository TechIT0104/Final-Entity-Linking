import requests
import json

# Query Wayback CDX for bilbo host URLs
queries=[
    'bilbo.cs.illinois.edu/*',
    'bilbo.cs.illinois.edu*wik*',
    'bilbo.cs.illinois.edu*data*',
    'bilbo.cs.illinois.edu*tr*',
    'bilbo.cs.illinois.edu*zip*',
    'bilbo.cs.illinois.edu*tar*',
]

for q in queries:
    print('\n[CDX]',q)
    params={
        'url': q,
        'output': 'json',
        'fl': 'timestamp,original,mimetype,statuscode,digest,length',
        'filter': 'statuscode:200',
        'limit': '20000',
        'from': '2014',
        'to': '2020',
        'collapse': 'urlkey',
    }
    try:
        r=requests.get('https://web.archive.org/cdx/search/cdx',params=params,timeout=60,headers={'User-Agent':'Mozilla/5.0'})
        print(' status',r.status_code,'len',len(r.text))
        if r.status_code!=200:
            print(r.text[:300])
            continue
        data=r.json()
        print(' rows',len(data)-1 if data else 0)
        rows=data[1:] if data else []
        # prioritize likely downloadable/data pages
        picked=[]
        for row in rows:
            ts,orig,mime,sc,dig,length=row
            low=orig.lower()
            if any(k in low for k in ['wiki','wikification','cross','dataset','data','download','tr2016','tsai','roth','tac','kbp','.zip','.tar','.gz','.tgz','.rar']):
                picked.append((ts,orig,mime,length))
        # de-dup by orig
        seen=set()
        out=[]
        for t,o,m,l in picked:
            if o in seen:
                continue
            seen.add(o)
            out.append((t,o,m,l))
        for t,o,m,l in out[:120]:
            print(' ',t,o,m,l)
    except Exception as ex:
        print(' ERR',ex)
