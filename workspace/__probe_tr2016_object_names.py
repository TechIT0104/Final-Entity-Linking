import requests, itertools

bases=[
    'http://dl.fbaipublicfiles.com/GENRE/',
    'https://dl.fbaipublicfiles.com/GENRE/',
    'https://s3.amazonaws.com/refined.public/2022_oct/datasets/',
    'https://s3.amazonaws.com/refined.public/2022_oct/',
]

langs=['de','es','fr','it']
seps=['-','_','']

names=set()
# core names
for c in ['tr2016','TR2016','tac_kbp_2016','tac-kbp-2016','kbp2016','tackbp2016','multilingual_tr2016']:
    names.update([
        f'{c}.tar.gz',f'{c}.tgz',f'{c}.zip',f'{c}.jsonl',f'{c}.json',
        f'{c}-test-kilt.jsonl',f'{c}_test_kilt.jsonl',f'{c}-kilt.jsonl'
    ])

# per-lang variants
for lang in langs:
    for c in ['tr2016','TR2016','tac_kbp_2016','kbp2016']:
        for s in ['test','dev','train','']:
            for sep in ['-','_']:
                stem=f'{c}{sep}{lang}' + (f'{sep}{s}' if s else '')
                names.update([
                    f'{stem}.jsonl',f'{stem}.json',f'{stem}.tar.gz',f'{stem}.tgz',
                    f'{stem}-kilt.jsonl',f'{stem}_kilt.jsonl'
                ])
                stem2=f'{lang}{sep}{c}' + (f'{sep}{s}' if s else '')
                names.update([
                    f'{stem2}.jsonl',f'{stem2}.json',f'{stem2}.tar.gz',f'{stem2}.tgz',
                    f'{stem2}-kilt.jsonl',f'{stem2}_kilt.jsonl'
                ])

# likely archive bundles
names.update([
    'TR2016_data.tar.gz','TR2016_dataset.tar.gz','tr2016_dataset.tar.gz','tr2016_data.tar.gz',
    'tr2016_test.tar.gz','tr2016_test_data.tar.gz','tr2016_multilingual.tar.gz',
    'mgenre_tr2016.tar.gz','mgenre_tr2016_data.tar.gz','TR2016.tar.gz',
    'tr2016-kilt.tar.gz','tr2016-kilt.jsonl','TR2016-kilt.jsonl'
])

names=sorted(names)
print('candidate_names',len(names))

session=requests.Session()
session.headers.update({'User-Agent':'Mozilla/5.0'})

hits=[]
for base in bases:
    print('\nBASE',base)
    for i,name in enumerate(names):
        url=base+name
        code=None
        try:
            r=session.get(url,timeout=12,allow_redirects=True,stream=True)
            code=r.status_code
            r.close()
        except Exception:
            continue
        if code in (200,206,302,301):
            print('HIT',code,url)
            hits.append((code,url))
    print('done base')

print('\nTOTAL_HITS',len(hits))
for h in hits:
    print(h[0],h[1])
