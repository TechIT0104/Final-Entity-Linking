import base64
import html
import re
import requests
from urllib.parse import quote_plus, parse_qs, urlparse

HEADERS = {"User-Agent": "Mozilla/5.0"}


def decode_u(uval: str):
    # common bing pattern: a1<base64url>
    s = uval
    if s.startswith("a1"):
        s = s[2:]
    s = s.replace('-', '+').replace('_', '/')
    # pad base64
    s += '=' * (-len(s) % 4)
    try:
        raw = base64.b64decode(s).decode('utf-8', errors='ignore')
        return raw
    except Exception:
        return None


def bing_extract(query: str):
    url = "https://www.bing.com/search?q=" + quote_plus(query)
    r = requests.get(url, headers=HEADERS, timeout=30)
    print("\n[BING]", query)
    print(" status", r.status_code, "len", len(r.text))
    if r.status_code != 200:
        return

    hrefs = re.findall(r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"', r.text, flags=re.S)
    out = []
    for h in hrefs:
        h = html.unescape(h)
        if "bing.com/ck/a" in h:
            qs = parse_qs(urlparse(h).query)
            uv = qs.get('u', [None])[0]
            if uv:
                dec = decode_u(uv)
                out.append((h, dec or ""))
            else:
                out.append((h, ""))
        else:
            out.append((h, h))

    seen = set()
    for _, dec in out:
        if dec and dec not in seen:
            seen.add(dec)
            print(" ", dec)


if __name__ == "__main__":
    bing_extract('"Cross-lingual wikification using multilingual embeddings"')
    bing_extract('"Chen-Tse Tsai" "Dan Roth" 2016 wikification')
    bing_extract('"TR2016hard" dataset')
    bing_extract('"TAC KBP 2016" "entity linking"')
