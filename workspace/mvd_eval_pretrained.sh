#!/bin/bash
# ======================================================================
# MVD: Download pretrained models + Evaluate on ZeShEL
# Server 170 (4x RTX 3090)
# ======================================================================
set -e

WORK=/home/kmpooja/entity_linking/MVD
PYEXE=/home/kmpooja/entity_linking/mvd_env/bin/python
MODELS_DIR=/tmp/mvd_pretrained
LOG=/home/kmpooja/entity_linking/mvd_eval_$(date '+%Y%m%d_%H%M%S').log

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
exec > >(tee -a "$LOG") 2>&1

source /home/kmpooja/entity_linking/mvd_env/bin/activate

log "============================================================"
log "   MVD: Download Pretrained + Evaluate"
log "============================================================"

# ---- Install gdown for Google Drive downloads ----
pip install gdown -q 2>/dev/null

mkdir -p $MODELS_DIR
cd $MODELS_DIR

# ---- Download pretrained models from Google Drive ----
# MVD README provides 3 checkpoints:
# 1. Warmup retriever: https://drive.google.com/file/d/1oYyfzq5kDNWZF502X2vt9fYKEfSjUjJ_/view
# 2. Teacher: https://drive.google.com/file/d/1MPWiCnTjE_wTGYrGe7DAPTemjonKs83Z/view
# 3. MVD retriever (final): https://drive.google.com/file/d/17DOtfKwSCjS9kZsDFG0lQQ0kghXXtE1u/view

log "Downloading MVD pretrained retriever (final model)..."
if [ ! -f "$MODELS_DIR/mvd_retriever.bin" ]; then
    gdown "17DOtfKwSCjS9kZsDFG0lQQ0kghXXtE1u" -O "$MODELS_DIR/mvd_retriever.bin" || {
        log "gdown failed, trying alternate method..."
        $PYEXE -c "
import gdown
gdown.download(id='17DOtfKwSCjS9kZsDFG0lQQ0kghXXtE1u', output='$MODELS_DIR/mvd_retriever.bin', quiet=False)
"
    }
fi
log "MVD retriever: $(ls -lh $MODELS_DIR/mvd_retriever.bin 2>/dev/null)"

log "Downloading warmup retriever..."
if [ ! -f "$MODELS_DIR/warmup_retriever.bin" ]; then
    gdown "1oYyfzq5kDNWZF502X2vt9fYKEfSjUjJ_" -O "$MODELS_DIR/warmup_retriever.bin" || true
fi
log "Warmup: $(ls -lh $MODELS_DIR/warmup_retriever.bin 2>/dev/null)"

log "Downloading teacher model..."
if [ ! -f "$MODELS_DIR/teacher.bin" ]; then
    gdown "1MPWiCnTjE_wTGYrGe7DAPTemjonKs83Z" -O "$MODELS_DIR/teacher.bin" || true
fi
log "Teacher: $(ls -lh $MODELS_DIR/teacher.bin 2>/dev/null)"

# ---- Verify data exists ----
log "Checking ZeShEL data..."
ls -la $WORK/data/zeshel/test.jsonl
ls $WORK/data/zeshel/entity/ | wc -l
log "Data OK"

# ---- GPU setup (exclude GPU 2 which is used by another user) ----
FREE_GPUS=$($PYEXE - <<'PYEOF'
import subprocess, re
out = subprocess.check_output(
    ["nvidia-smi","--query-gpu=index,memory.used","--format=csv,noheader"], text=True)
free = []
for line in out.strip().splitlines():
    idx, mem = line.split(",")
    mem_mb = int(re.sub(r"[^0-9]","", mem))
    if mem_mb < 1000:
        free.append(idx.strip())
print(",".join(free) if free else "0,1,3")
PYEOF
)
N_GPUS=$(echo "$FREE_GPUS" | tr ',' '\n' | wc -l)
export CUDA_VISIBLE_DEVICES="$FREE_GPUS"
log "GPUs: $FREE_GPUS (n=$N_GPUS)"

# ======================================================================
# EVALUATION 1: Warmup Retriever (baseline)
# ======================================================================
log ""
log "============================="
log " EVAL 1: Warmup Retriever"
log "============================="

EVAL_OUT_WARMUP=/tmp/mvd_eval_warmup
mkdir -p $EVAL_OUT_WARMUP

cd $WORK
$PYEXE -m torch.distributed.launch \
    --nproc_per_node=$N_GPUS \
    --master_port=29510 \
    main.py \
    --do_eval \
    --kb zeshel \
    --task_name retriever \
    --data_dir data/zeshel \
    --entity_data_dir data/zeshel/entity \
    --output_dir $EVAL_OUT_WARMUP \
    --bert_model bert-base-uncased \
    --pretrain_retriever $MODELS_DIR/warmup_retriever.bin \
    --max_seq_length 128 \
    --infer_view_type local \
    --train_view_type local \
    --max_ent_length 512 \
    --max_view_length 40 \
    --max_view_num 10 \
    --eval_batch_size 512 \
    --top_k 100 \
    --faiss \
    --seed 10000 \
    --cache_dir /tmp/mvd_cache \
    --do_lower_case

log "Warmup Results:"
cat $EVAL_OUT_WARMUP/eval_results.txt 2>/dev/null | tee -a "$LOG"

# ======================================================================
# EVALUATION 2: MVD Retriever (w/o global view)
# ======================================================================
log ""
log "============================="
log " EVAL 2: MVD (local view only)"
log "============================="

EVAL_OUT_LOCAL=/tmp/mvd_eval_local
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
    --eval_batch_size 512 \
    --top_k 100 \
    --faiss \
    --seed 10000 \
    --cache_dir /tmp/mvd_cache \
    --do_lower_case

log "MVD (local) Results:"
cat $EVAL_OUT_LOCAL/eval_results.txt 2>/dev/null | tee -a "$LOG"

# ======================================================================
# EVALUATION 3: MVD Retriever (global-local view — full model)
# ======================================================================
log ""
log "============================="
log " EVAL 3: MVD (global-local view)"
log "============================="

EVAL_OUT_GL=/tmp/mvd_eval_global_local
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
    --eval_batch_size 512 \
    --top_k 100 \
    --faiss \
    --seed 10000 \
    --cache_dir /tmp/mvd_cache \
    --do_lower_case

log "MVD (global-local) Results:"
cat $EVAL_OUT_GL/eval_results.txt 2>/dev/null | tee -a "$LOG"

# ======================================================================
# SUMMARY
# ======================================================================
log ""
log "============================================================"
log "   MVD EVALUATION SUMMARY"
log "============================================================"
log ""
log "--- Warmup Retriever ---"
cat $EVAL_OUT_WARMUP/eval_results.txt 2>/dev/null | tee -a "$LOG"
log ""
log "--- MVD (local view only) ---"
cat $EVAL_OUT_LOCAL/eval_results.txt 2>/dev/null | tee -a "$LOG"
log ""
log "--- MVD (global-local view) ---"
cat $EVAL_OUT_GL/eval_results.txt 2>/dev/null | tee -a "$LOG"
log ""
log "Paper reported: R@1=52.51, R@64=91.55 (global-local)"
log "============================================================"
log "DONE: $(date)"
