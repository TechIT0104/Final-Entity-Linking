import datetime
import json
import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PASSWORD = "kmpooja123"
WORKDIR = "/DATA/kmpooja/mrefined_option1"


def main() -> None:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"{WORKDIR}/logs/tr2016_full_{timestamp}.log"

    command = f"""
cd {WORKDIR}
source venv/bin/activate
export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES=0
nohup python3 -u ReFinED/src/refined/evaluation/multilingual_e2e_evaluation_tr2016.py \\
  --lang_title2wikidata "assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data" \\
  --mention2wikidata "assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data" \\
  --model "assets/finetune_models/mReFinED_Recall_9343" \\
  --data "assets/data_combine_11_languages_wikidata_all_eng_label_desc" \\
    --datasets_root "assets/tr2016" \\
  > "{log_path}" 2>&1 < /dev/null &
echo "PID:$!"
echo "LOG:{log_path}"
"""

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    _, stdout, stderr = client.exec_command(command)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    client.close()

    if err.strip():
        print("stderr:")
        print(err.strip())

    pid = None
    started_log = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("PID:"):
            pid = line.replace("PID:", "", 1).strip()
        elif line.startswith("LOG:"):
            started_log = line.replace("LOG:", "", 1).strip()

    payload = {
        "host": HOST,
        "workdir": WORKDIR,
        "pid": pid,
        "log": started_log,
        "raw_output": out.strip(),
    }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
