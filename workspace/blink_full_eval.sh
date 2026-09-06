#!/bin/bash
set -e

LOG="/home/kmpooja/entity_linking/blink_full_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1

echo "[$(date)] =============================================="
echo "[$(date)] COMPLETE BLINK EVALUATION ON SERVER 170"
echo "[$(date)] =============================================="

BLINK_CODE="/home/kmpooja/entity_linking/BLINK"
MODELS_TMP="/tmp/blink_models"

# ============================================
# STEP 1: Fix benchmark data on server 80
# ============================================
echo "[$(date)] STEP 1: Fixing BLINK benchmark data on server 80..."
ssh kmpooja@172.20.70.80 "cd /home/kmpooja/blink_eval && source blink_env/bin/activate && python fix_blink_data.py"
echo "[$(date)] STEP 1 DONE"

# ============================================
# STEP 2: Copy data & models from server 80
# ============================================
echo "[$(date)] STEP 2: Copying models and data from server 80..."

mkdir -p "$MODELS_TMP"
mkdir -p "$BLINK_CODE/data/BLINK_benchmark"

# Copy benchmark data (small, ~50MB total)
echo "[$(date)]   Copying benchmark data..."
scp kmpooja@172.20.70.80:/home/kmpooja/blink_eval/BLINK/data/BLINK_benchmark/*.jsonl "$BLINK_CODE/data/BLINK_benchmark/"

# Copy models to /tmp (large files ~31GB total)
for f in biencoder_wiki_large.bin biencoder_wiki_large.json crossencoder_wiki_large.bin crossencoder_wiki_large.json entity.jsonl all_entities_large.t7; do
    if [ -f "$MODELS_TMP/$f" ]; then
        echo "[$(date)]   $f already exists, skipping"
    else
        echo "[$(date)]   Copying $f from server 80..."
        scp kmpooja@172.20.70.80:/home/kmpooja/blink_eval/BLINK/models/$f "$MODELS_TMP/$f"
    fi
done

# Symlink models to expected location
echo "[$(date)]   Creating symlinks..."
mkdir -p "$BLINK_CODE/models"
for f in biencoder_wiki_large.bin biencoder_wiki_large.json crossencoder_wiki_large.bin crossencoder_wiki_large.json entity.jsonl all_entities_large.t7; do
    ln -sf "$MODELS_TMP/$f" "$BLINK_CODE/models/$f"
done

echo "[$(date)] STEP 2 DONE"

# ============================================
# STEP 3: Set up Python environment
# ============================================
echo "[$(date)] STEP 3: Setting up Python environment..."

if [ ! -d "/home/kmpooja/entity_linking/blink_env" ]; then
    python3 -m venv /home/kmpooja/entity_linking/blink_env
fi
source /home/kmpooja/entity_linking/blink_env/bin/activate

pip install --quiet torch torchvision 2>&1 | tail -2
pip install --quiet numpy==1.26.4 faiss-cpu prettytable termcolor colorama pytorch-transformers 2>&1 | tail -2

echo "[$(date)] STEP 3 DONE"

# ============================================
# STEP 4: Run BLINK benchmark
# ============================================
echo "[$(date)] STEP 4: Running BLINK benchmark (all 7 datasets)..."

cd "$BLINK_CODE"
export PYTHONPATH="$BLINK_CODE:$PYTHONPATH"
export CUDA_VISIBLE_DEVICES="0"

python -u blink/run_benchmark.py

echo "[$(date)] STEP 4 DONE"

# ============================================
# STEP 5: Cleanup
# ============================================
echo "[$(date)] STEP 5: Cleaning up /tmp models..."
rm -rf "$MODELS_TMP"
rm -f "$BLINK_CODE/models/biencoder_wiki_large.bin"
rm -f "$BLINK_CODE/models/biencoder_wiki_large.json"
rm -f "$BLINK_CODE/models/crossencoder_wiki_large.bin"
rm -f "$BLINK_CODE/models/crossencoder_wiki_large.json"
rm -f "$BLINK_CODE/models/entity.jsonl"
rm -f "$BLINK_CODE/models/all_entities_large.t7"
rmdir "$BLINK_CODE/models" 2>/dev/null || true

echo "[$(date)] =============================================="
echo "[$(date)] ALL COMPLETE"
echo "[$(date)] =============================================="
