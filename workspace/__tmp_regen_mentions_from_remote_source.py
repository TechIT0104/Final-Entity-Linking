import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PW = "kmpooja123"
WORKDIR = "/DATA/kmpooja/mrefined_option1"
REMOTE_SCRIPT = WORKDIR + "/__tmp_regen_mentions_from_source.py"

remote_py = r'''
import os
import glob
import pickle
import re

WORKDIR = '/DATA/kmpooja/mrefined_option1'
SRC_BASE = WORKDIR + '/assets/tr2016_source/xlwikifier-wikidata/data'
DST_BASE = WORKDIR + '/assets/tr2016'
ADD = WORKDIR + '/assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data'

with open(os.path.join(ADD, 'lang_title2wikidataID-normalized_with_redirect.pkl'), 'rb') as f:
    title_map = pickle.load(f)


def norm(x):
    x = (x or '').strip().replace('_', ' ')
    x = re.sub(r'\s+', ' ', x)
    return x.lower()


def pick_qid(v):
    if v is None:
        return 0
    if isinstance(v, str):
        return v
    if isinstance(v, (set, list, tuple)):
        if not v:
            return 0
        return sorted([str(x) for x in v])[0]
    return str(v)


for lang in ['de', 'es', 'fr', 'it']:
    src_mentions = glob.glob(f'{SRC_BASE}/{lang}/test/*.mentions')
    written = 0
    rows = 0
    nonzero = 0
    skipped_no_doc = 0

    for sm in src_mentions:
        base = os.path.basename(sm)[:-9]  # drop .mentions
        dst_txt = f'{DST_BASE}/{lang}/test/{base}.txt'
        dst_mentions_new = f'{DST_BASE}/{lang}/test/{base}.mentions.new'

        if not os.path.exists(dst_txt):
            skipped_no_doc += 1
            continue

        with open(sm, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        out_rows = []
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) < 5:
                continue
            try:
                start = int(parts[0])
                end = int(parts[1])
            except Exception:
                continue

            non_en_title = parts[3]
            is_hard = parts[4]

            qv = title_map.get((lang, norm(non_en_title)))
            qid = pick_qid(qv)
            if qid not in (0, '0', 'Q0', ''):
                nonzero += 1
            rows += 1
            out_rows.append((start, end, non_en_title, qid if qid else 0, is_hard))

        with open(dst_mentions_new, 'w', encoding='utf-8') as out:
            out.write('start\tend\tnon_en_title\tq_id\tis_hard\n')
            for s, e, t, q, h in out_rows:
                out.write(f'{s}\t{e}\t{t}\t{q}\t{h}\n')

        written += 1

    rate = (nonzero / rows) if rows else 0.0
    print(lang, 'files_written', written, 'rows', rows, 'nonzero_qid', nonzero, 'nonzero_rate', round(rate, 4), 'skipped_no_doc', skipped_no_doc)

# Post-check: ensure no filename mismatch remains
for lang in ['de', 'es', 'fr', 'it']:
    txt = {os.path.basename(p)[:-4] for p in glob.glob(f'{DST_BASE}/{lang}/test/*.txt')}
    men = {os.path.basename(p)[:-13] for p in glob.glob(f'{DST_BASE}/{lang}/test/*.mentions.new')}
    print('check', lang, 'txt', len(txt), 'mentions.new', len(men), 'missing_doc', len(men - txt), 'missing_mentions', len(txt - men))
'''

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)

sftp = client.open_sftp()
with sftp.open(REMOTE_SCRIPT, 'w') as f:
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
out = so.read().decode('utf-8', errors='replace')
err = se.read().decode('utf-8', errors='replace')
print(out)
if err.strip():
    print('[STDERR]')
    print(err)

client.close()
