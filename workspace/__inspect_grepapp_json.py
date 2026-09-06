import requests, json
q='lang_title2wikidataID-normalized_with_redirect.pkl'
r=requests.get('https://grep.app/api/search',params={'q':q,'regexp':'false','case':'false'},timeout=40,headers={'User-Agent':'Mozilla/5.0'})
print('status',r.status_code)
js=r.json()
print('keys',js.keys())
print('hits keys',js.get('hits',{}).keys())
print('hits sample type',type(js.get('hits',{}).get('hits',[])))
print('first',js.get('hits',{}).get('hits',[])[0] if js.get('hits',{}).get('hits',[]) else None)
open('__grepapp_sample.json','w',encoding='utf-8').write(json.dumps(js)[:20000])
