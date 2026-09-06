import datetime
import re
import paramiko

HOST='172.20.70.80'
USER='kmpooja'
PW='kmpooja123'
WORKDIR='/DATA/kmpooja/mrefined_option1'

ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
log_no = f"{WORKDIR}/logs/tr2016_offset_ab_no_{ts}.log"
log_yes = f"{WORKDIR}/logs/tr2016_offset_ab_yes_{ts}.log"

base_cmd = (
    "python3 -u ReFinED/src/refined/evaluation/multilingual_e2e_evaluation_tr2016.py "
    "--lang_title2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data "
    "--mention2wikidata assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data "
    "--model assets/finetune_models/mReFinED_Recall_9343 "
    "--data assets/data_combine_11_languages_wikidata_all_eng_label_desc "
    "--datasets_root assets/tr2016 "
    "--device cuda:0"
)

cmd_no = (
    "bash -lc 'cd {wd}; source venv/bin/activate; export PYTHONUNBUFFERED=1; export CUDA_VISIBLE_DEVICES=0; "
    "timeout 3600 {cmd} > {log} 2>&1'"
).format(wd=WORKDIR, cmd=base_cmd, log=log_no)

cmd_yes = (
    "bash -lc 'cd {wd}; source venv/bin/activate; export PYTHONUNBUFFERED=1; export CUDA_VISIBLE_DEVICES=0; "
    "timeout 3600 {cmd} --validate_gold_offsets > {log} 2>&1'"
).format(wd=WORKDIR, cmd=base_cmd, log=log_yes)


def run_and_wait(client, command, label):
    print(f"START {label}")
    _, so, se = client.exec_command(command)
    rc = so.channel.recv_exit_status()
    err = se.read().decode('utf-8', errors='replace').strip()
    if err:
        print(f"{label} STDERR:\n{err}")
    print(f"END {label} RC={rc}")
    return rc


def fetch_summary(client, log_path):
    grep_cmd = (
        "bash -lc \"grep -E 'Dataset name:|Recall:|Average recall:|Traceback' "
        + log_path
        + " || true\""
    )
    _, so, _ = client.exec_command(grep_cmd)
    key_lines = so.read().decode('utf-8', errors='replace')
    match = re.findall(r"Average recall:\s*([0-9.]+)", key_lines)
    avg = float(match[-1]) if match else None
    return avg, key_lines


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)

print(f"LOG_NO={log_no}")
print(f"LOG_YES={log_yes}")

rc_no = run_and_wait(client, cmd_no, 'NO_VALIDATION')
rc_yes = run_and_wait(client, cmd_yes, 'WITH_VALIDATION')

avg_no, key_no = fetch_summary(client, log_no)
avg_yes, key_yes = fetch_summary(client, log_yes)

print("AB_RESULTS")
print(f"RC_NO={rc_no}")
print(f"RC_YES={rc_yes}")
print(f"AVG_NO={avg_no}")
print(f"AVG_YES={avg_yes}")
if avg_no is not None and avg_yes is not None:
    print(f"DELTA={avg_yes-avg_no:.6f}")

print("KEY_NO_BEGIN")
print(key_no)
print("KEY_NO_END")
print("KEY_YES_BEGIN")
print(key_yes)
print("KEY_YES_END")

client.close()
