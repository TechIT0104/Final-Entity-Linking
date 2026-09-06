import requests
url='https://web.archive.org/web/20190420080619id_/http://bilbo.cs.illinois.edu:80/page/publication_view/810'
r=requests.get(url,timeout=60,headers={'User-Agent':'Mozilla/5.0'})
print('status',r.status_code,'len',len(r.text))
open('__wb_publication_810_20190420.html','w',encoding='utf-8',errors='ignore').write(r.text)
