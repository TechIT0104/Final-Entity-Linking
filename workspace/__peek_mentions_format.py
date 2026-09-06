import zipfile, random
z=zipfile.ZipFile('__xlwikifier_wikidata.zip','r')
cands=[n for n in z.namelist() if '/data/de/test/' in n and n.endswith('.mentions')]
print('de mention files',len(cands))
for n in cands[:3]:
    b=z.read(n).decode('utf-8','replace').splitlines()[:5]
    print('\nFILE',n)
    for line in b:
        print(line)
