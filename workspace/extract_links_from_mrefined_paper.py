import re
import requests
from pypdf import PdfReader
from io import BytesIO

PDF_URL = "https://aclanthology.org/2023.findings-emnlp.1007.pdf"


def main() -> None:
    r = requests.get(PDF_URL, timeout=60)
    r.raise_for_status()

    reader = PdfReader(BytesIO(r.content))
    text_parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        text_parts.append(text)
    text = "\n".join(text_parts)

    print("=== Contains keyword checks ===")
    for kw in ["TR2016", "TR 2016", "Mewsli", "MEWSLI", "github", "dataset", "download"]:
        print(f"{kw}: {kw.lower() in text.lower()}")

    print("\n=== Snippets around TR2016 ===")
    for m in re.finditer(r"tr\s*2016", text, flags=re.IGNORECASE):
        start = max(0, m.start() - 220)
        end = min(len(text), m.end() + 220)
        print(text[start:end].replace("\n", " "))
        print("---")

    print("\n=== URLs found ===")
    urls = sorted(set(re.findall(r"https?://[^\s)\]>\"']+", text)))
    for u in urls:
        print(u)


if __name__ == "__main__":
    main()
