import json
import paramiko

SERVERS = [
    ("172.20.70.80", "kmpooja", "kmpooja123"),
    ("172.20.70.170", "kmpooja", "kmpooja123"),
]

PATTERNS = [
    "find /DATA /home -maxdepth 8 -type f 2>/dev/null | grep -Ei 'tr2016|tr_2016' | grep -Ei '\\.(zip|tar|tar\\.gz|tgz|bz2|xz)$' | head -n 80",
    "find /DATA /home -maxdepth 8 -type f 2>/dev/null | grep -Ei 'placeholder\\.(mentions\\.new|txt)$' | head -n 40",
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
        data = {"archives": [], "placeholders": [], "errors": []}
        try:
            client.connect(host, username=user, password=password, timeout=30)
            out1, err1 = run_cmd(client, PATTERNS[0])
            out2, err2 = run_cmd(client, PATTERNS[1])
            data["archives"] = [x.strip() for x in out1.splitlines() if x.strip()]
            data["placeholders"] = [x.strip() for x in out2.splitlines() if x.strip()]
            if err1.strip():
                data["errors"].append(err1.strip())
            if err2.strip():
                data["errors"].append(err2.strip())
        except Exception as ex:
            data["errors"].append(str(ex))
        finally:
            try:
                client.close()
            except Exception:
                pass
        report[host] = data

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
