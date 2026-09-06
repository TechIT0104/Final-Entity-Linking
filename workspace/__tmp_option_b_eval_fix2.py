import paramiko
import os

HOST = '172.20.70.80'
USER = 'kmpooja'
PW = 'kmpooja123'
WORKDIR = '/DATA/kmpooja/mrefined_option1'

print("=" * 80)
print("Option B Fix v2: Restore original .mentions.new for missing documents")
print("=" * 80)

print("\nStep 1: Check which documents need restore...")
print("-" * 80)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)

print("\nStep 2: Query remote for backup files and restore...")
print("-" * 80)

# Execute remote script to restore
restore_cmd = WORKDIR + '''\
import os, glob, shutil

BASE = "/DATA/kmpooja/mrefined_option1/assets/tr2016"

for lang in ["de", "es", "fr", "it"]:
    test_dir = BASE + "/" + lang + "/test"
    corrupted = glob.glob(test_dir + "/*.mentions.new.corrupted")
    print("[" + lang + "] Found " + str(len(corrupted)) + " backup files")
    for backup_file in corrupted:
        base = backup_file.replace(".mentions.new.corrupted", "")
        current = base + ".mentions.new"
        try:
            if not os.path.exists(current) or os.path.getsize(current) == 0:
                shutil.copy(backup_file, current)
        except:
            pass
print("Restore complete")
'''

cmd = "cd " + WORKDIR + " && python3 - << 'EOF'\nimport os, glob, shutil\nBASE = '" + WORKDIR + "/assets/tr2016'\nfor lang in ['de', 'es', 'fr', 'it']:\n    test_dir = BASE + '/' + lang + '/test'\n    corrupted = glob.glob(test_dir + '/*.mentions.new.corrupted')\n    print('[' + lang + '] Found ' + str(len(corrupted)) + ' backup files')\n    for backup_file in corrupted:\n        base = backup_file.replace('.mentions.new.corrupted', '')\n        current = base + '.mentions.new'\n        try:\n            if not os.path.exists(current) or os.path.getsize(current) == 0:\n                shutil.copy(backup_file, current)\n        except:\n            pass\nprint('Restore complete')\nEOF\n"

stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)

import sys
while True:
    line = stdout.readline()
    if not line:
        break
    sys.stdout.write(line)
    sys.stdout.flush()

err = stderr.read().decode('utf-8', errors='replace')
if err.strip():
    print('[stderr] ' + err[:200])

status = stdout.channel.recv_exit_status()

# Step 3: Run evaluation
print("\n\nStep 3: Running TR2016 evaluation with mixed (corrected + original) mentions...")
print("=" * 80)

eval_cmd = "bash -lc 'cd " + WORKDIR + " && source venv/bin/activate && export PYTHONUNBUFFERED=1 && export CUDA_VISIBLE_DEVICES=0 && timeout 3600 python3 -u ReFinED/src/refined/evaluation/multilingual_e2e_evaluation_tr2016.py --lang_title2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data --mention2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data --model assets/finetune_models/mReFinED_Recall_9343 --data assets/data_combine_11_languages_wikidata_all_eng_label_desc --datasets_root assets/tr2016 2>&1'"

stdin2, stdout2, stderr2 = client.exec_command(eval_cmd, get_pty=True)

while True:
    line = stdout2.readline()
    if not line:
        break
    sys.stdout.write(line)
    sys.stdout.flush()

err2 = stderr2.read().decode('utf-8', errors='replace')
if err2.strip() and 'Traceback' in err2:
    print('\n[STDERR]')
    print(err2)

status2 = stdout2.channel.recv_exit_status()
client.close()

print("\n" + "=" * 80)
print(f"Evaluation complete! Exit code: {status2}")
print("\nCOMPARISON:")
print("  Baseline (all corrupted):     2.80% macro recall")
print("  Option B (mixed clean+orig):  <see above output>")
print("=" * 80)
