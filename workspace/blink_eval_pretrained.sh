#!/bin/bash
# ======================================================================
# BLINK: Setup + Download pretrained + Benchmark
# Server 80 (1x RTX 5000 Ada, 32GB)
# Run this FROM server 170 via: ssh kmpooja@172.20.70.80 'bash /path/to/this.sh'
# ======================================================================
set -e

WORK=/home/kmpooja/blink_eval
LOG=/home/kmpooja/blink_eval_$(date '+%Y%m%d_%H%M%S').log

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
exec > >(tee -a "$LOG") 2>&1

log "============================================================"
log "   BLINK: Setup + Download + Benchmark"
log "============================================================"

# ---- Create workspace ----
mkdir -p $WORK
cd $WORK

# ---- Setup Python venv ----
if [ ! -d "$WORK/blink_env" ]; then
    log "Creating virtual environment..."
    python3 -m venv blink_env
fi
source $WORK/blink_env/bin/activate

# ---- Install dependencies ----
log "Installing dependencies..."
pip install -q --upgrade pip
pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install -q transformers flair scipy tqdm requests jsonlines colorama pysolr
pip install -q faiss-gpu

# ---- Clone BLINK if not present ----
if [ ! -d "$WORK/BLINK" ]; then
    log "Cloning BLINK repo..."
    git clone https://github.com/facebookresearch/BLINK.git
fi
cd $WORK/BLINK
pip install -q -r requirements.txt 2>/dev/null || true
pip install -q -e . 2>/dev/null || true

# ---- Download BLINK pretrained models ----
log "Downloading BLINK pretrained models..."
mkdir -p models

# bi-encoder
if [ ! -f "models/biencoder_wiki_large.bin" ]; then
    log "  Downloading bi-encoder..."
    wget -q -O models/biencoder_wiki_large.bin "http://dl.fbaipublicfiles.com/BLINK/biencoder_wiki_large.bin" || true
fi

# bi-encoder config
if [ ! -f "models/biencoder_wiki_large.json" ]; then
    log "  Downloading bi-encoder config..."
    wget -q -O models/biencoder_wiki_large.json "http://dl.fbaipublicfiles.com/BLINK/biencoder_wiki_large.json" || true
fi

# cross-encoder
if [ ! -f "models/crossencoder_wiki_large.bin" ]; then
    log "  Downloading cross-encoder..."
    wget -q -O models/crossencoder_wiki_large.bin "http://dl.fbaipublicfiles.com/BLINK/crossencoder_wiki_large.bin" || true
fi

# cross-encoder config
if [ ! -f "models/crossencoder_wiki_large.json" ]; then
    log "  Downloading cross-encoder config..."
    wget -q -O models/crossencoder_wiki_large.json "http://dl.fbaipublicfiles.com/BLINK/crossencoder_wiki_large.json" || true
fi

# entity catalogue
if [ ! -f "models/entity.jsonl" ]; then
    log "  Downloading entity catalogue..."
    wget -q -O models/entity.jsonl "http://dl.fbaipublicfiles.com/BLINK/entity.jsonl" || true
fi

# entity encodings
if [ ! -f "models/all_entities_large.t7" ]; then
    log "  Downloading entity encodings (this is large ~2.4GB)..."
    wget -q -O models/all_entities_large.t7 "http://dl.fbaipublicfiles.com/BLINK/all_entities_large.t7" || true
fi

log "Model files:"
ls -lh models/ | tee -a "$LOG"

# ---- Download benchmark data ----
log "Downloading benchmark data..."
cd $WORK/BLINK

# Use BLINK's built-in download scripts
if [ ! -d "data" ] || [ $(ls data/ 2>/dev/null | wc -l) -lt 3 ]; then
    log "  Getting train and benchmark data..."
    chmod +x scripts/get_train_and_benchmark_data.sh
    bash scripts/get_train_and_benchmark_data.sh || true
fi

# Create BLINK benchmark format
log "Creating benchmark data..."
PYTHONPATH=. python scripts/create_BLINK_benchmark_data.py 2>&1 || true

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
log ""
log "Paper reported results:"
log "  AIDA-testb: bienc=79.51, cross=86.69, overall=80.27"
log "  MSNBC:      bienc=84.28, cross=90.31, overall=85.09"
log "  ACE2004:    bienc=84.43, cross=88.70, overall=86.89"
log "============================================================"
log "DONE: $(date)"
