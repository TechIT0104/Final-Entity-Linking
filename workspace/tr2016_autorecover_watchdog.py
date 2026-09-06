import argparse
import datetime
import json
import re
import time
from pathlib import Path

import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PASSWORD = "kmpooja123"
WORKDIR = "/DATA/kmpooja/mrefined_option1"
READER_PATH = (
    "/DATA/kmpooja/mrefined_option1/ReFinED/src/refined/"
    "dataset_reading/entity_linking/dataset_reader_multilingual.py"
)
STATE_PATH = Path("tr2016_watchdog_state.json")
EVENT_LOG_PATH = Path("tr2016_watchdog_events.log")
TR2016_DATASET_ROOT = f"{WORKDIR}/assets/tr2016"


def now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_event(message: str) -> None:
    line = f"[{now_str()}] {message}"
    print(line, flush=True)
    EVENT_LOG_PATH.write_text(
        (EVENT_LOG_PATH.read_text(encoding="utf-8") if EVENT_LOG_PATH.exists() else "") + line + "\n",
        encoding="utf-8",
    )


def write_state(payload: dict) -> None:
    payload = dict(payload)
    payload["updated_at"] = now_str()
    STATE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def connect() -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    return client


def exec_cmd(client: paramiko.SSHClient, command: str) -> tuple[str, str]:
    _, stdout, stderr = client.exec_command(command)
    return (
        stdout.read().decode("utf-8", errors="replace"),
        stderr.read().decode("utf-8", errors="replace"),
    )


def check_pid_running(client: paramiko.SSHClient, pid: str) -> tuple[bool, str]:
    out, _ = exec_cmd(client, f"ps -p {pid} -o pid=,etime=,cmd= || true")
    txt = out.strip()
    return (bool(txt), txt)


def read_tail(client: paramiko.SSHClient, log_path: str, n: int = 220) -> str:
    out, _ = exec_cmd(client, f"tail -n {n} {log_path} || true")
    return out


def is_success_log(text: str) -> bool:
    return "Average recall:" in text


def get_dataset_health(client: paramiko.SSHClient) -> dict:
    command = f"""
for lang in de es fr it; do
  d="{TR2016_DATASET_ROOT}/$lang/test"
  if [ ! -d "$d" ]; then
    echo "$lang|MISSING|0|0|0|0"
    continue
  fi
    m_total=$(find "$d" -maxdepth 1 -type f \( -name '*.mentions.new' -o -name '*.mentions' \) | wc -l)
    m_real=$(find "$d" -maxdepth 1 -type f \( -name '*.mentions.new' -o -name '*.mentions' \) ! -name 'placeholder.mentions.new' ! -name 'placeholder.mentions' | wc -l)
  t_total=$(find "$d" -maxdepth 1 -type f -name '*.txt' | wc -l)
  t_real=$(find "$d" -maxdepth 1 -type f -name '*.txt' ! -name 'placeholder.txt' | wc -l)
  echo "$lang|OK|$m_total|$m_real|$t_total|$t_real"
done
"""
    out, _ = exec_cmd(client, command)

    per_lang = {}
    for raw in out.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split("|")
        if len(parts) != 6:
            continue
        lang, status, m_total, m_real, t_total, t_real = parts
        per_lang[lang] = {
            "status": status,
            "mentions_total": int(m_total),
            "mentions_real": int(m_real),
            "txt_total": int(t_total),
            "txt_real": int(t_real),
        }

    required_langs = ("de", "es", "fr", "it")
    has_real_data = all(
        per_lang.get(lang, {}).get("mentions_real", 0) > 0
        and per_lang.get(lang, {}).get("txt_real", 0) > 0
        for lang in required_langs
    )
    missing_or_empty_langs = [
        lang
        for lang in required_langs
        if not (
            per_lang.get(lang, {}).get("mentions_real", 0) > 0
            and per_lang.get(lang, {}).get("txt_real", 0) > 0
        )
    ]
    only_placeholder_or_empty = not has_real_data

    return {
        "dataset_root": TR2016_DATASET_ROOT,
        "per_language": per_lang,
        "has_real_data": has_real_data,
        "missing_or_empty_langs": missing_or_empty_langs,
        "only_placeholder_or_empty": only_placeholder_or_empty,
    }


def has_valid_recall_lines(client: paramiko.SSHClient, log_path: str) -> bool:
    out, _ = exec_cmd(
        client,
        f"grep -E '\\[LANG [a-z]+\\] done: recall=|Recall:|num_gold_spans:[[:space:]]*[1-9][0-9]*' {log_path} || true",
    )
    return bool(out.strip())


def parse_average_recall(text: str) -> float | None:
    match = re.search(r"Average recall:([0-9.]+)", text)
    if not match:
        return None
    return float(match.group(1))


def detect_failure_reason(text: str) -> str | None:
    if "KeyError: 'is_hard'" in text:
        return "missing_is_hard_column"
    if "unrecognized arguments: --device" in text:
        return "unsupported_device_arg"
    if "Traceback" in text:
        return "python_traceback"
    return None


def kill_pid(client: paramiko.SSHClient, pid: str) -> None:
    exec_cmd(client, f"kill -9 {pid} || true")


def patch_remote_reader(client: paramiko.SSHClient) -> bool:
    sftp = client.open_sftp()
    try:
        with sftp.open(READER_PATH, "r") as f:
            original = f.read().decode("utf-8", errors="replace")

        patched = original

        old_mentions_line = "        mention_files = glob(filename+'/*.mentions.new')"
        new_mentions_block = (
            "        mention_files_new = glob(filename+'/*.mentions.new')\n"
            "        mention_files_legacy = glob(filename+'/*.mentions')\n"
            "        mention_files = mention_files_new if mention_files_new else mention_files_legacy"
        )
        if old_mentions_line in patched and "mention_files_legacy" not in patched:
            patched = patched.replace(old_mentions_line, new_mentions_block)

        marker = 'if "is_hard" in mention_label.columns'
        old_line = (
            '            all_titles = mention_label[(mention_label["is_hard"]==1) '
            '& (mention_label["q_id"] != 0)][["start","end","non_en_title","q_id"]].values.tolist()'
        )

        new_block = (
            '            if "q_id" not in mention_label.columns:\n'
            '                continue\n'
            '            qid_numeric = pd.to_numeric(mention_label["q_id"], errors="coerce").fillna(0)\n'
            '            base_filtered = mention_label[qid_numeric != 0]\n'
            '            if "is_hard" in mention_label.columns:\n'
            '                hard_mask = pd.to_numeric(mention_label["is_hard"], errors="coerce").fillna(0) == 1\n'
            '                filtered = base_filtered[hard_mask.loc[base_filtered.index]]\n'
            '            else:\n'
            '                filtered = base_filtered\n'
            '            title_col = "non_en_title" if "non_en_title" in filtered.columns else ("title" if "title" in filtered.columns else None)\n'
            '            if title_col is None:\n'
            '                continue\n'
            '            all_titles = filtered[["start", "end", title_col, "q_id"]].values.tolist()'
        )

        if marker not in patched and old_line in patched:
            patched = patched.replace(old_line, new_block)

        if patched == original:
            log_event("Remote reader already patched (mentions fallback + is_hard handling).")
            return True

        if marker not in patched:
            log_event("Remote patch failed: expected is_hard block not found in dataset reader.")
            return False

        if "mention_files_legacy" not in patched:
            log_event("Remote patch warning: could not apply .mentions fallback (continuing).")

        backup_path = READER_PATH + ".bak_watchdog"
        with sftp.open(backup_path, "w") as f:
            f.write(original)

        with sftp.open(READER_PATH, "w") as f:
            f.write(patched)

        log_event("Applied remote reader patch (is_hard handling + .mentions fallback).")
        return True
    finally:
        sftp.close()


def start_job(client: paramiko.SSHClient) -> tuple[str, str]:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"{WORKDIR}/logs/tr2016_full_{ts}.log"

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
    out, err = exec_cmd(client, command)
    if err.strip():
        log_event(f"Start command stderr: {err.strip()}")

    pid = ""
    log = ""
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("PID:"):
            pid = line.replace("PID:", "", 1).strip()
        elif line.startswith("LOG:"):
            log = line.replace("LOG:", "", 1).strip()

    if not pid or not log:
        raise RuntimeError(f"Failed to parse start output: {out}")

    return pid, log


def main() -> None:
    parser = argparse.ArgumentParser(description="TR2016 self-healing watchdog")
    parser.add_argument("--initial-pid", type=str, default="")
    parser.add_argument("--initial-log", type=str, default="")
    parser.add_argument("--interval-sec", type=int, default=120)
    parser.add_argument("--max-restarts", type=int, default=6)
    args = parser.parse_args()

    restarts = 0
    pid = args.initial_pid
    log_path = args.initial_log

    log_event("Watchdog started.")

    client = connect()
    try:
        dataset_health = get_dataset_health(client)
        if dataset_health["only_placeholder_or_empty"]:
            log_event("TR2016 dataset check failed: only placeholder or empty files were found.")
            write_state(
                {
                    "status": "failed",
                    "reason": "dataset_placeholder_or_missing",
                    "dataset_health": dataset_health,
                    "restarts": restarts,
                }
            )
            return

        if not pid or not log_path:
            pid, log_path = start_job(client)
            log_event(f"Started initial TR2016 job pid={pid} log={log_path}")

        while True:
            running, ps_line = check_pid_running(client, pid)
            tail = read_tail(client, log_path)

            if is_success_log(tail):
                avg_recall = parse_average_recall(tail)
                if not has_valid_recall_lines(client, log_path):
                    dataset_health = get_dataset_health(client)
                    reason = "invalid_completion_no_recall_lines"
                    if dataset_health["only_placeholder_or_empty"]:
                        reason = "dataset_placeholder_or_missing"
                    log_event(
                        f"TR2016 completion rejected ({reason}). pid={pid} log={log_path} avg_recall={avg_recall}"
                    )
                    write_state(
                        {
                            "status": "failed",
                            "reason": reason,
                            "pid": pid,
                            "log": log_path,
                            "restarts": restarts,
                            "avg_recall": avg_recall,
                            "dataset_health": dataset_health,
                        }
                    )
                    break
                log_event(f"TR2016 completed successfully. pid={pid} log={log_path}")
                write_state(
                    {
                        "status": "completed",
                        "pid": pid,
                        "log": log_path,
                        "restarts": restarts,
                        "ps": ps_line,
                    }
                )
                break

            failure = detect_failure_reason(tail)

            if failure:
                if running:
                    kill_pid(client, pid)
                    log_event(f"Killed failed process pid={pid} after detecting {failure}.")

                if failure == "missing_is_hard_column":
                    patched = patch_remote_reader(client)
                    if not patched:
                        write_state(
                            {
                                "status": "failed",
                                "reason": "patch_failed",
                                "pid": pid,
                                "log": log_path,
                                "restarts": restarts,
                            }
                        )
                        break

                if restarts >= args.max_restarts:
                    log_event("Max restarts reached. Stopping watchdog.")
                    write_state(
                        {
                            "status": "failed",
                            "reason": failure,
                            "pid": pid,
                            "log": log_path,
                            "restarts": restarts,
                        }
                    )
                    break

                restarts += 1
                pid, log_path = start_job(client)
                log_event(f"Restarted TR2016 (reason={failure}) pid={pid} log={log_path}")
                write_state(
                    {
                        "status": "running",
                        "pid": pid,
                        "log": log_path,
                        "restarts": restarts,
                        "reason": f"restarted_after_{failure}",
                    }
                )
                time.sleep(args.interval_sec)
                continue

            status = "running" if running else "not_running"
            write_state(
                {
                    "status": status,
                    "pid": pid,
                    "log": log_path,
                    "restarts": restarts,
                    "ps": ps_line,
                }
            )

            if not running:
                if restarts >= args.max_restarts:
                    log_event("Process stopped and max restarts reached.")
                    write_state(
                        {
                            "status": "failed",
                            "reason": "stopped_no_success",
                            "pid": pid,
                            "log": log_path,
                            "restarts": restarts,
                        }
                    )
                    break

                restarts += 1
                pid, log_path = start_job(client)
                log_event(f"Process was not running; restarted pid={pid} log={log_path}")
                write_state(
                    {
                        "status": "running",
                        "pid": pid,
                        "log": log_path,
                        "restarts": restarts,
                        "reason": "restarted_after_stop",
                    }
                )

            time.sleep(args.interval_sec)

    finally:
        client.close()
        log_event("Watchdog exited.")


if __name__ == "__main__":
    main()
