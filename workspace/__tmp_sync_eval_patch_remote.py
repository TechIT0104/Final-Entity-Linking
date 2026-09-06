import paramiko

HOST='172.20.70.80'
USER='kmpooja'
PW='kmpooja123'
REMOTE_BASE='/DATA/kmpooja/mrefined_option1/ReFinED/src/refined/evaluation'

local_eval = r'c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\_tmp_mrefined\src\refined\evaluation\evaluation.py'
local_tr = r'c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\_tmp_mrefined\src\refined\evaluation\multilingual_e2e_evaluation_tr2016.py'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)
sftp = client.open_sftp()

sftp.put(local_eval, REMOTE_BASE + '/evaluation.py')
sftp.put(local_tr, REMOTE_BASE + '/multilingual_e2e_evaluation_tr2016.py')

sftp.close()
client.close()
print('Uploaded patched evaluation.py and multilingual_e2e_evaluation_tr2016.py')
