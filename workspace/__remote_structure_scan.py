import paramiko
HOST='172.20.70.80'; USER='kmpooja'; PW='kmpooja123'
cmd=r'''
set -e
roots="/DATA /home"
for root in $roots; do
  [ -d "$root" ] || continue
  echo "=== ROOT:$root ==="
  find "$root" -type d -path '*/de/test' 2>/dev/null | head -n 200 | while read d; do
    b="${d%/de/test}"
    if [ -d "$b/es/test" ] && [ -d "$b/fr/test" ] && [ -d "$b/it/test" ]; then
      c1=$(find "$b/de/test" -maxdepth 1 -type f \( -name '*.mentions.new' -o -name '*.mentions' \) 2>/dev/null | wc -l)
      c2=$(find "$b/es/test" -maxdepth 1 -type f \( -name '*.mentions.new' -o -name '*.mentions' \) 2>/dev/null | wc -l)
      c3=$(find "$b/fr/test" -maxdepth 1 -type f \( -name '*.mentions.new' -o -name '*.mentions' \) 2>/dev/null | wc -l)
      c4=$(find "$b/it/test" -maxdepth 1 -type f \( -name '*.mentions.new' -o -name '*.mentions' \) 2>/dev/null | wc -l)
      t1=$(find "$b/de/test" -maxdepth 1 -type f -name '*.txt' 2>/dev/null | wc -l)
      t2=$(find "$b/es/test" -maxdepth 1 -type f -name '*.txt' 2>/dev/null | wc -l)
      t3=$(find "$b/fr/test" -maxdepth 1 -type f -name '*.txt' 2>/dev/null | wc -l)
      t4=$(find "$b/it/test" -maxdepth 1 -type f -name '*.txt' 2>/dev/null | wc -l)
      echo "CAND:$b|m:$c1,$c2,$c3,$c4|t:$t1,$t2,$t3,$t4"
    fi
  done
  echo
 done
'''
cli=paramiko.SSHClient(); cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST,username=USER,password=PW,timeout=30)
_,o,e=cli.exec_command(cmd,timeout=180)
print(o.read().decode('utf-8','replace'))
err=e.read().decode('utf-8','replace').strip()
if err:
  print('ERR:',err)
cli.close()
