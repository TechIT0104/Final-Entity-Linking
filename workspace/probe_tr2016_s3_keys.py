import requests
import urllib3

urllib3.disable_warnings()

base = "https://s3.amazonaws.com/refined.public/"
candidates = [
    "2022_oct/datasets/tr2016.tar.gz",
    "2022_oct/datasets/tr2016.tgz",
    "2022_oct/datasets/tr2016.zip",
    "2022_oct/datasets/TR2016.tar.gz",
    "2022_oct/datasets/TR2016.zip",
    "2022_oct/datasets/TR2016.tgz",
    "2022_oct/datasets/tr2016/de/test.tar.gz",
    "2022_oct/datasets/tr2016/de/test/de_test.tar.gz",
    "2022_oct/datasets/tr2016/de/test/de_test.zip",
    "2022_oct/datasets/tr2016/de/test/placeholder.mentions.new",
    "2022_oct/datasets/tr2016/de/test/0.mentions.new",
    "2022_oct/datasets/tr2016/de/test/test.mentions.new",
    "2022_oct/datasets/tr2016/de/test/test.txt",
    "2022_oct/datasets/tr2016/de/test/de.mentions.new",
    "2022_oct/datasets/tr2016/de/test/de.txt",
    "2022_oct/tr2016.tar.gz",
    "2022_oct/tr2016.zip",
    "datasets/tr2016.tar.gz",
    "datasets/tr2016.zip",
    "tr2016.tar.gz",
    "tr2016.zip",
]

for key in candidates:
    url = base + key
    try:
        r = requests.head(url, timeout=20, verify=False, allow_redirects=True)
        status = r.status_code
        length = r.headers.get("Content-Length", "")
        print(f"{status:3} {length:>10} {key}")
    except Exception as ex:
        print(f"ERR {'':>10} {key} :: {ex}")
