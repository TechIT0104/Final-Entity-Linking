#!/bin/bash
set -e

LOG="/home/kmpooja/entity_linking/blink_full_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1

echo "[$(date)] Starting BLINK full evaluation pipeline"

BLINK_CODE="/home/kmpooja/entity_linking/BLINK"
MODELS_TMP="/tmp/blink_models"

# Copy models from server 80
echo "[$(date)] Copying models from server 80 to /tmp/blink_models..."
mkdir -p "$MODELS_TMP"

for f in biencoder_wiki_large.json crossencoder_wiki_large.json; do
    if [ ! -f "$MODELS_TMP/$f" ]; then
        echo "[$(date)]   Copying $f..."
        scp kmpooja@172.20.70.80:/home/kmpooja/blink_eval/BLINK/models/$f "$MODELS_TMP/$f"
    fi
done

for f in entity.jsonl crossencoder_wiki_large.bin biencoder_wiki_large.bin all_entities_large.t7; do
    if [ ! -f "$MODELS_TMP/$f" ]; then
        echo "[$(date)]   Copying $f..."
        scp kmpooja@172.20.70.80:/home/kmpooja/blink_eval/BLINK/models/$f "$MODELS_TMP/$f"
    fi
done

echo "[$(date)] Models copied"

# Symlink models
echo "[$(date)] Creating symlinks..."
mkdir -p "$BLINK_CODE/models"
for f in biencoder_wiki_large.bin biencoder_wiki_large.json crossencoder_wiki_large.bin crossencoder_wiki_large.json entity.jsonl all_entities_large.t7; do
    ln -sf "$MODELS_TMP/$f" "$BLINK_CODE/models/$f"
done

# Setup python env - reuse mvd_env which already has PyTorch+CUDA
echo "[$(date)] Setting up Python environment..."
source /home/kmpooja/entity_linking/mvd_env/bin/activate
pip install --quiet numpy==1.26.4 faiss-cpu prettytable termcolor colorama pytorch-transformers 2>&1 | tail -3

# Check torch
python -c "import torch; print(f'PyTorch {torch.__version__}, CUDA available: {torch.cuda.is_available()}')"

# Run benchmark
echo "[$(date)] Running BLINK benchmark..."
cd "$BLINK_CODE"
export PYTHONPATH="$BLINK_CODE:$PYTHONPATH"
export CUDA_VISIBLE_DEVICES="0"

python -u blink/run_benchmark.py 2>&1

echo "[$(date)] BLINK benchmark COMPLETE"

# Cleanup models from /tmp
echo "[$(date)] Cleaning up /tmp/blink_models..."
rm -rf "$MODELS_TMP"
rm -f "$BLINK_CODE/models/biencoder_wiki_large.bin"
rm -f "$BLINK_CODE/models/biencoder_wiki_large.json"
rm -f "$BLINK_CODE/models/crossencoder_wiki_large.bin"
rm -f "$BLINK_CODE/models/crossencoder_wiki_large.json"
rm -f "$BLINK_CODE/models/entity.jsonl"
rm -f "$BLINK_CODE/models/all_entities_large.t7"
rmdir "$BLINK_CODE/models" 2>/dev/null || true

echo "[$(date)] ALL DONE - cleaned up"
