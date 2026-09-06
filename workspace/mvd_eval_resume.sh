#!/bin/bash
# Resume MVD evaluation from eval 2 onward with reduced batch size
set -e

WORK=/home/kmpooja/entity_linking/MVD
PYEXE=/home/kmpooja/entity_linking/mvd_env/bin/python
MODELS_DIR=/tmp/mvd_pretrained
LOG=/home/kmpooja/entity_linking/mvd_eval_resume_$(date '+%Y%m%d_%H%M%S').log

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
exec > >(tee -a "$LOG") 2>&1

source /home/kmpooja/entity_linking/mvd_env/bin/activate

# GPU setup - only GPU 0 is free currently
export CUDA_VISIBLE_DEVICES="0"
N_GPUS=1
log "GPUs: 0 (n=1) - other GPUs occupied by manish"

# ====== EVAL 2: MVD Retriever (local view only) ======
log "============================="
log " EVAL 2: MVD (local view only)"
log "============================="

EVAL_OUT_LOCAL=/tmp/mvd_eval_local
rm -rf $EVAL_OUT_LOCAL
mkdir -p $EVAL_OUT_LOCAL

cd $WORK
$PYEXE -m torch.distributed.launch \
    --nproc_per_node=$N_GPUS \
    --master_port=29511 \
    main.py \
    --do_eval \
    --kb zeshel \
    --task_name retriever \
    --data_dir data/zeshel \
    --entity_data_dir data/zeshel/entity \
    --output_dir $EVAL_OUT_LOCAL \
    --bert_model bert-base-uncased \
    --pretrain_retriever $MODELS_DIR/mvd_retriever.bin \
    --max_seq_length 128 \
    --infer_view_type local \
    --train_view_type local \
    --max_ent_length 512 \
    --max_view_length 40 \
    --max_view_num 10 \
    --eval_batch_size 128 \
    --top_k 100 \
    --faiss \
    --seed 10000 \
    --cache_dir /tmp/mvd_cache \
    --do_lower_case

log "MVD (local) Results:"
cat $EVAL_OUT_LOCAL/eval_results.txt 2>/dev/null | tee -a "$LOG"

# ====== EVAL 3: MVD Retriever (global-local view) ======
log ""
log "============================="
log " EVAL 3: MVD (global-local view)"
log "============================="

EVAL_OUT_GL=/tmp/mvd_eval_global_local
rm -rf $EVAL_OUT_GL
mkdir -p $EVAL_OUT_GL

cd $WORK
$PYEXE -m torch.distributed.launch \
    --nproc_per_node=$N_GPUS \
    --master_port=29512 \
    main.py \
    --do_eval \
    --kb zeshel \
    --task_name retriever \
    --data_dir data/zeshel \
    --entity_data_dir data/zeshel/entity \
    --output_dir $EVAL_OUT_GL \
    --bert_model bert-base-uncased \
    --pretrain_retriever $MODELS_DIR/mvd_retriever.bin \
    --max_seq_length 128 \
    --infer_view_type global-local \
    --train_view_type local \
    --max_ent_length 512 \
    --max_view_length 40 \
    --max_view_num 10 \
    --eval_batch_size 128 \
    --top_k 100 \
    --faiss \
    --seed 10000 \
    --cache_dir /tmp/mvd_cache \
    --do_lower_case

log "MVD (global-local) Results:"
cat $EVAL_OUT_GL/eval_results.txt 2>/dev/null | tee -a "$LOG"

# ====== SUMMARY ======
log ""
log "============================================================"
log "   MVD EVALUATION SUMMARY (RESUMED)"
log "============================================================"
log ""
log "--- Warmup Retriever (from previous run) ---"
cat /tmp/mvd_eval_warmup/eval_results.txt 2>/dev/null | tee -a "$LOG"
log ""
log "--- MVD (local view only) ---"
cat $EVAL_OUT_LOCAL/eval_results.txt 2>/dev/null | tee -a "$LOG"
log ""
log "--- MVD (global-local view) ---"
cat $EVAL_OUT_GL/eval_results.txt 2>/dev/null | tee -a "$LOG"
log ""
log "Paper: Warmup R@1=41.99, R@64=88.22"
log "Paper: MVD local R@1=51.27, R@64=91.16"
log "Paper: MVD global-local R@1=52.51, R@64=91.55"
log "============================================================"
log "DONE: $(date)"
