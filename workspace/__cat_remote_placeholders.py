import paramiko
host='172.20.70.80'; user='kmpooja'; pwd='kmpooja123'
files=[
'/DATA/kmpooja/mrefined_option1/assets/tr2016/de/test/placeholder.mentions.new',
'/DATA/kmpooja/mrefined_option1/assets/tr2016/es/test/placeholder.mentions.new',
'/DATA/kmpooja/mrefined_option1/assets/tr2016/fr/test/placeholder.mentions.new',
'/DATA/kmpooja/mrefined_option1/assets/tr2016/it/test/placeholder.mentions.new',
]
cli=paramiko.SSHClient(); cli.set_missing_host_key_policy(paramiko.AutoAddPolicy()); cli.connect(host,username=user,password=pwd,timeout=30)
for p in files:
    cmd=f"echo '--- {p}' ; sed -n '1,5p' {p} || true"
    stdin,stdout,stderr=cli.exec_command(cmd)
    print(stdout.read().decode('utf-8','replace'))
    err=stderr.read().decode('utf-8','replace')
    if err.strip():
        print('ERR',err)
cli.close()
