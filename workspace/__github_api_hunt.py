import requests

HEAD={'User-Agent':'Mozilla/5.0'}
queries=[
    'xlwikifier_data',
    'TR2016hard entity linking',
    'cross-lingual wikification multilingual embeddings dataset',
    'TAC-KBP 2016 trilingual entity linking',
]
for q in queries:
    u='https://api.github.com/search/repositories'
    r=requests.get(u,params={'q':q,'per_page':10},headers=HEAD,timeout=30)
    print('\n[REPO SEARCH]',q,'status',r.status_code)
    if r.status_code!=200:
        print(r.text[:300])
        continue
    data=r.json()
    print(' total_count',data.get('total_count'))
    for it in data.get('items',[])[:10]:
        print(' ',it.get('full_name'),'-',it.get('html_url'))

# try code search for string TR2016hard or .mentions.new in public repos
code_queries=['TR2016hard','preprocess_TR2016.py','".mentions.new" tr2016']
for cq in code_queries:
    r=requests.get('https://api.github.com/search/code',params={'q':cq,'per_page':10},headers=HEAD,timeout=30)
    print('\n[CODE SEARCH]',cq,'status',r.status_code)
    if r.status_code!=200:
        print(r.text[:500])
        continue
    j=r.json()
    print(' total_count',j.get('total_count'))
    for it in j.get('items',[])[:10]:
        print(' ',it.get('html_url'))
