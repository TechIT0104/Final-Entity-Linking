import requests, urllib.parse

queries=[
    'tr2016/de/test',
    'placeholder.mentions.new',
    'multilingual_e2e_evaluation_tr2016.py',
    'lang_title2wikidataID-normalized_with_redirect.pkl',
    'is_hard q_id non_en_title',
    '.mentions.new tr2016',
]

for q in queries:
    try:
        url='https://grep.app/api/search'
        params={'q':q,'regexp':'false','case':'false'}
        r=requests.get(url,params=params,timeout=40,headers={'User-Agent':'Mozilla/5.0'})
        print('\nQUERY',q,'status',r.status_code)
        if r.status_code!=200:
            print(r.text[:200]);
            continue
        js=r.json()
        hits=js.get('hits',{}).get('hits',[])
        print('hits',len(hits))
        for h in hits[:20]:
            repo=h.get('repo',{}).get('raw','')
            path=h.get('path',{}).get('raw','')
            print('  ',repo,'::',path)
    except Exception as e:
        print('ERR',q,e)
