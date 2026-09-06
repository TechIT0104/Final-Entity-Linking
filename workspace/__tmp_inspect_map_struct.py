import paramiko

HOST='172.20.70.80'
USER='kmpooja'
PW='kmpooja123'

cli=paramiko.SSHClient(); cli.set_missing_host_key_policy(paramiko.AutoAddPolicy()); cli.connect(HOST,username=USER,password=PW,timeout=30)
remote = r'''python3 - <<"PY"
import os,pickle,itertools
p='/DATA/kmpooja/mrefined_option1/assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data/lang_title2wikidataID-normalized_with_redirect.pkl'
with open(p,'rb') as f:
    m=pickle.load(f)
print('type', type(m))
if isinstance(m, dict):
    print('len', len(m))
    k=list(m.keys())[:10]
    print('top_keys_sample', k)
    first_key=k[0] if k else None
    if first_key is not None:
        v=m[first_key]
        print('first_key_type', type(v))
        if isinstance(v, dict):
            print('first_key_dict_len', len(v))
            sk=list(v.keys())[:5]
            print('subkeys_sample', sk)
            if sk:
                print('subval_sample', v[sk[0]])
# search for known title variants
cands=['rhinluch','norman robert pogson','departamento de antioquia','canard','gel di silice']
for c in cands:
    found=[]
    if isinstance(m, dict):
        if c in m:
            found.append(('top',m[c]))
        for lk in list(m.keys())[:20]:
            v=m[lk]
            if isinstance(v, dict) and c in v:
                found.append((lk,v[c]))
    print(c,'found',found[:3])
PY'''
_,so,se=cli.exec_command(remote)
out=so.read().decode('utf-8','replace'); err=se.read().decode('utf-8','replace')
print(out)
if err.strip(): print('ERR:\n'+err)
cli.close()
