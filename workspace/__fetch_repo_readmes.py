import requests
from pathlib import Path

files = {
    '__mrefined_README.md': 'https://raw.githubusercontent.com/amazon-science/ReFinED/mrefined/README.md',
    '__mrefined_root_README.md': 'https://raw.githubusercontent.com/amazon-science/ReFinED/main/README.md',
    '__genre_scripts_README.md': 'https://raw.githubusercontent.com/facebookresearch/GENRE/main/scripts_mgenre/README.md',
    '__genre_root_README.md': 'https://raw.githubusercontent.com/facebookresearch/GENRE/main/README.md',
}
for out, url in files.items():
    r = requests.get(url, timeout=30)
    print(out, r.status_code, len(r.text))
    if r.status_code == 200:
        Path(out).write_text(r.text, encoding='utf-8')
