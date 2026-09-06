import requests, json
queries=['TR2016', 'preprocess_TR2016.py', 'dl.fbaipublicfiles.com/GENRE/', 'mewsli', 'scripts_mgenre/README.md']
for q in queries:
    r=requests.get('https://grep.app/api/search',params={'q':q,'regexp':'false','case':'false'},timeout=40,headers={'User-Agent':'Mozilla/5.0'})
    print('\nQUERY',q,'status',r.status_code)
    if r.status_code!=200:
        print(r.text[:200]); continue
    js=r.json(); print('total',js.get('hits',{}).get('total'))
    hits=js.get('hits',{}).get('hits',[])
    for h in hits[:20]:
        repo=h.get('repo'); path=h.get('path');
        print(' ',repo,'::',path)
        sn=h.get('content',{}).get('snippet','')
        sn=sn.replace('\n',' ')
        print('   SNIP',sn[:240])
