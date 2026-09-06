import os
import requests
import zipfile

url='https://cogcomp.seas.upenn.edu/Data/ccgPapersData/ctsai12/xlwikifier-wikidata.zip'
print('URL',url)

try:
    h=requests.head(url,allow_redirects=True,timeout=30,headers={'User-Agent':'Mozilla/5.0'})
    print('HEAD status',h.status_code)
    print(' final',h.url)
    print(' content-type',h.headers.get('Content-Type'))
    print(' content-length',h.headers.get('Content-Length'))
except Exception as ex:
    print('HEAD err',ex)

# Try lightweight GET first bytes to ensure access
r=requests.get(url,stream=True,timeout=60,headers={'User-Agent':'Mozilla/5.0'})
print('GET status',r.status_code)
print('GET type',r.headers.get('Content-Type'))
print('GET len',r.headers.get('Content-Length'))

size=int(r.headers.get('Content-Length') or 0)
max_download=300*1024*1024
if size==0 or size<=max_download:
    path='__xlwikifier_wikidata.zip'
    with open(path,'wb') as f:
        for i,chunk in enumerate(r.iter_content(chunk_size=1024*1024)):
            if chunk:
                f.write(chunk)
            if i%20==0:
                print(' downloaded_mb', (i+1))
    print('saved',path,'bytes',os.path.getsize(path))

    try:
        with zipfile.ZipFile(path,'r') as z:
            names=z.namelist()
            print('zip entries',len(names))
            for n in names[:200]:
                print(' ',n)
            # look for tr2016-ish / mentions files
            print('\nLIKELY TR FILES')
            for n in names:
                low=n.lower()
                if any(k in low for k in ['tr2016','mentions','wikidata','de/','es/','fr/','it/','test','hard']):
                    print(' ',n)
    except Exception as ex:
        print('zip inspect err',ex)
else:
    print('skip download due size',size)
