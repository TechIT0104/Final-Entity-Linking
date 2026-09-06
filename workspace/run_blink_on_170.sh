#!/bin/bash
set -e

LOG="/home/kmpooja/entity_linking/blink_eval_170_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1

echo "[$(date)] =============================================="
echo "[$(date)] BLINK BENCHMARK ON SERVER 170 (4x RTX 3090)"
echo "[$(date)] =============================================="

# ============================================
# STEP 1: Fix benchmark data on server 80
# ============================================
echo "[$(date)] STEP 1: Fixing BLINK benchmark data on server 80..."

# Upload fix script
scp /home/kmpooja/entity_linking/fix_blink_data.py kmpooja@172.20.70.80:/home/kmpooja/blink_eval/fix_blink_data.py

# Run fix script on server 80 (CPU only, no GPU needed)
ssh kmpooja@172.20.70.80 "cd /home/kmpooja/blink_eval && source blink_env/bin/activate && python fix_blink_data.py"

echo "[$(date)] STEP 1 DONE: Benchmark data fixed"

# ============================================
# STEP 2: Copy BLINK models & data from server 80 to /tmp on 170
# ============================================
echo "[$(date)] STEP 2: Copying BLINK models from server 80..."

BLINK_DIR="/tmp/blink_eval"
mkdir -p "$BLINK_DIR/models"
mkdir -p "$BLINK_DIR/data/BLINK_benchmark"

# Copy models (only if not already present)
for f in biencoder_wiki_large.bin biencoder_wiki_large.json crossencoder_wiki_large.bin crossencoder_wiki_large.json entity.jsonl all_entities_large.t7; do
    if [ ! -f "$BLINK_DIR/models/$f" ]; then
        echo "[$(date)]   Copying $f..."
        scp kmpooja@172.20.70.80:/home/kmpooja/blink_eval/BLINK/models/$f "$BLINK_DIR/models/$f"
    else
        echo "[$(date)]   $f already exists, skipping"
    fi
done

# Copy fixed benchmark data
echo "[$(date)]   Copying benchmark data..."
scp kmpooja@172.20.70.80:/home/kmpooja/blink_eval/BLINK/data/BLINK_benchmark/*.jsonl "$BLINK_DIR/data/BLINK_benchmark/"

echo "[$(date)] STEP 2 DONE: Models and data copied"

# ============================================
# STEP 3: Set up BLINK environment on 170
# ============================================
echo "[$(date)] STEP 3: Setting up BLINK environment..."

BLINK_CODE="/home/kmpooja/entity_linking/BLINK"

# Create/reuse venv
if [ ! -d "/home/kmpooja/entity_linking/blink_env" ]; then
    python3 -m venv /home/kmpooja/entity_linking/blink_env
fi
source /home/kmpooja/entity_linking/blink_env/bin/activate

# Install deps
pip install torch torchvision --quiet 2>/dev/null || true
pip install numpy==1.26.4 faiss-cpu prettytable termcolor colorama pytorch-transformers --quiet 2>/dev/null || true

echo "[$(date)] STEP 3 DONE: Environment ready"

# ============================================
# STEP 4: Run BLINK benchmark (only remaining datasets)
# ============================================
echo "[$(date)] STEP 4: Running BLINK benchmark..."

cd "$BLINK_CODE"

# Create a custom run script that only runs the 5 remaining datasets
# plus re-runs AIDA testa and testb for completeness
export PYTHONPATH="$BLINK_CODE:$PYTHONPATH"
export CUDA_VISIBLE_DEVICES="0"

python -u blink/run_benchmark.py \
    --biencoder_model "$BLINK_DIR/models/biencoder_wiki_large.bin" \
    --biencoder_config "$BLINK_DIR/models/biencoder_wiki_large.json" \
    --crossencoder_model "$BLINK_DIR/models/crossencoder_wiki_large.bin" \
    --crossencoder_config "$BLINK_DIR/models/crossencoder_wiki_large.json" \
    --entity_catalogue "$BLINK_DIR/models/entity.jsonl" \
    --entity_encoding "$BLINK_DIR/models/all_entities_large.t7" \
    --test_mentions "$BLINK_DIR/data/BLINK_benchmark" \
    --output_path "/tmp/blink_results"

echo "[$(date)] STEP 4 DONE: BLINK benchmark complete"
echo "[$(date)] =============================================="
echo "[$(date)] ALL DONE"
echo "[$(date)] =============================================="
