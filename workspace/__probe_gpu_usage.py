import paramiko, time, re
host='172.20.70.80'; user='kmpooja'; pw='kmpooja123'
cmd_run="""
cd /DATA/kmpooja/mrefined_option1
source venv/bin/activate
export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES=0
LOG=/DATA/kmpooja/mrefined_option1/logs/tr2016_gpu_probe_$(date +%Y%m%d_%H%M%S).log
nohup python3 -u ReFinED/src/refined/evaluation/multilingual_e2e_evaluation_tr2016.py \\
  --lang_title2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data \\
  --mention2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data \\
  --model assets/finetune_models/mReFinED_Recall_9343 \\
  --data assets/data_combine_11_languages_wikidata_all_eng_label_desc \\
  --datasets_root assets/tr2016 > "$LOG" 2>&1 < /dev/null &
echo PID:$!
echo LOG:$LOG
"""
c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy()); c.connect(host,username=user,password=pw,timeout=20)
_,o,e=c.exec_command(cmd_run)
out=o.read().decode('utf-8','replace'); err=e.read().decode('utf-8','replace')
print(out.strip());
if err.strip(): print('ERR',err.strip())
pid=re.search(r'PID:(\d+)',out)
logm=re.search(r'LOG:(\S+)',out)
if not pid:
    print('FAILED_TO_START'); c.close(); raise SystemExit
pid=pid.group(1); log=logm.group(1) if logm else ''
print('Monitoring pid',pid)
for i in range(12):
    chk=f"ps -p {pid} -o pid=,etime=,cmd= || true"
    _,o1,e1=c.exec_command(chk)
    psline=o1.read().decode('utf-8','replace').strip()
    if not psline:
        print('process ended at sample',i)
        break
    print('PS',psline)
    gpu="nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader || true"
    _,o2,e2=c.exec_command(gpu)
    apps=o2.read().decode('utf-8','replace').strip().splitlines()
    hit=[a for a in apps if a.strip().startswith(pid+',')]
    print('GPU_HIT',hit if hit else 'none')
    time.sleep(1.5)

_,o3,e3=c.exec_command(f"tail -n 40 {log} || true")
print('\nLOG_TAIL\n'+o3.read().decode('utf-8','replace'))
# cleanup pid if still running
_,o4,e4=c.exec_command(f"ps -p {pid} -o pid= || true")
if o4.read().decode('utf-8','replace').strip():
    c.exec_command(f"kill -9 {pid} || true")
    print('Killed probe pid',pid)
print('log',log)
c.close()
