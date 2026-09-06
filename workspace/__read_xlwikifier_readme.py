import zipfile
with zipfile.ZipFile('__xlwikifier_wikidata.zip','r') as z:
    txt=z.read('xlwikifier-wikidata/README').decode('utf-8',errors='ignore')
print(txt)
