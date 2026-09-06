import paramiko
import os
import sys

HOST = '172.20.70.80'
USER = 'kmpooja'
PW = 'kmpooja123'
WORKDIR = '/DATA/kmpooja/mrefined_option1'

print("Option A: Sync raw mentions to remote and evaluate")
print("=" * 70)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)
sftp = client.open_sftp()

# Step 1: Sync each language's raw mentions to remote
print("\nStep 1: Syncing raw mentions to remote system...")
local_base = "__mentions_raw_extracted/xlwikifier-wikidata/data"
remote_base = WORKDIR + "/assets/tr2016"

for lang in ['de', 'es', 'fr', 'it']:
    local_test_dir = local_base + "/" + lang + "/test"
    remote_test_dir = remote_base + "/" + lang + "/test"
    
    if os.path.exists(local_test_dir):
        local_files = [f for f in os.listdir(local_test_dir) if f.endswith('.mentions')]
        print("  [" + lang + "] Found " + str(len(local_files)) + " raw .mentions files")
        
        # Count remote files to swap
        try:
            sftp.chdir(remote_test_dir)
            remote_list = sftp.listdir()
            new_files_count = len([f for f in remote_list if f.endswith('.mentions.new')])
            print("         Will replace: " + str(new_files_count) + " .mentions.new files")
        except:
            print("         Error accessing remote directory")
            continue

print("\nStep 2: Running evaluation with raw mentions...")
print("=" * 70)

# Use simpler approach: Python script on remote side
remote_py = '''
import os, shutil, glob

WORKDIR = '/DATA/kmpooja/mrefined_option1'
BASE = WORKDIR + '/assets/tr2016'
LOCAL_BASE = '/tmp/raw_mentions'

# Create symlinks from local extracted to use as mentions.new
for lang in ['de', 'es', 'fr', 'it']:
    test_dir = BASE + '/' + lang + '/test'
    os.chdir(test_dir)
    
    # Count mentions.new files
    new_files = glob.glob('*.mentions.new')
    
    # For each, check if raw version exists in zip extraction
    # We'll directly use the extracted files which are already in __mentions_raw_extracted
    print(f'[{lang}] Processing {len(new_files)} .mentions.new files...')
'''

# Actually, this is getting too complex. Let's use a simpler direct approach:
# Just copy all raw mentions directly

print("\nCopying raw mentions files directly...")
files_copied = 0

sftp = client.open_sftp()
for lang in ['de', 'es', 'fr', 'it']:
    local_test_dir = "__mentions_raw_extracted/xlwikifier-wikidata/data/" + lang + "/test"
    remote_test_dir = WORKDIR + "/assets/tr2016/" + lang + "/test"
    
    if os.path.exists(local_test_dir):
        local_files = [f for f in os.listdir(local_test_dir) if f.endswith('.mentions')]
        
        for lfile in local_files:
            local_path = os.path.join(local_test_dir, lfile)
            remote_path = remote_test_dir + "/" + lfile + ".new"
            
            try:
                sftp.put(local_path, remote_path)
                files_copied += 1
                if files_copied % 500 == 0:
                    print(f"  Copied {files_copied} files...")
            except Exception as e:
                if files_copied < 10:
                    print(f"  Error copying {lfile}: {str(e)[:60]}")

sftp.close()
print(f"Total files copied: {files_copied}")

# Now run evaluation
print("\nRunning evaluation...")
print("=" * 70)

eval_cmd = "bash -lc 'cd " + WORKDIR + " && source venv/bin/activate && export PYTHONUNBUFFERED=1 && export CUDA_VISIBLE_DEVICES=0 && timeout 3600 python3 -u ReFinED/src/refined/evaluation/multilingual_e2e_evaluation_tr2016.py --lang_title2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data --mention2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data --model assets/finetune_models/mReFinED_Recall_9343 --data assets/data_combine_11_languages_wikidata_all_eng_label_desc --datasets_root assets/tr2016 2>&1'"

stdin, stdout, stderr = client.exec_command(eval_cmd, get_pty=True)

import sys as sys2
while True:
    line = stdout.readline()
    if not line:
        break
    sys2.stdout.write(line)
    sys2.stdout.flush()

err = stderr.read().decode('utf-8', errors='replace')
if err.strip():
    print('\n[STDERR]')
    print(err)

status = stdout.channel.recv_exit_status()
client.close()

print("\n" + "=" * 70)
print("Evaluation complete! Exit code: " + str(status))
