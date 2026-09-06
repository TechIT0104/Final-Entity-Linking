import requests

CANDIDATES = [
    ("amazon-science", "ReFinED", ["main", "master", "mrefined"]),
    ("facebookresearch", "GENRE", ["main", "master"]),
    ("facebookresearch", "mgenre", ["main", "master"]),
    ("facebookresearch", "BLINK", ["main", "master"]),
]


def get_json(url):
    r = requests.get(url, timeout=60, headers={"Accept": "application/vnd.github+json", "User-Agent": "python"})
    return r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else {}


for owner, repo, branches in CANDIDATES:
    print(f"\n=== {owner}/{repo} ===")
    found_any = False
    for br in branches:
        code, branch_info = get_json(f"https://api.github.com/repos/{owner}/{repo}/branches/{br}")
        if code != 200:
            continue

        found_any = True
        sha = branch_info["commit"]["sha"]
        print(f"branch {br} sha {sha[:12]}")

        code2, tree_info = get_json(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{sha}?recursive=1")
        if code2 != 200:
            print(f"  tree fetch failed: {code2}")
            continue

        paths = [x.get("path", "") for x in tree_info.get("tree", [])]
        hits = [
            p for p in paths
            if any(k in p.lower() for k in ["tr2016", "tr_2016", "mewsli", "multilingual_e2e_evaluation_tr2016", "mentions.new"])
        ]

        print(f"  total paths: {len(paths)} | hits: {len(hits)}")
        for h in hits[:120]:
            print("   ", h)

    if not found_any:
        print("  no candidate branch found")
