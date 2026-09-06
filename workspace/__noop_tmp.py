import paramiko
host='172.20.70.80'; user='kmpooja'; pwd='kmpooja123'
cmd="""
python3 - << 'PY'
import os, pickle, zipfile
base='/DATA/kmpooja/mrefined_option1/assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data'
p=os.path.join(base,'lang_title2wikidataID-normalized_with_redirect.pkl')
with open(p,'rb') as f:
    mp=pickle.load(f)
z=zipfile.ZipFile('/DATA/kmpooja/mrefined_option1/assets/tr2016_source_probe/__nonexistent__.zip','r')
PY
"""
print('skip')
