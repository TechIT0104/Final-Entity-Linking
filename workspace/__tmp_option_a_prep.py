import paramiko

HOST='172.20.70.80'
USER='kmpooja'
PW='kmpooja123'
WORKDIR='/DATA/kmpooja/mrefined_option1'

# First write the Python script to the remote system
remote_py = """import os, glob, shutil

# Backup and replace corrupted .mentions.new with raw .mentions
base = '/DATA/kmpooja/mrefined_option1/assets/tr2016'
for lang in ['de', 'es', 'fr', 'it']:
    lang_dir = base + '/' + lang + '/test'
    mentions_new_files = glob.glob(lang_dir + '/*.mentions.new')
    print('[' + lang + '] Found ' + str(len(mentions_new_files)) + ' .mentions.new files')
    
    for mentions_new in mentions_new_files:
        raw_mentions = mentions_new.replace('.mentions.new', '.mentions')
        if os.path.exists(raw_mentions):
            # Backup the corrupted version
            backup = mentions_new + '.bak'
            if not os.path.exists(backup):
                shutil.copy(mentions_new, backup)
                print('  Backed up: ' + os.path.basename(mentions_new))
            
            # Copy raw .mentions to .mentions.new
            shutil.copy(raw_mentions, mentions_new)
            print('  Replaced: ' + os.path.basename(mentions_new) + ' with raw .mentions')
        else:
            print('  WARNING: No raw .mentions found for ' + os.path.basename(mentions_new))

print('Option A prep complete')
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)

# Write the script to remote
cmd = "cat > /DATA/kmpooja/mrefined_option1/__tmp_option_a_prep.py << 'EOF_SCRIPT'\n" + remote_py + "\nEOF_SCRIPT"
stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
status = stdout.channel.recv_exit_status()

# Execute it
cmd2 = "cd " + WORKDIR + " && source venv/bin/activate && python3 __tmp_option_a_prep.py"
stdin2, stdout2, stderr2 = client.exec_command(cmd2, get_pty=True)

import sys
while True:
    line = stdout2.readline()
    if not line:
        break
    sys.stdout.write(line)
    sys.stdout.flush()

err = stderr2.read().decode('utf-8', errors='replace')
if err.strip():
    print('\n[STDERR]')
    print(err)

status = stdout2.channel.recv_exit_status()
print('\n__EXIT_CODE:' + str(status))
client.close()
