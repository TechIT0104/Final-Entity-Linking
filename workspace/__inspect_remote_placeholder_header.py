import paramiko
host='172.20.70.80'; user='kmpooja'; pwd='kmpooja123'
path='/DATA/kmpooja/mrefined_option1/assets/tr2016/de/test/placeholder.mentions.new'
cli=paramiko.SSHClient(); cli.set_missing_host_key_policy(paramiko.AutoAddPolicy()); cli.connect(host,username=user,password=pwd,timeout=30)
cmd=f"python3 - << 'PY'\nimport pandas as pd\np='{path}'\ntry:\n d=pd.read_csv(p,sep='\\t')\n print('COLUMNS',list(d.columns))\n print('ROW0',d.head(1).to_dict(orient='records'))\nexcept Exception as e:\n print('ERR',e)\nPY"
stdin,stdout,stderr=cli.exec_command(cmd)
print(stdout.read().decode('utf-8','replace'))
print(stderr.read().decode('utf-8','replace'))
cli.close()
