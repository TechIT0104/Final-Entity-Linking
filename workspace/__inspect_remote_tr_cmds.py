import paramiko

HOST='172.20.70.80'
USER='kmpooja'
PW='kmpooja123'
paths=[
 '/DATA/kmpooja/mrefined_option1/remote_cmd_tr2016_server80.sh',
 '/DATA/kmpooja/mrefined_option1/remote_cmd_tr2016_server170.sh',
 '/home/kmpooja/mrefined_170/remote_cmd_tr2016_server170.sh',
]

cli=paramiko.SSHClient(); cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST,username=USER,password=PW,timeout=20)
for path in paths:
    cmd=f"echo '==== {path} ===='; if [ -f '{path}' ]; then sed -n '1,240p' '{path}'; else echo 'MISSING'; fi"
    _,o,e=cli.exec_command(cmd)
    print(o.read().decode('utf-8','replace'))
    err=e.read().decode('utf-8','replace').strip()
    if err:
        print('ERR:',err)
cli.close()
