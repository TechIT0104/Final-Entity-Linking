import json
import posixpath
import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PASSWORD = "kmpooja123"
BASE = "/DATA/kmpooja/mrefined_option1/assets/tr2016"
LANGS = ["de", "es", "fr", "it"]


def list_files(sftp, path):
    try:
        return sorted(sftp.listdir(path))
    except Exception:
        return []


def main() -> None:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    sftp = client.open_sftp()

    report = {}
    for lang in LANGS:
        lang_root = posixpath.join(BASE, lang)
        test_root = posixpath.join(lang_root, "test")

        lang_entries = list_files(sftp, lang_root)
        test_entries = list_files(sftp, test_root)

        txt = [f for f in test_entries if f.endswith(".txt")]
        mentions_new = [f for f in test_entries if f.endswith(".mentions.new")]
        mentions = [f for f in test_entries if f.endswith(".mentions")]
        tsv = [f for f in test_entries if f.endswith(".tsv")]

        sample_mention = None
        for candidate in mentions_new + mentions + tsv:
            sample_mention = candidate
            break

        sample_header = ""
        if sample_mention:
            sample_path = posixpath.join(test_root, sample_mention)
            try:
                with sftp.open(sample_path, "r") as f:
                    text = f.read(4096).decode("utf-8", errors="replace")
                    sample_header = text.splitlines()[0] if text.splitlines() else ""
            except Exception as ex:
                sample_header = f"<read-error: {ex}>"

        report[lang] = {
            "lang_root": lang_root,
            "test_root": test_root,
            "lang_entries_count": len(lang_entries),
            "test_entries_count": len(test_entries),
            "txt_count": len(txt),
            "mentions_new_count": len(mentions_new),
            "mentions_count": len(mentions),
            "tsv_count": len(tsv),
            "sample_test_entries": test_entries[:8],
            "sample_mention_file": sample_mention,
            "sample_mention_header": sample_header,
        }

    sftp.close()
    client.close()

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
