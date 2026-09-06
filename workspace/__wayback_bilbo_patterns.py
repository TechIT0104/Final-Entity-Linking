import requests
patterns=[
    'bilbo.cs.illinois.edu/backend.php*',
    'bilbo.cs.illinois.edu/*backend.php*',
    'bilbo.cs.illinois.edu/*.php*',
    'bilbo.cs.illinois.edu/page/data*',
    'bilbo.cs.illinois.edu/page/resource*',
    'bilbo.cs.illinois.edu/page/publication_view/*',
    'bilbo.cs.illinois.edu/page/software_view/*',
    'bilbo.cs.illinois.edu/page/demo_view/*',
    'bilbo.cs.illinois.edu/page/*controller*.js*',
    'bilbo.cs.illinois.edu/*/backend.php*',
]
for p in patterns:
    params={
        'url':p,
        'output':'json',
        'fl':'timestamp,original,mimetype,statuscode,length',
        'from':'2014','to':'2021','limit':'10000'
    }
    r=requests.get('https://web.archive.org/cdx/search/cdx',params=params,timeout=60,headers={'User-Agent':'Mozilla/5.0'})
    print('\nPATTERN',p,'status',r.status_code,'len',len(r.text))
    if r.status_code!=200:
        continue
    try:
        data=r.json()
    except Exception:
        print(r.text[:300])
        continue
    print(' rows',len(data)-1)
    for row in data[1:][:80]:
        print(' ',row)
