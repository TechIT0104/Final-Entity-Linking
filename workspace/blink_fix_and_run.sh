#!/bin/bash
# ======================================================================
# BLINK: Fix + Re-run Benchmark
# Server 80 (1x RTX 5000 Ada, 32GB)
# ======================================================================
set -e

WORK=/home/kmpooja/blink_eval
LOG=/home/kmpooja/blink_eval_fix_$(date '+%Y%m%d_%H%M%S').log

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
exec > >(tee -a "$LOG") 2>&1

source $WORK/blink_env/bin/activate
cd $WORK/BLINK

# ---- Fix missing modules ----
log "Installing missing packages..."
pip install -q prettytable flair

# ---- Fix benchmark data ----
log "Checking/downloading benchmark data..."
mkdir -p data

# Download using BLINK's script
if [ ! -d "data/train_and_benchmark_data" ]; then
    log "Downloading benchmark data..."
    cd data
    
    # The get_train_and_benchmark_data.sh downloads from BLINK server
    if [ ! -f "BLINK_benchmark_data.jsonl" ]; then
        wget -q "http://dl.fbaipublicfiles.com/BLINK/BLINK_benchmark_data.jsonl" || true
    fi
    
    # Also need the AIDA/MSNBC etc. test data
    if [ ! -d "train_and_benchmark_data" ]; then
        mkdir -p train_and_benchmark_data
        cd train_and_benchmark_data
        # Download from BLINK's release URLs
        wget -q "http://dl.fbaipublicfiles.com/BLINK/BLINK_benchmark_data.jsonl" -O benchmark.jsonl || true
        cd ..
    fi
    cd $WORK/BLINK
fi

# ---- Check what run_benchmark expects ----
log "Checking run_benchmark.py requirements..."
head -50 blink/run_benchmark.py | tee -a "$LOG"

# ---- Check what data files exist ----
log "Data files:"
find data/ -type f | head -30 | tee -a "$LOG"

# ---- Read get_train_and_benchmark_data.sh to understand data download ----
log "Checking data download script..."
cat scripts/get_train_and_benchmark_data.sh | tee -a "$LOG"

# ---- Download data properly ----
log "Running official data download..."
cd $WORK/BLINK
bash scripts/get_train_and_benchmark_data.sh 2>&1 | tail -20 | tee -a "$LOG"

# ---- Create benchmark format ----
log "Creating benchmark data..."
PYTHONPATH=. python scripts/create_BLINK_benchmark_data.py 2>&1 | tee -a "$LOG"

# ---- List benchmark data files ----
log "Benchmark data:"
find data/ -name "*.jsonl" -o -name "*.t7" -o -name "*.json" 2>/dev/null | head -30 | tee -a "$LOG"

# ---- Run benchmark ----
log ""
log "============================="
log " Running BLINK Benchmark"
log "============================="

export CUDA_VISIBLE_DEVICES=0

PYTHONPATH=. python blink/run_benchmark.py \
    --biencoder_model models/biencoder_wiki_large.bin \
    --biencoder_config models/biencoder_wiki_large.json \
    --crossencoder_model models/crossencoder_wiki_large.bin \
    --crossencoder_config models/crossencoder_wiki_large.json \
    --entity_catalogue models/entity.jsonl \
    --entity_encoding models/all_entities_large.t7 \
    --output_path output/ \
    --top_k 100 2>&1 | tee -a "$LOG"

log ""
log "============================================================"
log "   BLINK BENCHMARK COMPLETE"
log "============================================================"
log "DONE: $(date)"
