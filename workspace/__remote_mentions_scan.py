import paramiko
HOST='172.20.70.80';USER='kmpooja';PW='kmpooja123'
cmd=r'''
set -e
find /DATA /home -type f \( -name '*.mentions' -o -name '*.mentions.new' \) 2>/dev/null | head -n 400 > /tmp/_mfiles_list.txt || true
count=$(wc -l < /tmp/_mfiles_list.txt)
echo "TOTAL_LISTED:$count"
idx=0
while IFS= read -r f; do
  idx=$((idx+1))
  h=$(head -n 1 "$f" 2>/dev/null || true)
  p=$(dirname "$f")
  echo "[$idx] $f"
  echo "    HEAD:$h"
  if [ $idx -ge 120 ]; then break; fi
done < /tmp/_mfiles_list.txt
'''
cli=paramiko.SSHClient(); cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST,username=USER,password=PW,timeout=30)
_,o,e=cli.exec_command(cmd,timeout=240)
out=o.read().decode('utf-8','replace')
err=e.read().decode('utf-8','replace').strip()
print(out)
if err:
    print('ERR:',err)
cli.close()
