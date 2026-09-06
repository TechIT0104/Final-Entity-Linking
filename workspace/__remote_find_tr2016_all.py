import paramiko
servers=[('172.20.70.80','kmpooja','kmpooja123','/DATA'),('172.20.70.170','kmpooja','kmpooja123','/')] 
for host,user,pw,root in servers:
    print('\n'+'='*70)
    print('HOST',host,'ROOT',root)
    c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        c.connect(host,username=user,password=pw,timeout=20)
    except Exception as e:
        print('CONNECT_FAIL',e); continue
    cmd=f"""
find {root} -type f \\
  \( -name '*.mentions.new' -o -name '*.mentions' -o -name '*TR2016*' -o -name '*tr2016*' \) \\
  2>/dev/null | head -n 300
"""
    _,o,e=c.exec_command(cmd,timeout=120)
    out=o.read().decode('utf-8','replace')
    err=e.read().decode('utf-8','replace')
    lines=[ln for ln in out.splitlines() if ln.strip()]
    print('FOUND',len(lines),'entries')
    for ln in lines[:120]:
        print(ln)
    if err.strip():
        print('ERR',err[:500])
    c.close()
