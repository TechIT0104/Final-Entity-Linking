import paramiko
host='172.20.70.80'; user='kmpooja'; pw='kmpooja123'
cmd="""
cd /DATA/kmpooja/mrefined_option1
source venv/bin/activate
export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES=0
timeout 60s python3 -u ReFinED/src/refined/evaluation/multilingual_e2e_evaluation_tr2016.py \\
  --lang_title2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data \\
  --mention2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data \\
  --model assets/finetune_models/mReFinED_Recall_9343 \\
  --data assets/data_combine_11_languages_wikidata_all_eng_label_desc \\
  --datasets_root assets/tr2016
"""
c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy()); c.connect(host,username=user,password=pw,timeout=20)
_,o,e=c.exec_command(cmd,timeout=90)
out=o.read().decode('utf-8','replace')
err=e.read().decode('utf-8','replace')
print('STDOUT_BEGIN')
print(out)
print('STDOUT_END')
print('STDERR_BEGIN')
print(err)
print('STDERR_END')
c.close()
