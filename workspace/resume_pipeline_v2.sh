#!/bin/bash
# ======================================================================
# MVD Pipeline — RESUME v2 from Stage 2 (Teacher)
# Fix: Exclude GPU 2 (occupied by another user) — use GPUs 0,1,3
# ======================================================================

set -u

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
WORK=/home/kmpooja/entity_linking/MVD
PY=/home/kmpooja/entity_linking/mvd_env/bin/activate
PYEXE=/home/kmpooja/entity_linking/mvd_env/bin/python
LOG=/home/kmpooja/entity_linking/mvd_resume_v2_${TIMESTAMP}.log
WARMUP_BIN=/tmp/mvd_models/retriever.bin
OUTBASE=/tmp/mvd_output

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
exec > >(tee -a "$LOG") 2>&1

log "============================================================"
log "   MVD Pipeline RESUME v2 — from Stage 2 (Teacher)"
log "   Excluding GPU 2 (occupied by another user)"
log "============================================================"

source $PY

# Verify pre-requisites
[ -f "$WORK/data/zeshel/train_cand.jsonl" ] || { log "ERROR: train_cand.jsonl missing"; exit 1; }
[ -f "$WORK/data/zeshel/valid_cand.jsonl" ] || { log "ERROR: valid_cand.jsonl missing"; exit 1; }
[ -f "$WARMUP_BIN" ]                        || { log "ERROR: warmup model missing"; exit 1; }
log "Pre-requisites OK"

# Detect free GPUs — exclude any with >1GB used (another user's process)
FREE_GPUS=$($PYEXE - <<'PYEOF'
import subprocess, re
out = subprocess.check_output(
    ["nvidia-smi","--query-gpu=index,memory.used","--format=csv,noheader"],
    text=True)
free = []
for line in out.strip().splitlines():
    idx, mem = line.split(",")
    mem_mb = int(re.sub(r"[^0-9]","", mem))
    if mem_mb < 1000:
        free.append(idx.strip())
print(",".join(free) if free else "0,1,3")
PYEOF
)
[ -z "$FREE_GPUS" ] && FREE_GPUS="0,1,3"
N_GPUS=$(echo "$FREE_GPUS" | tr ',' '\n' | wc -l)
export CUDA_VISIBLE_DEVICES="$FREE_GPUS"
log "GPUs: $FREE_GPUS (n=$N_GPUS)"

if [ "$N_GPUS" -lt 2 ]; then EVAL_BS=256; else EVAL_BS=512; fi

mkdir -p $OUTBASE/teacher $OUTBASE/mvd $OUTBASE/eval_mvd

best_ckpt() {
    local task=$1 odir=$2
    local f=$(ls -t "$odir"/${task}*.bin 2>/dev/null | head -1)
    echo "$f"
}

# ======================================================================
# STAGE 2 — Train Teacher Cross-Encoder
# ======================================================================
log ""
log "============================="
log " STAGE 2: Train Teacher"
log "============================="
log "Started: $(date)"

cd $WORK

# Clean any leftover teacher output from failed run
rm -f $OUTBASE/teacher/*.bin 2>/dev/null

$PYEXE -m torch.distributed.launch \
    --nproc_per_node=$N_GPUS \
    --master_port=29501 \
    main.py \
    --do_train \
    --kb zeshel \
    --task_name teacher \
    --data_dir data/zeshel \
    --entity_data_dir data/zeshel/entity \
    --output_dir $OUTBASE/teacher \
    --bert_model bert-base-uncased \
    --max_seq_length 128 \
    --cand_num 16 \
    --infer_view_type local \
    --train_view_type local \
    --max_ent_length 128 \
    --max_view_length 40 \
    --max_view_num 10 \
    --num_train_epochs 3 \
    --train_batch_size 1 \
    --gradient_accumulation_steps 1 \
    --learning_rate 2e-5 \
    --eval_per_epoch 2 \
    --eval_batch_size 16 \
    --best_checkpoint_metric accuracy \
    --seed 10000 \
    --cache_dir /tmp/mvd_cache \
    --do_lower_case

rc=$?
if [ $rc -ne 0 ]; then
    log "ERROR: Stage 2 (teacher) failed (exit $rc) — aborting."
    exit $rc
fi
log "Stage 2 Done: $(date)"
ls -lh $OUTBASE/teacher/*.bin 2>/dev/null | tee -a "$LOG"

TEACHER_BIN=$(best_ckpt "teacher" "$OUTBASE/teacher")
[ -z "$TEACHER_BIN" ] && TEACHER_BIN=$(ls -t $OUTBASE/teacher/*.bin 2>/dev/null | head -1)
log "Teacher: $TEACHER_BIN"
[ -z "$TEACHER_BIN" ] && { log "ERROR: No teacher .bin found"; exit 1; }

# ======================================================================
# STAGE 3 — MVD Distillation
# ======================================================================
log ""
log "============================="
log " STAGE 3: MVD Distillation"
log "============================="
log "Started: $(date)"

cd $WORK
$PYEXE -m torch.distributed.launch \
    --nproc_per_node=$N_GPUS \
    --master_port=29502 \
    main.py \
    --do_train \
    --kb zeshel \
    --task_name mvd \
    --data_dir data/zeshel \
    --entity_data_dir data/zeshel/entity \
    --output_dir $OUTBASE/mvd \
    --bert_model bert-base-uncased \
    --pretrain_retriever $WARMUP_BIN \
    --pretrain_teacher  $TEACHER_BIN \
    --max_seq_length 128 \
    --cand_num 16 \
    --infer_view_type global-local \
    --train_view_type local \
    --max_ent_length 128 \
    --max_view_length 40 \
    --max_view_num 10 \
    --num_train_epochs 5 \
    --train_batch_size 16 \
    --gradient_accumulation_steps 16 \
    --learning_rate 2e-5 \
    --eval_per_epoch 1 \
    --eval_batch_size $EVAL_BS \
    --top_k 100 \
    --faiss \
    --best_checkpoint_metric top64_hits \
    --seed 10000 \
    --cache_dir /tmp/mvd_cache \
    --do_lower_case

rc=$?
if [ $rc -ne 0 ]; then
    log "ERROR: Stage 3 (MVD) failed (exit $rc) — aborting."
    exit $rc
fi
log "Stage 3 Done: $(date)"
ls -lh $OUTBASE/mvd/*.bin 2>/dev/null | tee -a "$LOG"

MVD_BIN=$(best_ckpt "mvd" "$OUTBASE/mvd")
[ -z "$MVD_BIN" ] && MVD_BIN=$(ls -t $OUTBASE/mvd/*.bin 2>/dev/null | head -1)
log "MVD: $MVD_BIN"
[ -z "$MVD_BIN" ] && { log "ERROR: No MVD .bin found"; exit 1; }

# ======================================================================
# STAGE 4 — Final Evaluation
# ======================================================================
log ""
log "============================="
log " STAGE 4: Final Evaluation"
log "============================="
log "Started: $(date)"

cd $WORK
$PYEXE -m torch.distributed.launch \
    --nproc_per_node=$N_GPUS \
    --master_port=29503 \
    main.py \
    --do_eval \
    --kb zeshel \
    --task_name retriever \
    --data_dir data/zeshel \
    --entity_data_dir data/zeshel/entity \
    --output_dir $OUTBASE/eval_mvd \
    --bert_model bert-base-uncased \
    --pretrain_retriever $MVD_BIN \
    --max_seq_length 128 \
    --infer_view_type global-local \
    --train_view_type local \
    --max_ent_length 512 \
    --max_view_length 40 \
    --max_view_num 10 \
    --eval_batch_size $EVAL_BS \
    --top_k 100 \
    --faiss \
    --seed 10000 \
    --cache_dir /tmp/mvd_cache \
    --do_lower_case

log "Stage 4 Done: $(date)"
cat $OUTBASE/eval_mvd/eval_results.txt 2>/dev/null | tee -a "$LOG" || true

# ======================================================================
# STAGE 5 — Save Models
# ======================================================================
SAVE_DIR=/home/kmpooja/entity_linking/mvd_trained_models
mkdir -p $SAVE_DIR
cp "$TEACHER_BIN" "$SAVE_DIR/teacher.bin" 2>/dev/null && log "Saved: teacher.bin"
cp "$MVD_BIN"     "$SAVE_DIR/mvd.bin"     2>/dev/null && log "Saved: mvd.bin"
cp $OUTBASE/eval_mvd/*.json "$SAVE_DIR/"  2>/dev/null || true
cp $OUTBASE/eval_mvd/eval_results.txt "$SAVE_DIR/" 2>/dev/null || true

log ""
log "============================================================"
log "   MVD RESUME v2 Pipeline — COMPLETE"
log "   Finished: $(date)"
log "   Full log: $LOG"
log "============================================================"
