import re
import sys
import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PASSWORD = "kmpooja123"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python collect_tr2016_recall.py <remote_log_path>")
        sys.exit(1)

    log_path = sys.argv[1]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=30)

    cmd = f"grep -E '\\[LANG [a-z]+\\] done: recall=|Average recall' {log_path} || true"
    _, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    client.close()

    if err.strip():
        print("stderr:")
        print(err.strip())

    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if not lines:
        print("No recall lines found yet. The run may still be in progress.")
        return

    per_lang = {}
    average = None

    for line in lines:
        m_lang = re.search(r"\[LANG\s+([a-z]+)\] done: recall=([0-9.]+)", line)
        if m_lang:
            per_lang[m_lang.group(1)] = float(m_lang.group(2))
            continue

        m_avg = re.search(r"Average recall:([0-9.]+)", line)
        if m_avg:
            average = float(m_avg.group(1))

    print("TR2016 recall summary:")
    for lang in ["de", "es", "fr", "it"]:
        if lang in per_lang:
            print(f"  {lang}: {per_lang[lang]:.4f} ({per_lang[lang] * 100:.2f}%)")

    if average is not None:
        print(f"  macro_avg: {average:.4f} ({average * 100:.2f}%)")
    elif per_lang:
        macro = sum(per_lang.values()) / len(per_lang)
        print(f"  macro_avg_from_seen_langs: {macro:.4f} ({macro * 100:.2f}%)")


if __name__ == "__main__":
    main()
