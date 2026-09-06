import requests
u='https://raw.githubusercontent.com/amazon-science/ReFinED/mrefined/src/refined/evaluation/multilingual_e2e_evaluation_tr2016.py'
r=requests.get(u,timeout=30)
print('status',r.status_code,'len',len(r.text))
open('__mrefined_eval_tr2016.py','w',encoding='utf-8').write(r.text)
