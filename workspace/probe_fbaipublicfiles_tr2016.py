import requests

bases = [
    "http://dl.fbaipublicfiles.com/GENRE/",
    "https://dl.fbaipublicfiles.com/GENRE/",
    "http://dl.fbaipublicfiles.com/mGENRE/",
    "https://dl.fbaipublicfiles.com/mGENRE/",
]

names = []
for lang in ["de", "es", "fr", "it"]:
    names += [
        f"{lang}-kilt-test.jsonl",
        f"{lang}-kilt-test-hard.jsonl",
        f"{lang}-kilt-train.jsonl",
        f"{lang}-kilt-train-hard.jsonl",
        f"TR2016/{lang}-kilt-test.jsonl",
        f"TR2016/{lang}-kilt-test-hard.jsonl",
        f"datasets/TR2016/{lang}-kilt-test-hard.jsonl",
    ]

names += [
    "TR2016hard.tar.gz",
    "TR2016hard.zip",
    "TR2016.tar.gz",
    "tr2016.tar.gz",
    "mewsli-9.tar.gz",
    "mewsli-9-kilt.jsonl",
]

for base in bases:
    print("\n===", base, "===")
    for name in names:
        url = base + name
        try:
            r = requests.get(url, timeout=20, stream=True, allow_redirects=True)
            print(f"{r.status_code:3} {name}")
        except Exception as ex:
            print(f"ERR {name} :: {ex}")
