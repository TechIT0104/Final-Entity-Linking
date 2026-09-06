#!/usr/bin/env python3
"""Run A/B evaluation for TR2016 and extract RECALL@1 (accuracy metric) matching paper."""

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

# Languages to evaluate
LANGS = ['de', 'es', 'fr', 'it']

print('\n' + '='*80)
print('TR2016 RECALL@1 EVALUATION - MATCHING PAPER METRIC')
print('='*80)

print('\nLoading model once...')
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

for LANG in LANGS:
    print(f'\n{"-"*60}')
    print(f'Language: {LANG.upper()}')
    print(f'{"-"*60}')
    
    DSET = f'assets/tr2016/{LANG}/test'
    pem = LmdbImmutableDict(os.path.join(DATA_DIR, f'wikidata_data/pem_{LANG}.lmdb'))
    refined.preprocessor.lookups.pem = pem
    refined.preprocessor.candidate_generator.pem = pem
    refined.preprocessor.candidate_generator.language = LANG

    for validate in [False, True]:
        mode = 'WITH_OFFSET_VALIDATION' if validate else 'BASELINE (no validation)'
        print(f'\n{mode}:')
        
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
        
        # Extract key metrics
        recall_at_1 = metrics.get_accuracy()  # This is Recall@1 matching paper
        gold_recall = metrics.get_gold_recall()
        num_gold = metrics.num_gold_spans
        tp = metrics.tp
        
        print(f'  Recall@1 (accuracy): {recall_at_1:.4f} ({recall_at_1*100:.2f}%)')
        print(f'  Gold Recall: {gold_recall:.4f} ({gold_recall*100:.2f}%)')
        print(f'  Candidate Recall: {metrics.get_recall():.4f} ({metrics.get_recall()*100:.2f}%)')
        print(f'  TP: {tp} / {num_gold} gold entities')
'''

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PW, timeout=30)

remote_script = WORKDIR + '/__tmp_eval_recall_at_1_remote.py'
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
    sys.stdout.write(line)
    sys.stdout.flush()

err = se.read().decode('utf-8', errors='replace')
if err.strip():
    print('\n[STDERR]')
    print(err)

client.close()
print('\n' + '='*80)
print('✓ Evaluation complete')
print('='*80)
