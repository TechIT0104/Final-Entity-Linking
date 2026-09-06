import paramiko
import sys

HOST='172.20.70.80'
USER='kmpooja'
PW='kmpooja123'
WORKDIR='/DATA/kmpooja/mrefined_option1'

remote_py = r'''
import os
import pickle
from refined.inference.processor import Refined
from refined.evaluation.evaluation import evaluate_on_docs
from refined.dataset_reading.entity_linking.dataset_reader_multilingual import Datasets
from refined.resource_management.lmdb_wrapper import LmdbImmutableDict

DATA_DIR='assets/data_combine_11_languages_wikidata_all_eng_label_desc'
ADDITIONAL='assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data'
MODEL='assets/finetune_models/mReFinED_Recall_9343'
LANG='es'
DSET='assets/tr2016/es/test'

print('Loading model once for A/B...')
with open(os.path.join(ADDITIONAL,'lang_title2wikidataID-normalized_with_redirect.pkl'),'rb') as f:
    lang_title2wikidataID = pickle.load(f)
mention2wikidataID = LmdbImmutableDict(os.path.join(ADDITIONAL,'mention2wikidataID.lmdb'))

refined = Refined.from_pretrained(
    model_name=MODEL,
    entity_set='wikidata',
    use_precomputed_descriptions=True,
    data_dir=DATA_DIR,
    download_files=False,
    device='cuda:0',
)

refined.preprocessor.candidate_generator.mention2wikidataID = mention2wikidataID
refined.preprocessor.candidate_generator.lang_title2wikidataID = lang_title2wikidataID
refined.model.ed_2.temperature_scaling = 0.02
refined.preprocessor.candidate_generator.combine = False
pem = LmdbImmutableDict(os.path.join(DATA_DIR, f'wikidata_data/pem_{LANG}.lmdb'))
refined.preprocessor.lookups.pem = pem
refined.preprocessor.candidate_generator.pem = pem
refined.preprocessor.candidate_generator.language = LANG

for validate in [False, True]:
    datasets = Datasets(preprocessor=refined.preprocessor, datasets_path=DSET)
    docs = datasets.get_tr2016_docs(filename=DSET, lang=LANG)
    metrics = evaluate_on_docs(
        refined=refined,
        docs=docs,
        dataset_name=f'tr2016-{LANG}',
        el=True,
        ed_threshold=0.0,
        topk_eval=True,
        top_k=3,
        progress_bar=False,
        validate_gold_offsets=validate,
    )
    print('RUN', 'WITH_VALIDATION' if validate else 'NO_VALIDATION')
    print('SAMPLE_SIZE', 'full')
    print('RECALL', metrics.get_recall())
    print('PRECISION', metrics.get_precision())
    print('F1', metrics.get_f1())
    print('GOLD_RECALL', metrics.get_gold_recall())
'''

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)

remote_script = WORKDIR + '/__tmp_eval_es_offset_ab_remote.py'
sftp = client.open_sftp()
with sftp.open(remote_script, 'w') as f:
    f.write(remote_py)
sftp.close()

cmd = (
    "bash -lc 'cd " + WORKDIR
    + "; source venv/bin/activate"
    + "; export PYTHONUNBUFFERED=1"
    + "; export CUDA_VISIBLE_DEVICES=0"
    + "; python3 " + remote_script
    + "; rc=$?"
    + "; rm -f " + remote_script
    + "; echo __RC__:$rc'"
)

_, so, se = client.exec_command(cmd, get_pty=True)

while True:
    line = so.readline()
    if not line:
        break
    sys.stdout.buffer.write(line.encode('utf-8') if isinstance(line, str) else line)
    sys.stdout.buffer.flush()

err = se.read().decode('utf-8', errors='replace')
if err.strip():
    print('\n[STDERR]')
    print(err)
client.close()
