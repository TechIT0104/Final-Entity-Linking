import paramiko, posixpath
HOST='172.20.70.80'; USER='kmpooja'; PW='kmpooja123'
WORKDIR='/DATA/kmpooja/mrefined_option1'
REMOTE_SCRIPT='/tmp/tr2016_ab_desc.py'
remote_py = '''import os,pickle,time,torch
from refined.inference.processor import Refined
from refined.evaluation.evaluation import evaluate_on_docs
from refined.dataset_reading.entity_linking.dataset_reader_multilingual import Datasets
from refined.resource_management.lmdb_wrapper import LmdbImmutableDict

DATA_DIR='assets/data_combine_11_languages_wikidata_all_eng_label_desc'
MODEL='assets/finetune_models/mReFinED_Recall_9343'
LANG='de'
DSET='assets/tr2016/de/test'
ADD='assets/data_combine_11_languages_wikidata_all_eng_label_desc/additional_data'
with open(os.path.join(ADD,'lang_title2wikidataID-normalized_with_redirect.pkl'),'rb') as f:
    lang_title2wikidataID=pickle.load(f)
mention2wikidataID=LmdbImmutableDict(os.path.join(ADD,'mention2wikidataID.lmdb'))

for flag in [True, False]:
    t0=time.time()
    refined=Refined.from_pretrained(
        model_name=MODEL,
        entity_set='wikidata',
        use_precomputed_descriptions=flag,
        data_dir=DATA_DIR,
        download_files=False,
        device='cuda:0'
    )
    refined.preprocessor.candidate_generator.mention2wikidataID=mention2wikidataID
    refined.preprocessor.candidate_generator.lang_title2wikidataID=lang_title2wikidataID
    refined.model.ed_2.temperature_scaling=0.02
    refined.preprocessor.candidate_generator.combine=False
    pem=LmdbImmutableDict(os.path.join(DATA_DIR,f'wikidata_data/pem_{LANG}.lmdb'))
    refined.preprocessor.lookups.pem=pem
    refined.preprocessor.candidate_generator.pem=pem
    refined.preprocessor.candidate_generator.language=LANG
    datasets=Datasets(preprocessor=refined.preprocessor,datasets_path=DSET)
    docs=datasets.get_tr2016_docs(filename=DSET,lang=LANG)
    m=evaluate_on_docs(refined=refined,docs=docs,dataset_name='ab-de',el=True,ed_threshold=0.0,topk_eval=True,top_k=3)
    print('FLAG',flag,'recall',m.get_recall(),'gold_recall',m.get_gold_recall(),'f1',m.get_f1(),'sec',round(time.time()-t0,1),'cuda',torch.cuda.is_available(), flush=True)
'''

cli=paramiko.SSHClient(); cli.set_missing_host_key_policy(paramiko.AutoAddPolicy()); cli.connect(HOST,username=USER,password=PW,timeout=30)
sftp=cli.open_sftp()
with sftp.open(REMOTE_SCRIPT,'w') as f:
    f.write(remote_py)
sftp.close()

cmd=f"bash -lc 'cd {WORKDIR}; source venv/bin/activate; export PYTHONUNBUFFERED=1; python3 {REMOTE_SCRIPT}; rc=$?; rm -f {REMOTE_SCRIPT}; exit $rc'"
_,so,se=cli.exec_command(cmd,get_pty=True)
while True:
    line=so.readline()
    if not line:
        break
    print(line,end='')
err=se.read().decode('utf-8','replace')
if err.strip():
    print('\n[STDERR]\n'+err)
print('__EXIT__',so.channel.recv_exit_status())
cli.close()
