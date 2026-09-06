import requests
import re

urls=[
 'http://cogcomp.cs.illinois.edu/',
 'https://cogcomp.cs.illinois.edu/',
 'http://cogcomp.org/',
 'https://cogcomp.org/',
 'http://cogcomp.seas.upenn.edu/',
 'https://cogcomp.seas.upenn.edu/',
 'https://cogcomp.illinois.edu/',
 'https://cogcomp.cs.illinois.edu/page/publications/',
 'https://cogcomp.cs.illinois.edu/page/publication_view/810',
 'https://cogcomp.org/page/publications/',
 'https://cogcomp.org/page/publication_view/810',
]
for u in urls:
    try:
        r=requests.get(u,timeout=30,headers={'User-Agent':'Mozilla/5.0'},allow_redirects=True)
        print('\nURL',u)
        print(' status',r.status_code,'final',r.url,'len',len(r.text))
        if r.status_code==200:
            title=re.search(r'<title>(.*?)</title>',r.text,re.I|re.S)
            print(' title',title.group(1).strip() if title else 'N/A')
            links=sorted(set(re.findall(r'href=["\']([^"\']+)["\']',r.text,re.I)))
            for l in links[:80]:
                if any(k in l.lower() for k in ['publication','resource','data','download','view-controller','controller','json','api','backend','tr2016','wikification','tsai','roth']):
                    print('  ',l)
    except Exception as ex:
        print('\nURL',u,'ERR',ex)
