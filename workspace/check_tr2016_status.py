import sys
import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PASSWORD = "kmpooja123"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python check_tr2016_status.py <pid> [log_path]")
        sys.exit(1)

    pid = sys.argv[1]
    log_path = sys.argv[2] if len(sys.argv) > 2 else ""

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=30)

    cmd_running = f"ps -p {pid} -o pid=,etime=,cmd= || true"
    _, stdout, stderr = client.exec_command(cmd_running)
    running = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()

    print("Process status:")
    if running:
        print(running)
    else:
        print(f"PID {pid} is not running")

    if err:
        print("stderr:")
        print(err)

    if log_path:
        cmd_tail = f"tail -n 40 {log_path} || true"
        _, stdout2, stderr2 = client.exec_command(cmd_tail)
        tail_text = stdout2.read().decode("utf-8", errors="replace")
        tail_err = stderr2.read().decode("utf-8", errors="replace").strip()

        print("\nLast log lines:")
        print(tail_text.strip())
        if tail_err:
            print("stderr:")
            print(tail_err)

    client.close()


if __name__ == "__main__":
    main()
