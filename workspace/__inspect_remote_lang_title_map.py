import paramiko
host='172.20.70.80'; user='kmpooja'; pwd='kmpooja123'
cmd="""
python3 - << 'PY'
import os, pickle, random
base='/DATA/kmpooja/mrefined_option1/assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data'
p=os.path.join(base,'lang_title2wikidataID-normalized_with_redirect.pkl')
with open(p,'rb') as f:
    m=pickle.load(f)
print('map_size',len(m))
keys=list(m.keys())
print('sample_keys',keys[:5])
for lang in ['de','es','fr','it','en']:
    vals=[k for k in keys if isinstance(k,tuple) and len(k)==2 and k[0]==lang][:5]
    print('lang',lang,'sample',vals)
PY
"""
cli=paramiko.SSHClient(); cli.set_missing_host_key_policy(paramiko.AutoAddPolicy()); cli.connect(host,username=user,password=pwd,timeout=30)
stdin,stdout,stderr=cli.exec_command(cmd)
print(stdout.read().decode('utf-8','replace'))
print(stderr.read().decode('utf-8','replace'))
cli.close()
