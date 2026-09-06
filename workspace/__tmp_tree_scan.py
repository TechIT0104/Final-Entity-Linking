import requests,re
owner='amazon-science';repo='ReFinED';branch='mrefined'
url=f'https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1'
r=requests.get(url,timeout=60)
print('status',r.status_code)
if r.status_code!=200:
    print(r.text[:500]);raise SystemExit
items=r.json().get('tree',[])
print('count',len(items))
paths=[i['path'] for i in items if i.get('type')=='blob']
for p in paths:
    lp=p.lower()
    if any(k in lp for k in ['readme','dataset','data','tr2016','mewsli','benchmark','download','script','eval','preprocess']):
        if lp.endswith(('.md','.txt','.sh','.py','.json','.yaml','.yml','.cfg','.ini')):
            print(p)
