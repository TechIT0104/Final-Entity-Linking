import paramiko
import os

HOST = '172.20.70.80'
USER = 'kmpooja'
PW = 'kmpooja123'
WORKDIR = '/DATA/kmpooja/mrefined_option1'

print("=" * 80)
print("Option B Fix: Create filename mapping and upload correctly")
print("=" * 80)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)
sftp = client.open_sftp()

print("\nStep 1: Query remote for actual .txt filenames...")
print("-" * 80)

# Get list of .txt files on remote for each language
txt_mapping = {}  # {lang: {sanitized_name: actual_name}}

for lang in ['de', 'es', 'fr', 'it']:
    remote_dir = WORKDIR + "/assets/tr2016/" + lang + "/test"
    
    try:
        sftp.chdir(remote_dir)
        remote_files = sftp.listdir()
        txt_files = [f for f in remote_files if f.endswith('.txt')]
        
        txt_mapping[lang] = {}
        for txt_file in txt_files:
            # Create sanitized version (same as we did locally)
            sanitized = txt_file.replace('.txt', '').replace(':', '_').replace('<', '_').replace('>', '_').replace('"', '_').replace('|', '_').replace('?', '_').replace('*', '_')
            txt_mapping[lang][sanitized] = txt_file.replace('.txt', '')
        
        print(f"[{lang}] Found {len(txt_files)} .txt files")
        if txt_files:
            print(f"        Sample: {txt_files[0]}")
    except Exception as e:
        print(f"[{lang}] Error: {str(e)[:80]}")

sftp.close()

print("\nStep 2: Create corrected upload list with proper filenames...")
print("-" * 80)

# Map our local corrected mentions to actual remote filenames
upload_map = {}  # {lang: [(local_file, remote_filename)]}

local_base = "__mentions_new_corrected"
for lang in ['de', 'es', 'fr', 'it']:
    local_lang_dir = os.path.join(local_base, lang)
    upload_map[lang] = []
    
    if os.path.exists(local_lang_dir):
        local_files = [f for f in os.listdir(local_lang_dir) if f.endswith('.mentions.new')]
        
        for lfile in local_files:
            # Extract base name (remove .mentions.new)
            base = lfile.replace('.mentions.new', '')
            
            # Look up actual remote filename
            if base in txt_mapping.get(lang, {}):
                actual_name = txt_mapping[lang][base]
                upload_map[lang].append((lfile, actual_name + '.mentions.new'))
            else:
                # If mapping not found, use sanitized name (fallback)
                upload_map[lang].append((lfile, lfile))

print("Upload mapping created")
for lang in ['de', 'es', 'fr', 'it']:
    print(f"  [{lang}] {len(upload_map[lang])} files to upload")

print("\nStep 3: Upload corrected mentions with correct filenames...")
print("-" * 80)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)
sftp = client.open_sftp()

files_uploaded = 0
for lang in ['de', 'es', 'fr', 'it']:
    local_lang_dir = os.path.join(local_base, lang)
    remote_lang_dir = WORKDIR + "/assets/tr2016/" + lang + "/test"
    
    for local_file, remote_file in upload_map[lang]:
        local_path = os.path.join(local_lang_dir, local_file)
        remote_path = remote_lang_dir + "/" + remote_file
        
        try:
            sftp.put(local_path, remote_path)
            files_uploaded += 1
            if files_uploaded % 500 == 0:
                print(f"  Progress: {files_uploaded} files uploaded...")
        except Exception as e:
            if files_uploaded < 5:
                print(f"  Error uploading {remote_file}: {str(e)[:60]}")

sftp.close()
print(f"\nTotal files uploaded: {files_uploaded}")

# Run evaluation
print("\n\nStep 4: Running TR2016 evaluation with corrected mentions...")
print("=" * 80)

eval_cmd = "bash -lc 'cd " + WORKDIR + " && source venv/bin/activate && export PYTHONUNBUFFERED=1 && export CUDA_VISIBLE_DEVICES=0 && timeout 3600 python3 -u ReFinED/src/refined/evaluation/multilingual_e2e_evaluation_tr2016.py --lang_title2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data --mention2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data --model assets/finetune_models/mReFinED_Recall_9343 --data assets/data_combine_11_languages_wikidata_all_eng_label_desc --datasets_root assets/tr2016 2>&1'"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)

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
print("=" * 80)
