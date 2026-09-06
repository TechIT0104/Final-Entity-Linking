import paramiko
servers=[('172.20.70.80','kmpooja','kmpooja123'),('172.20.70.170','kmpooja','kmpooja123')]
for host,user,pw in servers:
    print('\n'+'='*70)
    print('HOST',host)
    c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        c.connect(host,username=user,password=pw,timeout=20)
    except Exception as e:
        print('CONNECT_FAIL',e)
        continue
    cmds=[
        "hostname",
        "nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv,noheader || true",
        "cd /DATA/kmpooja/mrefined_option1 ; source venv/bin/activate ; python3 -c \"import torch;print('torch',torch.__version__);print('cuda_available',torch.cuda.is_available());print('device_count',torch.cuda.device_count());print('current_device',torch.cuda.current_device() if torch.cuda.is_available() else -1);print('device_name',torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NA')\""
    ]
    for cmd in cmds:
        print('\n$ '+cmd)
        _,o,e=c.exec_command(cmd)
        out=o.read().decode('utf-8','replace').strip()
        err=e.read().decode('utf-8','replace').strip()
        if out: print(out)
        if err: print('ERR:',err)
    c.close()
