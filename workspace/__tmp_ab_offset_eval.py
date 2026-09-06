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
    "timeout 3600 {cmd} 2>&1 | tee {log}'"
).format(wd=WORKDIR, cmd=base_cmd, log=log_no)

cmd_yes = (
    "bash -lc 'cd {wd}; source venv/bin/activate; export PYTHONUNBUFFERED=1; export CUDA_VISIBLE_DEVICES=0; "
    "timeout 3600 {cmd} --validate_gold_offsets 2>&1 | tee {log}'"
).format(wd=WORKDIR, cmd=base_cmd, log=log_yes)


def stream_and_wait(client, command, label):
    print(f"\n===== {label} =====")
    _, so, se = client.exec_command(command, get_pty=True)
    while True:
        line = so.readline()
        if not line:
            break
        # Keep output concise but still visible
        if (
            "[LANG" in line
            or "Dataset name:" in line
            or "Average recall:" in line
            or "Traceback" in line
            or "Recall:" in line
        ):
            print(line, end="")
    err = se.read().decode('utf-8', errors='replace')
    if err.strip():
        print("[STDERR]")
        print(err)
    return so.channel.recv_exit_status()


def fetch_avg_recall(client, log_path):
    cmd = (
        "bash -lc 'grep -E "
        + '"Average recall:|Dataset name:|Recall:" '
        + log_path
        + " || true'"
    )
    _, so, _ = client.exec_command(cmd)
    txt = so.read().decode('utf-8', errors='replace')
    m = re.findall(r"Average recall:\s*([0-9.]+)", txt)
    avg = float(m[-1]) if m else None
    return avg, txt


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)

print(f"LOG_NO={log_no}")
print(f"LOG_YES={log_yes}")

rc_no = stream_and_wait(client, cmd_no, "RUN A (no offset validation)")
rc_yes = stream_and_wait(client, cmd_yes, "RUN B (with offset validation)")

avg_no, key_no = fetch_avg_recall(client, log_no)
avg_yes, key_yes = fetch_avg_recall(client, log_yes)

print("\n===== A/B SUMMARY =====")
print(f"RC_NO={rc_no} RC_YES={rc_yes}")
print(f"AVG_NO={avg_no}")
print(f"AVG_YES={avg_yes}")
if avg_no is not None and avg_yes is not None:
    print(f"DELTA={avg_yes-avg_no:.6f}")

print("\n--- KEY LINES (NO VALIDATION) ---")
print(key_no)
print("\n--- KEY LINES (WITH VALIDATION) ---")
print(key_yes)

client.close()
