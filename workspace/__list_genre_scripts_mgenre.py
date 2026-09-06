import requests
u='https://api.github.com/repos/facebookresearch/GENRE/contents/scripts_mgenre'
r=requests.get(u,timeout=30,headers={'User-Agent':'Mozilla/5.0'})
print('status',r.status_code)
if r.status_code==200:
    data=r.json()
    for x in data:
        print(x.get('name'), x.get('download_url'))
else:
    print(r.text[:500])
