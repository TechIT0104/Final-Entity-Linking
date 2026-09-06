import requests

params={
    'url':'bilbo.cs.illinois.edu/*',
    'output':'json',
    'fl':'timestamp,original,mimetype,statuscode,length',
    'filter':'statuscode:200',
    'from':'2014',
    'to':'2020',
    'collapse':'urlkey',
    'limit':'50000'
}
r=requests.get('https://web.archive.org/cdx/search/cdx',params=params,timeout=60,headers={'User-Agent':'Mozilla/5.0'})
print('status',r.status_code,'len',len(r.text))
if r.status_code==200:
    data=r.json()
    print('rows',len(data)-1)
    for row in data[1:]:
        ts,orig,mime,sc,length=row
        print(ts,orig,mime,length)
