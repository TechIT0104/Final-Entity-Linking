import re
import requests

base='http://bilbo.cs.illinois.edu/'
try:
    r=requests.get(base,timeout=30,headers={'User-Agent':'Mozilla/5.0'},allow_redirects=True)
    print('base status',r.status_code,'url',r.url,'len',len(r.text))
    open('__bilbo_home.html','w',encoding='utf-8',errors='ignore').write(r.text)
    links=sorted(set(re.findall(r'href=["\']([^"\']+)["\']', r.text, flags=re.I)))
    print('home links',len(links))
    for l in links[:200]:
        if any(k in l.lower() for k in ['wiki','wikification','cross','dataset','data','download','tac','kbp','entity','tr2016','tsai','roth']):
            print(' ',l)
except Exception as ex:
    print('base err',ex)

# Probe likely paths
cands=[
    'wikification',
    'crosslingual_wikification',
    'cross-lingual-wikification',
    'wikification/data',
    'wikification/dataset',
    'wikiME',
    'wikime',
    'wiki_me',
    'wikiME/data',
    'data',
    'datasets',
    'downloads',
    'publications',
    'papers',
    'resources',
    '~ctsai',
    '~danr',
    'people',
]
for c in cands:
    u=base+c
    try:
        rr=requests.get(u,timeout=20,headers={'User-Agent':'Mozilla/5.0'},allow_redirects=True)
        print('PATH',u,'=>',rr.status_code,'url',rr.url,'len',len(rr.text))
        if rr.status_code==200 and len(rr.text)>0:
            fn='__bilbo_'+re.sub(r'[^a-zA-Z0-9]+','_',c)+'.html'
            open(fn,'w',encoding='utf-8',errors='ignore').write(rr.text)
            ls=sorted(set(re.findall(r'href=["\']([^"\']+)["\']', rr.text, flags=re.I)))
            for l in ls[:300]:
                if any(k in l.lower() for k in ['zip','tar','gz','wiki','wikification','dataset','data','download','tac','kbp','entity','tr2016','tsai','roth']):
                    print('   link',l)
    except Exception as ex:
        print('PATH',u,'ERR',ex)
