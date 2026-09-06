import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PW = "kmpooja123"
WORKDIR = "/DATA/kmpooja/mrefined_option1"
REMOTE_SCRIPT = WORKDIR + "/__tmp_regen_mentions_qid_exact_lookup.py"

remote_py = r'''
import os
import glob
import pickle

WORKDIR = '/DATA/kmpooja/mrefined_option1'
SRC_BASE = WORKDIR + '/assets/tr2016_source/xlwikifier-wikidata/data'
DST_BASE = WORKDIR + '/assets/tr2016'
MAP_PATH = WORKDIR + '/assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data/lang_title2wikidataID-normalized_with_redirect.pkl'

with open(MAP_PATH, 'rb') as f:
    m = pickle.load(f)


def variants(t):
    t = (t or '').strip()
    if not t:
        return []
    out = []
    for v in [t, t.replace('_', ' '), t.replace(' ', '_')]:
        v = v.strip()
        if v and v not in out:
            out.append(v)
    return out


def pick_qid(val):
    if val is None:
        return 0
    if isinstance(val, str):
        return val
    if isinstance(val, (set, list, tuple)):
        if not val:
            return 0
        return sorted([str(x) for x in val])[0]
    return str(val)


for lang in ['de', 'es', 'fr', 'it']:
    src_mentions = glob.glob(f'{SRC_BASE}/{lang}/test/*.mentions')
    files_written = 0
    rows = 0
    mapped = 0
    mapped_non_en = 0
    mapped_en = 0
    skipped_no_doc = 0

    for sm in src_mentions:
        base = os.path.basename(sm)[:-9]
        dst_txt = f'{DST_BASE}/{lang}/test/{base}.txt'
        dst_mentions_new = f'{DST_BASE}/{lang}/test/{base}.mentions.new'

        if not os.path.exists(dst_txt):
            skipped_no_doc += 1
            continue

        out_rows = []
        with open(sm, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                p = line.rstrip('\n').split('\t')
                if len(p) < 5:
                    continue
                try:
                    start = int(p[0])
                    end = int(p[1])
                except Exception:
                    continue

                en_title = p[2]
                non_en_title = p[3]
                is_hard = p[4]

                rows += 1
                val = None

                for t in variants(non_en_title):
                    k = (lang, t)
                    if k in m:
                        val = m[k]
                        mapped_non_en += 1
                        break

                if val is None:
                    for t in variants(en_title):
                        k = ('en', t)
                        if k in m:
                            val = m[k]
                            mapped_en += 1
                            break

                qid = pick_qid(val)
                if qid not in (0, '0', '', 'Q0'):
                    mapped += 1

                out_rows.append((start, end, non_en_title, qid if qid else 0, is_hard))

        with open(dst_mentions_new, 'w', encoding='utf-8') as out:
            out.write('start\tend\tnon_en_title\tq_id\tis_hard\n')
            for s, e, t, q, h in out_rows:
                out.write(f'{s}\t{e}\t{t}\t{q}\t{h}\n')

        files_written += 1

    hit_rate = (mapped / rows) if rows else 0.0
    print(lang, 'files_written', files_written, 'rows', rows, 'mapped', mapped, 'hit_rate', round(hit_rate, 4),
          'mapped_non_en', mapped_non_en, 'mapped_en', mapped_en, 'skipped_no_doc', skipped_no_doc)

# integrity check
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
