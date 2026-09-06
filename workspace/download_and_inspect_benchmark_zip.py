import os
import zipfile
import gdown

FILE_ID = "1IDjXFnNnHf__MO5j_onw4YwR97oS8lAy"
OUT_PATH = "train_and_benchmark_data.zip"


def main() -> None:
    url = f"https://drive.google.com/uc?id={FILE_ID}"

    if not os.path.exists(OUT_PATH):
        print("Downloading archive...")
        gdown.download(url, OUT_PATH, quiet=False, fuzzy=True)
    else:
        print("Archive already exists, skipping download")

    print(f"Archive size: {os.path.getsize(OUT_PATH) / (1024*1024):.2f} MB")

    with zipfile.ZipFile(OUT_PATH, "r") as zf:
        names = zf.namelist()

    print(f"Total entries: {len(names)}")

    # Print likely relevant entries
    keywords = ["tr2016", "TR2016", "mewsli", "wned", "aida", "mentions", "test_datasets"]
    matched = [n for n in names if any(k.lower() in n.lower() for k in keywords)]

    print("\nMatched entries (first 200):")
    for n in matched[:200]:
        print(n)

    print("\nTop-level folders:")
    top = sorted({n.split('/')[0] for n in names if '/' in n})
    for t in top[:100]:
        print(t)


if __name__ == "__main__":
    main()
