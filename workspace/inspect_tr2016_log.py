import re
import sys
import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PASSWORD = "kmpooja123"

KEYWORDS = (
    "[LANG",
    "Dataset name:",
    "Recall:",
    "Average recall",
    "Traceback",
    "KeyError",
)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python inspect_tr2016_log.py <remote_log_path>")
        sys.exit(1)

    log_path = sys.argv[1]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=30)

    sftp = client.open_sftp()
    try:
        with sftp.open(log_path, "r") as f:
            content = f.read().decode("utf-8", errors="replace")
    finally:
        sftp.close()
        client.close()

    lines = content.splitlines()
    print("Relevant lines:")
    for line in lines:
        if any(key in line for key in KEYWORDS):
            print(line)

    per_lang = {}
    for line in lines:
        m = re.search(r"\[LANG\s+([a-z]+)\]\s+done:\s+recall=([0-9.]+)", line)
        if m:
            per_lang[m.group(1)] = float(m.group(2))

    m_avg = re.search(r"Average recall:([0-9.]+)", content)
    if m_avg:
        avg = float(m_avg.group(1))
        print(f"\nParsed average recall: {avg:.4f} ({avg * 100:.2f}%)")

    if per_lang:
        print("Parsed per-language done recalls:")
        for lang in ["de", "es", "fr", "it"]:
            if lang in per_lang:
                val = per_lang[lang]
                print(f"  {lang}: {val:.4f} ({val * 100:.2f}%)")


if __name__ == "__main__":
    main()
