import json
import paramiko

SERVERS = [
    ("172.20.70.80", "kmpooja", "kmpooja123"),
    ("172.20.70.170", "kmpooja", "kmpooja123"),
]

SEARCH_COMMANDS = [
    "find /DATA /home -maxdepth 6 -type d -iname '*tr2016*' 2>/dev/null | head -n 120",
    "find /DATA /home -maxdepth 8 -type f \( -name '*.mentions.new' -o -name '*.mentions' \) 2>/dev/null | grep -Ei 'tr2016|tr_2016' | head -n 120",
]


def run_cmd(client, cmd):
    _, stdout, stderr = client.exec_command(cmd)
    return (
        stdout.read().decode("utf-8", errors="replace"),
        stderr.read().decode("utf-8", errors="replace"),
    )


def main() -> None:
    report = {}

    for host, user, password in SERVERS:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        item = {"dirs": [], "mention_files": [], "errors": []}
        try:
            client.connect(host, username=user, password=password, timeout=30)

            out1, err1 = run_cmd(client, SEARCH_COMMANDS[0])
            out2, err2 = run_cmd(client, SEARCH_COMMANDS[1])

            item["dirs"] = [x.strip() for x in out1.splitlines() if x.strip()]
            item["mention_files"] = [x.strip() for x in out2.splitlines() if x.strip()]
            if err1.strip():
                item["errors"].append(err1.strip())
            if err2.strip():
                item["errors"].append(err2.strip())

            # For each candidate dir, list small sample
            samples = {}
            for d in item["dirs"][:20]:
                cmd = f"find '{d}' -maxdepth 3 -type f | head -n 20"
                out, _ = run_cmd(client, cmd)
                samples[d] = [x.strip() for x in out.splitlines() if x.strip()]
            item["dir_samples"] = samples

        except Exception as ex:
            item["errors"].append(str(ex))
        finally:
            try:
                client.close()
            except Exception:
                pass

        report[host] = item

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
