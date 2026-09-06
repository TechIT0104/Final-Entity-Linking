import requests
u='https://raw.githubusercontent.com/facebookresearch/GENRE/main/scripts_genre/download_all_datasets.sh'
r=requests.get(u,timeout=30)
print('status',r.status_code,'len',len(r.text))
open('__genre_download_all_datasets.sh','w',encoding='utf-8').write(r.text)
