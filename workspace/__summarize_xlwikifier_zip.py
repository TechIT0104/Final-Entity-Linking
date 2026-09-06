import os
import zipfile
from collections import Counter, defaultdict

path='__xlwikifier_wikidata.zip'
print('exists',os.path.exists(path))
if not os.path.exists(path):
    raise SystemExit('zip missing')

size=os.path.getsize(path)
print('zip_size_bytes',size)

with zipfile.ZipFile(path,'r') as z:
    names=z.namelist()

print('entries',len(names))

# detect language dirs under xlwikifier-wikidata/data/<lang>/test
langs=Counter()
for n in names:
    parts=n.split('/')
    if len(parts)>=5 and parts[0]=='xlwikifier-wikidata' and parts[1]=='data':
        lang=parts[2]
        split=parts[3]
        if split=='test':
            langs[lang]+=1

print('languages_with_test',len(langs))
print('langs',sorted(langs.keys()))

for lang in ['de','es','fr','it']:
    print('count',lang,langs.get(lang,0))

# extension stats
ext=Counter()
for n in names:
    if '.' in n.split('/')[-1]:
        ext_name='.'+n.split('/')[-1].split('.')[-1]
        ext[ext_name]+=1
print('ext_top',ext.most_common(10))

# find mention files
mention_files=[n for n in names if n.endswith('.mentions')]
mention_new=[n for n in names if n.endswith('.mentions.new')]
print('mentions_count',len(mention_files))
print('mentions_new_count',len(mention_new))

# show first 8 mention files for each target lang
for lang in ['de','es','fr','it']:
    ms=[n for n in mention_files if f'/data/{lang}/test/' in n]
    print('\nlang',lang,'mention_files',len(ms))
    for n in ms[:8]:
        print(' ',n)

# identify any consolidated files
for key in ['wikidata', 'tr2016', 'hard', 'README', 'readme']:
    hits=[n for n in names if key.lower() in n.lower()]
    print('\ncontains',key,'count',len(hits))
    for n in hits[:10]:
        print(' ',n)
