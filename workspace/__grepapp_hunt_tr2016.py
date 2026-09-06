import requests

queries = [
    'TR2016hard',
    'TR2016',
    'preprocess_TR2016.py',
    '.mentions.new',
    'is_hard q_id non_en_title',
    'cross-lingual wikification multilingual embeddings',
    'Tsai Roth 2016',
    'tac kbp 2016 entity linking',
    'xlwikifier',
    'tr2016/de/test',
]

for q in queries:
    try:
        r = requests.get(
            'https://grep.app/api/search',
            params={'q': q, 'regexp': 'false', 'case': 'false'},
            timeout=40,
            headers={'User-Agent': 'Mozilla/5.0'},
        )
        print(f"\nQUERY: {q}\n status={r.status_code}")
        if r.status_code != 200:
            print(r.text[:200])
            continue
        js = r.json()
        total = js.get('hits', {}).get('total', 0)
        hits = js.get('hits', {}).get('hits', [])
        print(' total=', total, 'returned=', len(hits))
        for h in hits[:20]:
            repo = h.get('repo')
            path = h.get('path')
            snippet = h.get('content', {}).get('snippet', '')
            if any(k in snippet.lower() for k in ['http', 'https', 'tr2016', 'ldc', 'tac', 'download', 'tsai', 'roth', 'mentions.new']):
                print('  ', repo, '::', path)
                # print compact snippet fragment
                s = snippet.replace('\n', ' ').replace('\r', ' ')
                if len(s) > 300:
                    s = s[:300] + '...'
                print('    ', s)
            else:
                print('  ', repo, '::', path)
    except Exception as e:
        print(' ERR', q, e)
