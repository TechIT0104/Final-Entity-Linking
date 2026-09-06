import re
import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}


def ddg(query: str):
    print(f"\n[DDG] {query}")
    try:
        r = requests.get("https://duckduckgo.com/html/", params={"q": query}, timeout=25, headers=HEADERS)
        print("status", r.status_code, "len", len(r.text))
        if r.status_code != 200:
            return
        links = re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"', r.text)
        for link in links[:15]:
            print(" ", link)
    except Exception as ex:
        print("ERR", ex)


def acl_and_pdf():
    print("\n[ACL PAGE]")
    u = "https://aclanthology.org/N16-1075/"
    r = requests.get(u, timeout=30, headers=HEADERS)
    print("status", r.status_code, "len", len(r.text))
    if r.status_code == 200:
        links = sorted(set(re.findall(r'href="(https?://[^"]+)"', r.text)))
        for l in links:
            if any(k in l.lower() for k in ["data", "dataset", "github", "cogcomp", "tac", "ldc", "wiki"]):
                print(" ", l)

    print("\n[ACL PDF]")
    pdf = "https://aclanthology.org/N16-1075.pdf"
    pr = requests.get(pdf, timeout=30, headers=HEADERS)
    print("status", pr.status_code, "bytes", len(pr.content))
    if pr.status_code != 200:
        return
    with open("__N16_1075.pdf", "wb") as f:
        f.write(pr.content)

    try:
        import pypdf

        reader = pypdf.PdfReader("__N16_1075.pdf")
        txt = "\n".join((p.extract_text() or "") for p in reader.pages)
        urls = sorted(set(re.findall(r'https?://[^\s)\]}>"\']+', txt)))
        print("urls_in_pdf", len(urls))
        for x in urls:
            if any(k in x.lower() for k in ["data", "dataset", "cogcomp", "tac", "ldc", "wiki", "github"]):
                print(" ", x)
    except Exception as ex:
        print("PDF_PARSE_ERR", ex)


def ldc_search():
    print("\n[LDC SEARCH]")
    urls = [
        "https://catalog.ldc.upenn.edu/?q=TAC+KBP+2016+entity+linking",
        "https://catalog.ldc.upenn.edu/?q=TAC+KBP+entity+linking",
        "https://catalog.ldc.upenn.edu/?q=TR2016hard",
        "https://catalog.ldc.upenn.edu/?q=Tsai+Roth+2016",
    ]
    for su in urls:
        try:
            rr = requests.get(su, timeout=40, headers=HEADERS)
            print("\nURL", su)
            print(" status", rr.status_code, "len", len(rr.text))
            if rr.status_code != 200:
                continue
            ids = sorted(set(re.findall(r"LDC\d{4}[ST]\d+", rr.text)))
            print(" ids", ids[:40])
            anchors = re.findall(r'href="(/LDC\d{4}[ST]\d+)"', rr.text)
            for a in sorted(set(anchors))[:40]:
                print("  https://catalog.ldc.upenn.edu" + a)
        except Exception as ex:
            print(" ERR", ex)


if __name__ == "__main__":
    ddg("TR2016hard Tsai Roth 2016 dataset download")
    ddg("TAC KBP 2016 entity linking data LDC")
    ddg("mGENRE preprocess_TR2016 dataset")
    acl_and_pdf()
    ldc_search()
