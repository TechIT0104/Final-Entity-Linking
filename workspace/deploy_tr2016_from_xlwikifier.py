#!/usr/bin/env python3
import json
import os
import sys
import time
from pathlib import Path

import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PASSWORD = "kmpooja123"

REMOTE_WORKDIR = "/DATA/kmpooja/mrefined_option1"
REMOTE_ZIP = f"{REMOTE_WORKDIR}/assets/tr2016_source/xlwikifier-wikidata.zip"
REMOTE_EXTRACT_ROOT = f"{REMOTE_WORKDIR}/assets/tr2016_source"
REMOTE_EXTRACTED_DIR = f"{REMOTE_WORKDIR}/assets/tr2016_source/xlwikifier-wikidata"
REMOTE_DATASET_ROOT = f"{REMOTE_WORKDIR}/assets/tr2016"
REMOTE_MAP_PATH = (
    f"{REMOTE_WORKDIR}/assets/"
    "data_combine_11_languages_wikidata_all_eng_label_desc/"
    "additional_data/lang_title2wikidataID-normalized_with_redirect.pkl"
)

LOCAL_ZIP = Path("__xlwikifier_wikidata.zip")


def run_cmd(client: paramiko.SSHClient, command: str) -> tuple[int, str, str]:
    stdin, stdout, stderr = client.exec_command(command)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    return code, out, err


def ensure_remote_dirs(client: paramiko.SSHClient) -> None:
    cmd = (
        f"mkdir -p {REMOTE_WORKDIR}/assets/tr2016_source "
        f"{REMOTE_WORKDIR}/assets/tr2016/de/test "
        f"{REMOTE_WORKDIR}/assets/tr2016/es/test "
        f"{REMOTE_WORKDIR}/assets/tr2016/fr/test "
        f"{REMOTE_WORKDIR}/assets/tr2016/it/test"
    )
    code, out, err = run_cmd(client, cmd)
    if code != 0:
        raise RuntimeError(f"Failed to create remote directories: {err or out}")


def remote_file_size(client: paramiko.SSHClient, path: str) -> int:
    code, out, _ = run_cmd(client, f"python3 - << 'PY'\nimport os\np='{path}'\nprint(os.path.getsize(p) if os.path.exists(p) else -1)\nPY")
    if code != 0:
        return -1
    try:
        return int(out.strip().splitlines()[-1])
    except Exception:
        return -1


def upload_zip(client: paramiko.SSHClient, local_zip: Path) -> None:
    local_size = local_zip.stat().st_size
    remote_size = remote_file_size(client, REMOTE_ZIP)

    if remote_size == local_size:
        print(f"[INFO] Remote zip already present with matching size ({local_size} bytes).")
        return

    print(
        f"[INFO] Uploading zip to remote: local={local_size} bytes, remote={remote_size} bytes"
    )
    sftp = client.open_sftp()
    try:
        uploaded = {"bytes": 0, "last_mb": -1}

        def cb(transferred: int, total: int) -> None:
            uploaded["bytes"] = transferred
            mb = transferred // (1024 * 1024)
            if mb != uploaded["last_mb"] and mb % 25 == 0:
                uploaded["last_mb"] = mb
                print(f"  uploaded {mb} MB / {total // (1024 * 1024)} MB")

        sftp.put(str(local_zip), REMOTE_ZIP, callback=cb)
    finally:
        sftp.close()

    remote_size_after = remote_file_size(client, REMOTE_ZIP)
    if remote_size_after != local_size:
        raise RuntimeError(
            f"Upload size mismatch: local={local_size}, remote={remote_size_after}"
        )
    print("[INFO] Upload completed and size verified.")


def prepare_remote_data(client: paramiko.SSHClient) -> dict:
    remote_py = f"""
import csv
import glob
import json
import os
import pickle
import shutil
import zipfile

REMOTE_ZIP = {REMOTE_ZIP!r}
REMOTE_EXTRACT_ROOT = {REMOTE_EXTRACT_ROOT!r}
REMOTE_EXTRACTED_DIR = {REMOTE_EXTRACTED_DIR!r}
REMOTE_DATASET_ROOT = {REMOTE_DATASET_ROOT!r}
REMOTE_MAP_PATH = {REMOTE_MAP_PATH!r}
LANGS = ['de', 'es', 'fr', 'it']


def dedup(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def title_variants(title: str):
    t = (title or '').strip()
    if not t:
        return []
    vars_ = [
        t,
        t.replace(' ', '_'),
        t.replace('_', ' '),
        t.replace('–', '-'),
        t.replace('-', '–'),
        t.replace('  ', ' '),
    ]
    return dedup([v.strip() for v in vars_ if v.strip()])


def choose_qid(val):
    if isinstance(val, dict):
        cands = [str(k) for k in val.keys()]
    elif isinstance(val, (set, list, tuple)):
        cands = [str(v) for v in val]
    else:
        cands = [str(val)]

    cands = [c for c in cands if c and c != '0']
    if not cands:
        return '0'

    qids = [c for c in cands if c.startswith('Q') and c[1:].isdigit()]
    if qids:
        qids.sort(key=lambda x: int(x[1:]))
        return qids[0]

    cands.sort()
    return cands[0]


def map_qid(lang_title2wikidata, lang, en_title, non_en_title):
    for tv in title_variants(non_en_title):
        k = (lang, tv)
        if k in lang_title2wikidata:
            return choose_qid(lang_title2wikidata[k])

    for tv in title_variants(en_title):
        k = ('en', tv)
        if k in lang_title2wikidata:
            return choose_qid(lang_title2wikidata[k])

    return '0'


os.makedirs(REMOTE_EXTRACT_ROOT, exist_ok=True)
if not os.path.exists(REMOTE_EXTRACTED_DIR):
    with zipfile.ZipFile(REMOTE_ZIP, 'r') as zf:
        zf.extractall(REMOTE_EXTRACT_ROOT)

with open(REMOTE_MAP_PATH, 'rb') as f:
    lang_title2wikidata = pickle.load(f)

summary = {{
    'zip': REMOTE_ZIP,
    'map_path': REMOTE_MAP_PATH,
    'languages': {{}},
}}

for lang in LANGS:
    src_dir = os.path.join(REMOTE_EXTRACTED_DIR, 'data', lang, 'test')
    dst_dir = os.path.join(REMOTE_DATASET_ROOT, lang, 'test')
    os.makedirs(dst_dir, exist_ok=True)

    for p in glob.glob(os.path.join(dst_dir, '*')):
        if os.path.isfile(p):
            os.remove(p)

    mention_files = sorted(glob.glob(os.path.join(src_dir, '*.mentions')))
    copied_txt = 0
    written_mentions_new = 0
    total_mentions = 0
    resolved_mentions = 0
    hard_mentions = 0
    hard_resolved = 0

    for mention_path in mention_files:
        base = os.path.basename(mention_path)[:-len('.mentions')]
        txt_src = os.path.join(src_dir, base + '.txt')
        if not os.path.exists(txt_src):
            continue

        txt_dst = os.path.join(dst_dir, base + '.txt')
        mentions_new_dst = os.path.join(dst_dir, base + '.mentions.new')

        shutil.copy2(txt_src, txt_dst)
        copied_txt += 1

        with open(mention_path, 'r', encoding='utf-8', errors='ignore') as fin, \
             open(mentions_new_dst, 'w', encoding='utf-8', newline='') as fout:
            writer = csv.writer(fout, delimiter='\t')
            writer.writerow(['start', 'end', 'non_en_title', 'q_id', 'is_hard'])

            for line in fin:
                parts = line.rstrip('\\n').split('\\t')
                if len(parts) < 5:
                    continue

                start, end, en_title, non_en_title, is_hard = parts[:5]

                try:
                    s = int(start)
                    e = int(end)
                    h = int(is_hard)
                except Exception:
                    continue

                qid = map_qid(lang_title2wikidata, lang, en_title, non_en_title)

                total_mentions += 1
                if h == 1:
                    hard_mentions += 1
                if qid != '0':
                    resolved_mentions += 1
                    if h == 1:
                        hard_resolved += 1

                writer.writerow([s, e, non_en_title, qid, h])

        written_mentions_new += 1

    summary['languages'][lang] = {{
        'src_mentions_files': len(mention_files),
        'copied_txt_files': copied_txt,
        'written_mentions_new_files': written_mentions_new,
        'total_mentions': total_mentions,
        'resolved_mentions': resolved_mentions,
        'hard_mentions': hard_mentions,
        'hard_resolved': hard_resolved,
    }}

print(json.dumps(summary))
"""

    command = "python3 - << 'PY'\n" + remote_py + "\nPY"
    code, out, err = run_cmd(client, command)
    if code != 0:
        raise RuntimeError(f"Remote prepare script failed:\nSTDOUT:\n{out}\nSTDERR:\n{err}")

    txt = out.strip()
    if not txt:
        raise RuntimeError("Remote prepare script produced no output")

    lines = txt.splitlines()
    payload_line = lines[-1]
    try:
        return json.loads(payload_line)
    except Exception as ex:
        raise RuntimeError(
            f"Failed to parse remote summary JSON. Last line:\n{payload_line}\nFull output:\n{out}\nError: {ex}"
        )


def verify_remote_layout(client: paramiko.SSHClient) -> str:
    cmd = f"""
for lang in de es fr it; do
  d=\"{REMOTE_DATASET_ROOT}/$lang/test\"
  txt=$(find \"$d\" -maxdepth 1 -type f -name '*.txt' | wc -l)
  men=$(find \"$d\" -maxdepth 1 -type f -name '*.mentions.new' | wc -l)
  echo \"$lang txt=$txt mentions_new=$men\"
done
"""
    code, out, err = run_cmd(client, cmd)
    if code != 0:
        raise RuntimeError(f"Failed to verify remote layout: {err or out}")
    return out


def main() -> int:
    if not LOCAL_ZIP.exists():
        print(f"[ERROR] Missing local zip: {LOCAL_ZIP}")
        return 1

    print("[INFO] Connecting to remote host...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=45)

    try:
        ensure_remote_dirs(client)
        upload_zip(client, LOCAL_ZIP)

        print("[INFO] Preparing extracted TR2016 data and converting .mentions -> .mentions.new ...")
        t0 = time.time()
        summary = prepare_remote_data(client)
        dt = time.time() - t0
        print(f"[INFO] Remote prepare completed in {dt:.1f}s")

        print("[INFO] Conversion summary:")
        print(json.dumps(summary, indent=2))

        print("[INFO] Remote target layout:")
        print(verify_remote_layout(client))

        return 0
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
