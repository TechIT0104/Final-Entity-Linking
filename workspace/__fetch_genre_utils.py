import requests
u='https://raw.githubusercontent.com/facebookresearch/GENRE/main/genre/utils.py'
r=requests.get(u,timeout=30)
print('status',r.status_code,'len',len(r.text))
open('__genre_utils.py','w',encoding='utf-8').write(r.text)
