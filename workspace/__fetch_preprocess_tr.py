import requests
u='https://raw.githubusercontent.com/facebookresearch/GENRE/main/scripts_mgenre/preprocess_TR2016.py'
r=requests.get(u,timeout=30)
print('status',r.status_code,'len',len(r.text))
open('__preprocess_TR2016.py','w',encoding='utf-8').write(r.text)
