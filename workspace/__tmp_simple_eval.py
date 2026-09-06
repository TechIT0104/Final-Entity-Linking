import paramiko
import sys

HOST = '172.20.70.80'
USER = 'kmpooja'
PW = 'kmpooja123'
WORKDIR = '/DATA/kmpooja/mrefined_option1'

print("=" * 80)
print("Running TR2016 Evaluation with Current Mentions (mixed corrected + original)")
print("=" * 80)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)

eval_cmd = "bash -lc 'cd " + WORKDIR + " && source venv/bin/activate && export PYTHONUNBUFFERED=1 && export CUDA_VISIBLE_DEVICES=0 && timeout 3600 python3 -u ReFinED/src/refined/evaluation/multilingual_e2e_evaluation_tr2016.py --lang_title2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data --mention2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data --model assets/finetune_models/mReFinED_Recall_9343 --data assets/data_combine_11_languages_wikidata_all_eng_label_desc --datasets_root assets/tr2016 2>&1'"

print("\nEvaluation output:")
print("-" * 80)

stdin, stdout, stderr = client.exec_command(eval_cmd, get_pty=True)

while True:
    line = stdout.readline()
    if not line:
        break
    sys.stdout.write(line)
    sys.stdout.flush()

err = stderr.read().decode('utf-8', errors='replace')
if err.strip():
    print('\n[STDERR]')
    print(err)

status = stdout.channel.recv_exit_status()
client.close()

print("\n" + "=" * 80)
print(f"Exit code: {status}")
print("=" * 80)
