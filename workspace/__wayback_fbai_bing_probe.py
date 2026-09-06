import requests,re

print('=== Wayback wildcard TAC-KBP 2016 ===')
for q in [
  'https://web.archive.org/cdx/search/cdx?url=tac.nist.gov/2016/KBP/*&output=json&fl=timestamp,original,statuscode,mimetype&filter=statuscode:200&limit=2000',
  'https://web.archive.org/cdx/search/cdx?url=tac.nist.gov/2016/*Entity*&output=json&fl=timestamp,original,statuscode,mimetype&filter=statuscode:200&limit=2000',
  'https://web.archive.org/cdx/search/cdx?url=tac.nist.gov/*KBP*2016*&output=json&fl=timestamp,original,statuscode,mimetype&filter=statuscode:200&limit=2000'
]:
    try:
        r=requests.get(q,timeout=60,headers={'User-Agent':'Mozilla/5.0'})
        print('\nURL',q,'status',r.status_code,'len',len(r.text))
        if r.status_code!=200:
            continue
        txt=r.text
        if txt.strip().startswith('['):
            arr=r.json()
            print('rows',len(arr)-1 if len(arr)>0 else 0)
            rows=arr[1:]
            filt=[]
            for row in rows:
                if len(row)<2: continue
                orig=row[1]
                if any(k in orig.lower() for k in ['entity', 'link', 'kbp', 'eval', 'data', 'download', 'coldstart']):
                    filt.append(row)
            print('filtered',len(filt))
            for row in filt[:120]:
                print('  ',row[0],row[1])
        else:
            print(txt[:300])
    except Exception as e:
        print('ERR',e)

print('\n=== fbaipublicfiles index probes ===')
urls=[
 'http://dl.fbaipublicfiles.com/',
 'http://dl.fbaipublicfiles.com/GENRE/',
 'http://dl.fbaipublicfiles.com/mGENRE/',
 'http://dl.fbaipublicfiles.com/KILT/',
 'http://dl.fbaipublicfiles.com/BLINK/',
 'https://dl.fbaipublicfiles.com/GENRE/',
 'https://dl.fbaipublicfiles.com/mGENRE/',
]
for u in urls:
    try:
        r=requests.get(u,timeout=30,headers={'User-Agent':'Mozilla/5.0'})
        print('\n',u,'status',r.status_code,'len',len(r.text))
        print(r.text[:220].replace('\n',' '))
        links=re.findall(r'href=[\"\']([^\"\']+)[\"\']',r.text,flags=re.I)
        cand=[x for x in links if any(k in x.lower() for k in ['tr2016','genre','kilt','blink','kbp','tar','zip','json'])]
        for x in cand[:60]:
            print('  ',x)
    except Exception as e:
        print(u,'ERR',e)

print('\n=== Bing RSS search ===')
queries=['TR2016 entity linking dataset', 'TAC KBP 2016 Entity Linking data', 'preprocess_TR2016.py dataset']
for q in queries:
    try:
        u='https://www.bing.com/search'
        r=requests.get(u,params={'q':q,'format':'rss'},timeout=30,headers={'User-Agent':'Mozilla/5.0'})
        print('\nQ',q,'status',r.status_code,'len',len(r.text))
        items=re.findall(r'<item>(.*?)</item>',r.text,flags=re.S)
        for it in items[:8]:
            title=re.search(r'<title>(.*?)</title>',it,re.S)
            link=re.search(r'<link>(.*?)</link>',it,re.S)
            if title and link:
                print('  ',re.sub(r'\s+',' ',title.group(1)).strip())
                print('   ',link.group(1).strip())
    except Exception as e:
        print('ERR',q,e)
