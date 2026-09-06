import re
import requests
from pypdf import PdfReader
from io import BytesIO
import sys


def extract(pdf_url: str) -> None:
    r = requests.get(pdf_url, timeout=60)
    r.raise_for_status()
    reader = PdfReader(BytesIO(r.content))
    text = "\n".join((p.extract_text() or "") for p in reader.pages)

    print("PDF:", pdf_url)
    print("contains TR2016:", "tr2016" in text.lower())
    print("contains hard:", "hard" in text.lower())

    urls = sorted(set(re.findall(r"https?://[^\s)\]>\"']+", text)))
    print("URLs:")
    for u in urls:
        print("-", u)

    for kw in ["dataset", "github", "download", "wikifier", "wiki", "candidate", "code"]:
        print(kw, kw in text.lower())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_links_from_paper_pdf.py <pdf_url>")
        raise SystemExit(1)
    extract(sys.argv[1])
