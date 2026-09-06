import requests
from urllib.parse import quote_plus

HEADERS = {"User-Agent": "Mozilla/5.0"}

q = "TR2016hard dataset"
url = "https://www.bing.com/search?q=" + quote_plus(q)
r = requests.get(url, headers=HEADERS, timeout=30)
print("bing", r.status_code, len(r.text))
with open("__bing.html", "w", encoding="utf-8") as f:
    f.write(r.text)

q2 = "tr2016hard"
url2 = "https://github.com/search?q=" + quote_plus(q2) + "&type=code"
r2 = requests.get(url2, headers=HEADERS, timeout=30)
print("gh", r2.status_code, len(r2.text))
with open("__gh_search.html", "w", encoding="utf-8") as f:
    f.write(r2.text)
