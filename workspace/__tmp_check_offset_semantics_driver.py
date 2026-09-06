import paramiko

HOST = "172.20.70.80"
USER = "kmpooja"
PW = "kmpooja123"

REMOTE = r'''bash -lc '
python3 - << "PY"
import glob
import os
import re

root = "/DATA/kmpooja/mrefined_option1/assets/tr2016_source/xlwikifier-wikidata/data"

def norm(x):
    x = (x or "").strip().replace("_", " ")
    x = re.sub(r"\s+", " ", x)
    return x.lower()

for lang in ["de", "es", "fr", "it"]:
    files = glob.glob(os.path.join(root, lang, "test", "*.mentions"))
    total = 0
    exact_char = 0
    exact_byte = 0
    hard_total = 0
    hard_char = 0
    hard_byte = 0

    for mp in files:
        tp = mp[:-len(".mentions")] + ".txt"
        if not os.path.exists(tp):
            continue
        txt = open(tp, "r", encoding="utf-8", errors="ignore").read()
        btxt = txt.encode("utf-8", errors="ignore")

        byte_to_char = {}
        bpos = 0
        for cidx, ch in enumerate(txt):
            enc = ch.encode("utf-8", errors="ignore")
            for _ in range(len(enc)):
                byte_to_char[bpos] = cidx
                bpos += 1
        byte_to_char[bpos] = len(txt)

        with open(mp, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) < 5:
                    continue
                s, e, _, non_en_title, is_hard = p[:5]
                try:
                    s = int(s)
                    e = int(e)
                    h = int(is_hard)
                except Exception:
                    continue

                total += 1
                if h == 1:
                    hard_total += 1

                gold = norm(non_en_title)

                span_char = norm(txt[s:e]) if 0 <= s <= e <= len(txt) else ""
                if span_char == gold:
                    exact_char += 1
                    if h == 1:
                        hard_char += 1

                if 0 <= s <= e <= len(btxt) and s in byte_to_char and e in byte_to_char:
                    cs = byte_to_char[s]
                    ce = byte_to_char[e]
                    span_byte = norm(txt[cs:ce])
                    if span_byte == gold:
                        exact_byte += 1
                        if h == 1:
                            hard_byte += 1

    print(
        lang,
        "total", total,
        "hard", hard_total,
        "char_match", exact_char,
        "char_match_rate", round(exact_char / total, 4) if total else 0,
        "byte_match", exact_byte,
        "byte_match_rate", round(exact_byte / total, 4) if total else 0,
        "hard_char_rate", round(hard_char / hard_total, 4) if hard_total else 0,
        "hard_byte_rate", round(hard_byte / hard_total, 4) if hard_total else 0,
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
