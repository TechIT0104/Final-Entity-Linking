import re
import requests
from bs4 import BeautifulSoup

queries = [
    "TR2016hard dataset download",
    "Tsai Roth 2016 entity linking dataset",
    "mGENRE TR2016 hard",
    "mReFinED TR2016 data",
    "de es fr it tr2016 entity linking",
]

for q in queries:
    print("\n=== QUERY:", q, "===")
    url = "https://duckduckgo.com/html/"
    resp = requests.get(url, params={"q": q}, timeout=30)
    print("status:", resp.status_code)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for a in soup.select("a.result__a")[:10]:
        href = a.get("href")
        text = a.get_text(" ", strip=True)
        links.append((text, href))
    if not links:
        # fallback generic anchors
        for a in soup.find_all("a", href=True)[:30]:
            h = a["href"]
            t = a.get_text(" ", strip=True)
            if h.startswith("http"):
                links.append((t, h))
    for t, h in links[:10]:
        print("-", t)
        print(" ", h)
