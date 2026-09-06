import re
import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PASSWORD = "kmpooja123"
LOG_PATH = "/DATA/kmpooja/mrefined_option1/logs/mewsli9_final_20260416_232428.log"


def main() -> None:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=30)

    command = (
        f"grep -E '\\[LANG [a-z]+\\] done: recall=|Average recall|Micro-avg' {LOG_PATH} || true"
    )
    _, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode("utf-8", errors="replace")
    error = stderr.read().decode("utf-8", errors="replace")
    client.close()

    if error.strip():
        print("stderr:")
        print(error.strip())

    lines = [ln.strip() for ln in output.splitlines() if ln.strip()]
    print("Recall lines from log:")
    for line in lines:
        print(line)

    recalls = []
    for line in lines:
        match = re.search(r"\[LANG\s+([a-z]+)\]\s+done:\s+recall=([0-9.]+)", line)
        if match:
            recalls.append((match.group(1), float(match.group(2))))

    if recalls:
        macro = sum(val for _, val in recalls) / len(recalls)
        print("\nParsed per-language recall:")
        for lang, val in recalls:
            print(f"{lang}: {val:.4f}")
        print(f"macro_avg_from_lines: {macro:.4f} ({macro * 100:.2f}%)")


if __name__ == "__main__":
    main()
