import requests

q='Cross-lingual wikification using multilingual embeddings'
u='https://api.openalex.org/works'
r=requests.get(u,params={'search':q,'per-page':10},timeout=30,headers={'User-Agent':'Mozilla/5.0'})
print('status',r.status_code)
if r.status_code==200:
    j=r.json()
    print('count',j.get('meta',{}).get('count'))
    for w in j.get('results',[]):
        title=w.get('title')
        year=w.get('publication_year')
        doi=w.get('doi')
        ids=w.get('ids',{})
        host=w.get('primary_location',{})
        src=(host.get('source') or {}).get('display_name')
        landing=host.get('landing_page_url')
        pdf=host.get('pdf_url')
        print('\nTITLE:',title)
        print(' year',year)
        print(' doi',doi)
        print(' openalex',ids.get('openalex'))
        print(' source',src)
        print(' landing',landing)
        print(' pdf',pdf)
        print(' concepts', [c.get('display_name') for c in w.get('concepts',[])[:6]])
