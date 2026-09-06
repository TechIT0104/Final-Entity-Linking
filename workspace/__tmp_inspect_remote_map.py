import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PW = "kmpooja123"
WORKDIR = "/DATA/kmpooja/mrefined_option1"
REMOTE_SCRIPT = WORKDIR + "/__tmp_inspect_map.py"

remote_py = r'''
import os
import pickle

p = '/DATA/kmpooja/mrefined_option1/assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data/lang_title2wikidataID-normalized_with_redirect.pkl'
with open(p, 'rb') as f:
    m = pickle.load(f)

print('type', type(m))
if isinstance(m, dict):
    keys = list(m.keys())
    print('top_len', len(keys))
    print('top_sample', keys[:10])
    if keys:
        v = m[keys[0]]
        print('first_val_type', type(v))
        if isinstance(v, dict):
            sk = list(v.keys())[:5]
            print('sub_len', len(v))
            print('sub_sample', sk)
            if sk:
                print('sub_val_sample', v[sk[0]])

queries = ['de', 'es', 'fr', 'it', 'rhinluch', 'norman robert pogson', 'departamento de antioquia', 'gel di silice']
for q in queries:
    found = []
    if isinstance(m, dict):
        if q in m:
            found.append(('top', str(m[q])[:80]))
        for lk in list(m.keys())[:200]:
            v = m[lk]
            if isinstance(v, dict) and q in v:
                found.append((lk, str(v[q])[:80]))
    print('query', q, 'found', found[:5])
'''

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)

sftp = client.open_sftp()
with sftp.open(REMOTE_SCRIPT, 'w') as f:
    f.write(remote_py)
sftp.close()

cmd = (
    "bash -lc 'python3 " + REMOTE_SCRIPT + " ; rc=$?; rm -f " + REMOTE_SCRIPT + "; echo __RC__:$rc'"
)

_, so, se = client.exec_command(cmd, get_pty=True)
out = so.read().decode('utf-8', errors='replace')
err = se.read().decode('utf-8', errors='replace')
print(out)
if err.strip():
    print('[STDERR]')
    print(err)

client.close()
