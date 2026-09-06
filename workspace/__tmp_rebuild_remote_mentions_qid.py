import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PW = "kmpooja123"
WORKDIR = "/DATA/kmpooja/mrefined_option1"
REMOTE_SCRIPT = WORKDIR + "/__tmp_rebuild_mentions_qid.py"

remote_py = r'''
import os
import glob
import pickle
import re

WORKDIR = "/DATA/kmpooja/mrefined_option1"
BASE = WORKDIR + "/assets/tr2016"
ADDITIONAL = WORKDIR + "/assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data"

with open(os.path.join(ADDITIONAL, "lang_title2wikidataID-normalized_with_redirect.pkl"), "rb") as f:
    title_map = pickle.load(f)


def norm(x):
    x = (x or "").strip().replace("_", " ")
    x = re.sub(r"\s+", " ", x)
    return x.lower()


langs = ["de", "es", "fr", "it"]
for lang in langs:
    files = glob.glob(f"{BASE}/{lang}/test/*.mentions.new")
    rows_total = 0
    rows_nonzero = 0
    rows_kept = 0
    files_done = 0

    for fp in files:
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        parsed_rows = []
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 5:
                continue

            # Headered format
            if parts[0] == "start" and "non_en_title" in parts:
                continue

            try:
                start = int(parts[0])
                end = int(parts[1])
            except Exception:
                continue

            # Support both current raw-like format and any pre-header format.
            # Expected most often: start, end, is_hard, non_en_title, q_id
            is_hard = parts[2] if len(parts) > 2 else "0"
            non_en_title = parts[3] if len(parts) > 3 else ""

            # If a file already had header style order start,end,non_en_title,q_id,is_hard
            if parts[2] not in ("0", "1"):
                non_en_title = parts[2]
                is_hard = parts[4] if len(parts) > 4 else "0"

            key = norm(non_en_title)
            mapped_qid = title_map.get((lang, key), 0)

            rows_total += 1
            if mapped_qid and str(mapped_qid) not in ("0", "Q0"):
                rows_nonzero += 1
            rows_kept += 1

            parsed_rows.append((start, end, non_en_title, mapped_qid if mapped_qid else 0, is_hard))

        tmp = fp + ".tmp"
        with open(tmp, "w", encoding="utf-8") as out:
            out.write("start\tend\tnon_en_title\tq_id\tis_hard\n")
            for start, end, title, qid, is_hard in parsed_rows:
                out.write(f"{start}\t{end}\t{title}\t{qid}\t{is_hard}\n")

        os.replace(tmp, fp)
        files_done += 1

    rate = (rows_nonzero / rows_total) if rows_total else 0.0
    print(lang, "files", files_done, "rows", rows_total, "nonzero_qid", rows_nonzero, "nonzero_rate", round(rate, 4))
'''

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)

sftp = client.open_sftp()
with sftp.open(REMOTE_SCRIPT, "w") as f:
    f.write(remote_py)
sftp.close()

cmd = (
    "bash -lc 'cd " + WORKDIR
    + "; source venv/bin/activate"
    + "; python3 " + REMOTE_SCRIPT
    + "; rc=$?"
    + "; rm -f " + REMOTE_SCRIPT
    + "; echo __RC__:$rc'"
)

_, so, se = client.exec_command(cmd, get_pty=True)
out = so.read().decode("utf-8", errors="replace")
err = se.read().decode("utf-8", errors="replace")
print(out)
if err.strip():
    print("[STDERR]")
    print(err)

client.close()
