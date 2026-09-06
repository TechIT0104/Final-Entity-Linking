import paramiko, time, re, datetime
host='172.20.70.80'; user='kmpooja'; pw='kmpooja123'
c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy()); c.connect(host,username=user,password=pw,timeout=20)
start_cmd="""
cd /DATA/kmpooja/mrefined_option1
source venv/bin/activate
export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES=0
LOG=/DATA/kmpooja/mrefined_option1/logs/tr2016_gpu_fullprobe_$(date +%Y%m%d_%H%M%S).log
nohup python3 -u ReFinED/src/refined/evaluation/multilingual_e2e_evaluation_tr2016.py \\
  --lang_title2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data \\
  --mention2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data \\
  --model assets/finetune_models/mReFinED_Recall_9343 \\
  --data assets/data_combine_11_languages_wikidata_all_eng_label_desc \\
  --datasets_root assets/tr2016 > \"$LOG\" 2>&1 < /dev/null &
echo PID:$!
echo LOG:$LOG
"""
_,o,e=c.exec_command(start_cmd)
out=o.read().decode('utf-8','replace')
print(out.strip())
pid=re.search(r'PID:(\d+)',out).group(1)
log=re.search(r'LOG:(\S+)',out).group(1)
print('START',datetime.datetime.now().isoformat(),'PID',pid)

for step in range(80):
    _,op,_=c.exec_command(f"ps -p {pid} -o pid=,etime=,cmd= || true")
    psline=op.read().decode('utf-8','replace').strip()
    if not psline:
        print('PROCESS_ENDED_AT_STEP',step)
        break
    _,og,_=c.exec_command("nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader")
    g=og.read().decode('utf-8','replace').strip().replace('\n',' | ')
    _,oa,_=c.exec_command("nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader || true")
    apps=oa.read().decode('utf-8','replace').strip()
    hit=[ln for ln in apps.splitlines() if ln.strip().startswith(pid+',')]
    _,ol,_=c.exec_command(f"grep -E 'Loading mReFinED|Dataset name:|Average recall:|\[LANG' {log} | tail -n 3 || true")
    sig=ol.read().decode('utf-8','replace').strip().replace('\n',' || ')
    print(f"S{step:02d} GPU[{g}] APP[{'; '.join(hit) if hit else 'none'}] SIG[{sig if sig else 'none'}]")
    time.sleep(5)

_,ot,_=c.exec_command(f"tail -n 120 {log} || true")
print('\nFINAL_LOG_TAIL\n'+ot.read().decode('utf-8','replace'))
_,op2,_=c.exec_command(f"ps -p {pid} -o pid= || true")
if op2.read().decode('utf-8','replace').strip():
    c.exec_command(f"kill -9 {pid} || true")
    print('KILLED_REMAINING',pid)
print('LOG_PATH',log)
c.close()
