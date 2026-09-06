#!/usr/bin/env python3
import csv
import json
import os
import re
import shutil
import sys
import tarfile
import time
import zipfile
from pathlib import Path

import paramiko
import requests

HOST = "172.20.70.80"
USER = "kmpooja"
PASSWORD = "kmpooja123"

REMOTE_WORKDIR = "/DATA/kmpooja/mrefined_option1"
REMOTE_DATASET_ROOT = f"{REMOTE_WORKDIR}/assets/tr2016"
REMOTE_SOURCE_ROOT = f"{REMOTE_WORKDIR}/assets/tr2016_source"
REMOTE_PREPARED_TAR = f"{REMOTE_SOURCE_ROOT}/tr2016_prepared_api.tar.gz"

LOCAL_ZIP = Path("__xlwikifier_wikidata.zip")
LOCAL_PREPARED_ROOT = Path("_tr2016_prepared")
LOCAL_PREPARED_TAR = Path("_tr2016_prepared_api.tar.gz")
LOCAL_CACHE_DIR = Path("_tr2016_cache")

LANGS = ["de", "es", "fr", "it"]
USER_AGENT = "EntityLinkingTR2016/1.0 (local-batch-script)"

INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


def normalize_title(title: str) -> str:
    t = (title or "").strip()
    if not t:
        return ""
    t = t.replace("_", " ").replace("|", " ")
    t = " ".join(t.split())
    return t


def batched(items: list[str], size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def dedup_preserve_order(items: list[str]) -> list[str]:
    out = []
    seen = set()
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def load_json_map(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_json_map(path: Path, payload: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def make_safe_base_name(base: str, used: set[str]) -> str:
    safe = INVALID_FILENAME_CHARS.sub("_", base)
    safe = safe.strip().rstrip(". ")
    if not safe:
        safe = "doc"

    if safe.upper() in WINDOWS_RESERVED_NAMES:
        safe = safe + "_"

    candidate = safe
    i = 1
    while candidate in used:
        i += 1
        candidate = f"{safe}__{i}"

    used.add(candidate)
    return candidate


def resolve_titles_via_wikipedia(
    lang: str,
    titles: list[str],
    session: requests.Session,
    batch_size: int = 50,
) -> dict[str, str]:
    endpoint = f"https://{lang}.wikipedia.org/w/api.php"

    cleaned = [normalize_title(t) for t in titles]
    cleaned = [t for t in cleaned if t]
    ordered_titles = dedup_preserve_order(cleaned)
    total = len(ordered_titles)
    resolved: dict[str, str] = {}

    if total == 0:
        return resolved

    num_batches = (total + batch_size - 1) // batch_size

    for batch_idx, batch in enumerate(batched(ordered_titles, batch_size), start=1):
        params = {
            "action": "query",
            "format": "json",
            "redirects": 1,
            "prop": "pageprops",
            "ppprop": "wikibase_item",
            "titles": "|".join(batch),
        }

        data = {}
        for attempt in range(5):
            try:
                resp = session.get(endpoint, params=params, timeout=30)
                if resp.status_code in (429, 500, 502, 503, 504):
                    raise RuntimeError(f"HTTP {resp.status_code}")
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as ex:
                if attempt == 4:
                    print(
                        f"[WARN] {lang}: batch {batch_idx}/{num_batches} failed permanently: {ex}"
                    )
                    data = {}
                    time.sleep(5)
                else:
                    time.sleep(1.5 * (attempt + 1))

        query = data.get("query", {}) if isinstance(data, dict) else {}
        normalized_map = {
            x.get("from", ""): x.get("to", "") for x in query.get("normalized", [])
        }
        redirect_map = {
            x.get("from", ""): x.get("to", "") for x in query.get("redirects", [])
        }

        title_to_qid: dict[str, str] = {}
        for page in query.get("pages", {}).values():
            if not isinstance(page, dict):
                continue
            page_title = page.get("title")
            qid = page.get("pageprops", {}).get("wikibase_item")
            if page_title and isinstance(qid, str) and qid.startswith("Q"):
                title_to_qid[page_title] = qid

        for original in batch:
            cur = original
            for _ in range(5):
                changed = False
                nxt = normalized_map.get(cur)
                if nxt:
                    cur = nxt
                    changed = True
                nxt = redirect_map.get(cur)
                if nxt:
                    cur = nxt
                    changed = True
                if not changed:
                    break

            qid = title_to_qid.get(cur)
            if qid:
                resolved[original] = qid

        if batch_idx % 20 == 0 or batch_idx == num_batches:
            print(
                f"[INFO] {lang}: resolved {len(resolved)}/{total} unique titles "
                f"(batch {batch_idx}/{num_batches})"
            )

        time.sleep(0.08)

    return resolved


def collect_test_mentions(zip_path: Path) -> dict:
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        names_set = set(names)

        data = {"languages": {}, "all_en_titles": set()}

        for lang in LANGS:
            prefix = f"xlwikifier-wikidata/data/{lang}/test/"
            mention_paths = sorted(
                n for n in names if n.startswith(prefix) and n.endswith(".mentions")
            )

            files = []
            lang_non_en_titles = set()
            lang_en_titles = set()
            mentions_total = 0

            for mention_path in mention_paths:
                txt_path = mention_path[: -len(".mentions")] + ".txt"
                if txt_path not in names_set:
                    continue

                rows = []
                raw = zf.read(mention_path).decode("utf-8", errors="ignore")
                for line in raw.splitlines():
                    parts = line.split("\t")
                    if len(parts) < 5:
                        continue

                    start, end, en_title, non_en_title, is_hard = parts[:5]
                    try:
                        s = int(start)
                        e = int(end)
                        h = int(is_hard)
                    except Exception:
                        continue

                    en_title = en_title.strip()
                    non_en_title = non_en_title.strip()

                    rows.append((s, e, en_title, non_en_title, h))
                    mentions_total += 1

                    nen_norm = normalize_title(non_en_title)
                    en_norm = normalize_title(en_title)
                    if nen_norm:
                        lang_non_en_titles.add(nen_norm)
                    if en_norm:
                        lang_en_titles.add(en_norm)
                        data["all_en_titles"].add(en_norm)

                base = os.path.basename(mention_path)[: -len(".mentions")]
                files.append(
                    {
                        "base": base,
                        "mention_path": mention_path,
                        "txt_path": txt_path,
                        "rows": rows,
                    }
                )

            data["languages"][lang] = {
                "files": files,
                "non_en_titles": lang_non_en_titles,
                "en_titles": lang_en_titles,
                "num_files": len(files),
                "num_mentions": mentions_total,
            }

    return data


def build_prepared_dataset(
    zip_path: Path,
    collected: dict,
    lang_title_maps: dict[str, dict[str, str]],
    en_title_map: dict[str, str],
    out_root: Path,
) -> dict:
    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    summary = {"languages": {}}

    with zipfile.ZipFile(zip_path, "r") as zf:
        for lang in LANGS:
            lang_data = collected["languages"][lang]
            dst_dir = out_root / lang / "test"
            dst_dir.mkdir(parents=True, exist_ok=True)

            copied_txt = 0
            written_mentions_new = 0
            total_mentions = 0
            resolved_mentions = 0
            hard_mentions = 0
            hard_resolved = 0

            lang_map = lang_title_maps.get(lang, {})
            used_names: set[str] = set()

            for file_info in lang_data["files"]:
                base = make_safe_base_name(file_info["base"], used_names)
                txt_dst = dst_dir / f"{base}.txt"
                mentions_new_dst = dst_dir / f"{base}.mentions.new"

                txt_bytes = zf.read(file_info["txt_path"])
                txt_dst.write_bytes(txt_bytes)
                copied_txt += 1

                with mentions_new_dst.open("w", encoding="utf-8", newline="") as fout:
                    writer = csv.writer(fout, delimiter="\t")
                    writer.writerow(["start", "end", "non_en_title", "q_id", "is_hard"])

                    for s, e, en_title, non_en_title, h in file_info["rows"]:
                        qid = (
                            lang_map.get(normalize_title(non_en_title))
                            or en_title_map.get(normalize_title(en_title))
                            or "0"
                        )

                        total_mentions += 1
                        if h == 1:
                            hard_mentions += 1
                        if qid != "0":
                            resolved_mentions += 1
                            if h == 1:
                                hard_resolved += 1

                        writer.writerow([s, e, non_en_title, qid, h])

                written_mentions_new += 1

            summary["languages"][lang] = {
                "files": lang_data["num_files"],
                "mentions": lang_data["num_mentions"],
                "copied_txt_files": copied_txt,
                "written_mentions_new_files": written_mentions_new,
                "resolved_mentions": resolved_mentions,
                "hard_mentions": hard_mentions,
                "hard_resolved": hard_resolved,
            }

    return summary


def make_tarball(source_root: Path, tar_path: Path) -> None:
    if tar_path.exists():
        tar_path.unlink()

    with tarfile.open(tar_path, "w:gz") as tf:
        for lang in LANGS:
            tf.add(source_root / lang, arcname=lang)


def run_cmd(client: paramiko.SSHClient, command: str) -> tuple[int, str, str]:
    _, stdout, stderr = client.exec_command(command)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    return code, out, err


def upload_file(client: paramiko.SSHClient, local_path: Path, remote_path: str) -> None:
    sftp = client.open_sftp()
    try:
        local_size = local_path.stat().st_size
        print(f"[INFO] Uploading {local_path.name} ({local_size} bytes) to remote...")
        sftp.put(str(local_path), remote_path)
    finally:
        sftp.close()


def deploy_to_remote(client: paramiko.SSHClient, tar_path: Path) -> None:
    code, out, err = run_cmd(
        client,
        (
            f"mkdir -p {REMOTE_SOURCE_ROOT} {REMOTE_DATASET_ROOT} "
            f"{REMOTE_DATASET_ROOT}/de/test {REMOTE_DATASET_ROOT}/es/test "
            f"{REMOTE_DATASET_ROOT}/fr/test {REMOTE_DATASET_ROOT}/it/test"
        ),
    )
    if code != 0:
        raise RuntimeError(f"Failed preparing remote directories: {err or out}")

    upload_file(client, tar_path, REMOTE_PREPARED_TAR)

    extract_cmd = f"""
for lang in de es fr it; do
  d=\"{REMOTE_DATASET_ROOT}/$lang/test\"
  find \"$d\" -maxdepth 1 -type f -delete
  mkdir -p \"$d\"
done

tar -xzf \"{REMOTE_PREPARED_TAR}\" -C \"{REMOTE_DATASET_ROOT}\"
"""
    code, out, err = run_cmd(client, extract_cmd)
    if code != 0:
        raise RuntimeError(f"Failed extracting prepared tar on remote: {err or out}")


def verify_remote_layout(client: paramiko.SSHClient) -> str:
    cmd = f"""
for lang in de es fr it; do
  d=\"{REMOTE_DATASET_ROOT}/$lang/test\"
  txt=$(find \"$d\" -maxdepth 1 -type f -name '*.txt' | wc -l)
  men=$(find \"$d\" -maxdepth 1 -type f -name '*.mentions.new' | wc -l)
  echo \"$lang txt=$txt mentions_new=$men\"
done
"""
    code, out, err = run_cmd(client, cmd)
    if code != 0:
        raise RuntimeError(f"Remote layout check failed: {err or out}")
    return out


def main() -> int:
    if not LOCAL_ZIP.exists():
        print(f"[ERROR] Missing local zip: {LOCAL_ZIP}")
        return 1

    print("[INFO] Collecting test mention files from zip...")
    collected = collect_test_mentions(LOCAL_ZIP)
    for lang in LANGS:
        info = collected["languages"][lang]
        print(
            f"[INFO] {lang}: files={info['num_files']} mentions={info['num_mentions']} "
            f"unique_non_en_titles={len(info['non_en_titles'])}"
        )

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    LOCAL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    lang_title_maps: dict[str, dict[str, str]] = {}
    for lang in LANGS:
        titles = sorted(collected["languages"][lang]["non_en_titles"])
        cache_path = LOCAL_CACHE_DIR / f"{lang}_wiki_map.json"
        cached = load_json_map(cache_path)
        missing = [t for t in titles if t not in cached]
        if missing:
            print(
                f"[INFO] Resolving {len(missing)} non-English titles for {lang} via {lang}wiki..."
            )
            resolved = resolve_titles_via_wikipedia(lang, missing, session)
            cached.update(resolved)
            save_json_map(cache_path, cached)
        else:
            print(f"[INFO] Using cached {lang}wiki map ({len(cached)} titles).")
        lang_title_maps[lang] = cached

    unresolved_en_titles = set()
    for lang in LANGS:
        lang_map = lang_title_maps.get(lang, {})
        for file_info in collected["languages"][lang]["files"]:
            for _, _, en_title, non_en_title, _ in file_info["rows"]:
                if normalize_title(non_en_title) not in lang_map:
                    en_norm = normalize_title(en_title)
                    if en_norm:
                        unresolved_en_titles.add(en_norm)

    en_cache_path = LOCAL_CACHE_DIR / "en_wiki_map.json"
    en_title_map = load_json_map(en_cache_path)
    missing_en = sorted(t for t in unresolved_en_titles if t not in en_title_map)
    if missing_en:
        print(
            f"[INFO] Resolving {len(missing_en)} English fallback titles via enwiki..."
        )
        resolved_en = resolve_titles_via_wikipedia("en", missing_en, session)
        en_title_map.update(resolved_en)
        save_json_map(en_cache_path, en_title_map)
    else:
        print(f"[INFO] Using cached enwiki fallback map ({len(en_title_map)} titles).")

    print("[INFO] Building local prepared dataset with .mentions.new files...")
    summary = build_prepared_dataset(
        LOCAL_ZIP,
        collected,
        lang_title_maps,
        en_title_map,
        LOCAL_PREPARED_ROOT,
    )

    print("[INFO] Creating tarball for remote sync...")
    make_tarball(LOCAL_PREPARED_ROOT, LOCAL_PREPARED_TAR)

    print("[INFO] Connecting to remote host and deploying prepared data...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=45)

    try:
        deploy_to_remote(client, LOCAL_PREPARED_TAR)
        remote_layout = verify_remote_layout(client)
    finally:
        client.close()

    print("[INFO] Conversion summary:")
    print(json.dumps(summary, indent=2))
    print("[INFO] Remote target layout:")
    print(remote_layout)

    return 0


if __name__ == "__main__":
    sys.exit(main())
