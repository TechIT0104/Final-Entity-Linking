import re
import requests
from urllib.parse import quote_plus

HEADERS = {"User-Agent": "Mozilla/5.0"}


def bing(query):
    url = "https://www.bing.com/search?q=" + quote_plus(query)
    print("\n[BING]", query)
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        print(" status", r.status_code, "len", len(r.text))
        if r.status_code != 200:
            return []
        # Bing typically wraps results in <li class="b_algo"> with <a href="...">
        links = re.findall(r'<li class="b_algo".*?<a href="(https?://[^"]+)"', r.text, flags=re.S)
        if not links:
            links = re.findall(r'<a href="(https?://[^"]+)" h=', r.text)
        seen = []
        for l in links:
            if l not in seen:
                seen.append(l)
        for l in seen[:15]:
            print(" ", l)
        return seen
    except Exception as ex:
        print(" ERR", ex)
        return []


def github_search(query):
    url = "https://github.com/search?q=" + quote_plus(query) + "&type=code"
    print("\n[GITHUB SEARCH]", query)
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        print(" status", r.status_code, "len", len(r.text))
        if r.status_code != 200:
            return
        # extract any /owner/repo/blob/... links
        rel = re.findall(r'href="(/[^/]+/[^/]+/blob/[^"]+)"', r.text)
        seen = []
        for x in rel:
            full = "https://github.com" + x
            if full not in seen:
                seen.append(full)
        for s in seen[:20]:
            print(" ", s)
    except Exception as ex:
        print(" ERR", ex)


if __name__ == "__main__":
    bing("TR2016hard dataset")
    bing("\".mentions.new\" tr2016")
    bing("\"Tsai\" \"Roth\" \"entity linking\" dataset")
    bing("\"TAC KBP 2016\" \"entity linking\" \"LDC\"")
    github_search("tr2016hard")
    github_search(".mentions.new tr2016")
    github_search("preprocess_TR2016")
