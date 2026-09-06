import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PW = "kmpooja123"

REMOTE = r'''bash -lc '
cd /DATA/kmpooja/mrefined_option1
source venv/bin/activate
python3 - << "PY"
import glob
import os
import pickle

root = "/DATA/kmpooja/mrefined_option1/assets/tr2016_source/xlwikifier-wikidata/data"
map_path = "/DATA/kmpooja/mrefined_option1/assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data/lang_title2wikidataID-normalized_with_redirect.pkl"

with open(map_path, "rb") as f:
    m = pickle.load(f)


def variants(t):
    t = (t or "").strip()
    if not t:
        return []
    out = []
    for v in [t, t.replace("_", " "), t.replace(" ", "_")]:
        v = v.strip()
        if v and v not in out:
            out.append(v)
    return out

for lang in ["de", "es", "fr", "it"]:
    files = glob.glob(os.path.join(root, lang, "test", "*.mentions"))
    tot = hard = 0
    hit = hit_h = 0
    miss = miss_h = 0
    one = one_h = 0
    multi = multi_h = 0

    for fp in files:
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) < 5:
                    continue
                _, _, en_title, non_en_title, is_hard = p[:5]
                try:
                    h = int(is_hard)
                except Exception:
                    h = 0
                tot += 1
                if h == 1:
                    hard += 1

                val = None

                for t in variants(non_en_title):
                    k = (lang, t)
                    if k in m:
                        val = m[k]
                        break

                if val is None:
                    for t in variants(en_title):
                        k = ("en", t)
                        if k in m:
                            val = m[k]
                            break

                if val is None:
                    miss += 1
                    if h == 1:
                        miss_h += 1
                else:
                    hit += 1
                    if h == 1:
                        hit_h += 1
                    n = len(val) if hasattr(val, "__len__") else 1
                    if n <= 1:
                        one += 1
                        if h == 1:
                            one_h += 1
                    else:
                        multi += 1
                        if h == 1:
                            multi_h += 1

    print(
        lang,
        "tot", tot,
        "hard", hard,
        "hit", hit,
        "miss", miss,
        "one", one,
        "multi", multi,
        "hit_h", hit_h,
        "miss_h", miss_h,
        "one_h", one_h,
        "multi_h", multi_h,
    )
PY
' '''

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)
_, so, se = client.exec_command(REMOTE)
out = so.read().decode("utf-8", errors="replace")
err = se.read().decode("utf-8", errors="replace")
print(out)
if err.strip():
    print("ERR:")
    print(err)
client.close()
