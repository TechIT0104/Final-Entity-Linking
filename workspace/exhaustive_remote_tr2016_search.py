import paramiko

SERVERS = [
    ("172.20.70.80", "kmpooja", "kmpooja123"),
    ("172.20.70.170", "kmpooja", "kmpooja123"),
]

CMD_MENTION = "find /DATA /home -type f -name '*.mentions.new' 2>/dev/null | grep -Ei 'tr2016|tr_2016|TR2016' | head -n 300"
CMD_TAR = "find /DATA /home -type f 2>/dev/null | grep -Ei 'tr2016|tr_2016|TR2016' | grep -Ei '\\.(zip|tar|tar.gz|tgz|bz2|xz)$' | head -n 200"

for host, user, pwd in SERVERS:
    print(f"\n=== {host} ===")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, username=user, password=pwd, timeout=40)

    for name, cmd in [("mentions", CMD_MENTION), ("archives", CMD_TAR)]:
        print(f"-- {name} --")
        _, so, se = c.exec_command(cmd)
        out = so.read().decode("utf-8", errors="replace").strip()
        err = se.read().decode("utf-8", errors="replace").strip()
        print(out if out else "<none>")
        if err:
            print("ERR:", err)

    c.close()
