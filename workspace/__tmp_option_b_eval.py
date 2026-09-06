import paramiko
import os

HOST = '172.20.70.80'
USER = 'kmpooja'
PW = 'kmpooja123'
WORKDIR = '/DATA/kmpooja/mrefined_option1'

print("=" * 80)
print("Option B: Upload corrected mentions and evaluate")
print("=" * 80)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)
sftp = client.open_sftp()

print("\nStep 1: Uploading corrected .mentions.new files...")
print("-" * 80)

local_base = "__mentions_new_corrected"
remote_base = WORKDIR + "/assets/tr2016"

files_uploaded = 0
for lang in ['de', 'es', 'fr', 'it']:
    local_lang_dir = os.path.join(local_base, lang)
    remote_lang_dir = remote_base + "/" + lang + "/test"
    
    if not os.path.exists(local_lang_dir):
        print(f"[{lang}] Directory not found: {local_lang_dir}")
        continue
    
    local_files = [f for f in os.listdir(local_lang_dir) if f.endswith('.mentions.new')]
    print(f"[{lang}] Uploading {len(local_files)} corrected mention files...")
    
    for lfile in local_files:
        local_path = os.path.join(local_lang_dir, lfile)
        remote_path = remote_lang_dir + "/" + lfile
        
        try:
            sftp.put(local_path, remote_path)
            files_uploaded += 1
            if files_uploaded % 500 == 0:
                print(f"  Progress: {files_uploaded} files uploaded...")
        except Exception as e:
            if files_uploaded < 5:
                print(f"  Error uploading {lfile}: {str(e)[:60]}")

sftp.close()
print(f"\nTotal files uploaded: {files_uploaded}")

# Run evaluation
print("\n\nStep 2: Running TR2016 evaluation with corrected mentions...")
print("=" * 80)

eval_cmd = "bash -lc 'cd " + WORKDIR + " && source venv/bin/activate && export PYTHONUNBUFFERED=1 && export CUDA_VISIBLE_DEVICES=0 && timeout 3600 python3 -u ReFinED/src/refined/evaluation/multilingual_e2e_evaluation_tr2016.py --lang_title2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data --mention2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data --model assets/finetune_models/mReFinED_Recall_9343 --data assets/data_combine_11_languages_wikidata_all_eng_label_desc --datasets_root assets/tr2016 2>&1'"

stdin, stdout, stderr = client.exec_command(eval_cmd, get_pty=True)

import sys
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
print(f"Evaluation complete! Exit code: {status}")
print("\nEXPECTED RESULTS:")
print("  Baseline (corrupted .mentions.new): ~2.80% macro recall")
print("  Option B (corrected offsets):       <see above output>")
print("  Expected improvement:                Should show significant recall boost")
print("=" * 80)
