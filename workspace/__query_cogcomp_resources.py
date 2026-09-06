import requests, json

base='https://cogcomp.seas.upenn.edu'
ids=[102,105,93]
for rid in ids:
    u=f'{base}/page/resource_view/view-backend.php?id={rid}'
    r=requests.get(u,timeout=60,headers={'User-Agent':'Mozilla/5.0'})
    print('\nresource',rid,'status',r.status_code,'len',len(r.text))
    out=f'__cogcomp_resource_{rid}.json'
    open(out,'w',encoding='utf-8',errors='ignore').write(r.text)
    if r.status_code!=200:
        continue
    try:
        j=r.json()
    except Exception as ex:
        print(' json err',ex)
        print(r.text[:400])
        continue
    b=j.get('basic',{})
    print(' title',b.get('title'))
    print(' timestamp',b.get('timestamp'))
    print(' description',str(b.get('description'))[:500])
    if j.get('downloads'):
        print(' downloads',j['downloads'])
    if j.get('publications'):
        print(' publications',j['publications'])
    if j.get('software'):
        print(' software',j['software'])
    if j.get('demo'):
        print(' demo',j['demo'])
    if j.get('people'):
        print(' people',j['people'])
