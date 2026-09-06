import paramiko
host='172.20.70.80'; user='kmpooja'; pwd='kmpooja123'
remote_py = r'''
import os, pickle
base='/DATA/kmpooja/mrefined_option1/assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data'
p=os.path.join(base,'lang_title2wikidataID-normalized_with_redirect.pkl')
with open(p,'rb') as f:
    m=pickle.load(f)
print('map_loaded', len(m))
need={k:[] for k in ['de','es','fr','it','en']}
for key in m.keys():
    if not isinstance(key, tuple) or len(key)!=2:
        continue
    lang,title=key
    if lang in need and len(need[lang])<5:
        need[lang].append(title)
    if all(len(v)>=5 for v in need.values()):
        break
for lang in ['de','es','fr','it','en']:
    print('LANG',lang)
    for t in need[lang]:
        print(' ',repr(t))
'''
cmd = "python3 - << 'PY'\n" + remote_py + "\nPY"
cli=paramiko.SSHClient(); cli.set_missing_host_key_policy(paramiko.AutoAddPolicy()); cli.connect(host,username=user,password=pwd,timeout=30)
stdin,stdout,stderr=cli.exec_command(cmd)
out=stdout.read().decode('utf-8','replace')
err=stderr.read().decode('utf-8','replace')
print(out)
print(err)
cli.close()
