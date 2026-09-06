#!/usr/bin/env bash
# Quick RAG Pipeline Deploy & Run (with full retriever fixes)

set -euo pipefail

# Ensure conda is available even in non-login shells
if ! command -v conda >/dev/null 2>&1; then
  if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    echo "Sourcing conda from $HOME/miniconda3/etc/profile.d/conda.sh"
    # shellcheck disable=SC1090
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
  elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    echo "Sourcing conda from $HOME/anaconda3/etc/profile.d/conda.sh"
    # shellcheck disable=SC1090
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
  elif [ -f "$HOME/mambaforge/etc/profile.d/conda.sh" ]; then
    echo "Sourcing conda from $HOME/mambaforge/etc/profile.d/conda.sh"
    # shellcheck disable=SC1090
    source "$HOME/mambaforge/etc/profile.d/conda.sh"
  else
    echo "ERROR: conda not found on PATH and no conda.sh discovered in common locations."
    exit 1
  fi
fi

if ! command -v conda >/dev/null 2>&1; then
  echo "ERROR: conda still not available after sourcing conda.sh"
  exit 1
fi

# This script:
# 1. Applies the retriever fix
# 2. Re-runs BELA candidate retrieval for NEWSEYE_FI
# 3. Runs RAG pipeline on both datasets
# 4. Generates improvement report

LLM_ENV=${LLM_ENV:-llm}
BELA_ENV=${BELA_ENV:-bela39}
BELA_DEVICE=${BELA_DEVICE:-cuda:0}
BELA_FALLBACK_DEVICE=${BELA_FALLBACK_DEVICE:-cpu}
BELA_BATCH_SIZE=${BELA_BATCH_SIZE:-2}
BELA_FALLBACK_BATCH_SIZE=${BELA_FALLBACK_BATCH_SIZE:-1}
RAG_DEVICE=${RAG_DEVICE:-cuda:0}
RAG_FALLBACK_DEVICE=${RAG_FALLBACK_DEVICE:-cpu}
AJMC_MODEL_ID_DEFAULT="mistralai/Mistral-Small-24B-Instruct-2501"
AJMC_MODEL_ID=${AJMC_MODEL_ID:-$AJMC_MODEL_ID_DEFAULT}
AJMC_FALLBACK_MODEL_ID=${AJMC_FALLBACK_MODEL_ID:-mistralai/Mistral-7B-Instruct-v0.3}
AJMC_MIN_GPU_MB_FOR_24B=${AJMC_MIN_GPU_MB_FOR_24B:-45000}
FORCE_AJMC_MODEL_ID=${FORCE_AJMC_MODEL_ID:-0}
FI_MODEL_ID=${FI_MODEL_ID:-LumiOpen/Llama-Poro-2-8B-Instruct}
FI_FALLBACK_MODEL_ID=${FI_FALLBACK_MODEL_ID:-LumiOpen/Llama-Poro-2-8B-Instruct}
GPU_MIN_FREE_MB=${GPU_MIN_FREE_MB:-4096}
GPU_MIN_RERANK_MB=${GPU_MIN_RERANK_MB:-1024}

echo "=== RAG Pipeline Deploy & Run ==="

# Prefer GPU only when there's enough free memory
if command -v nvidia-smi >/dev/null 2>&1; then
  free_mb=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n1 | tr -d ' ')
  if [ -n "$free_mb" ] && [ "$free_mb" -lt "$GPU_MIN_FREE_MB" ]; then
    echo "Low GPU free memory (${free_mb} MiB). Forcing CPU for BELA/RAG."
    BELA_DEVICE="$BELA_FALLBACK_DEVICE"
    MHEL_DEVICE_MAP="${MHEL_FALLBACK_DEVICE_MAP:-cpu}"
    MHEL_TORCH_DTYPE="${MHEL_FALLBACK_TORCH_DTYPE:-float32}"
  fi
  if [ -n "$free_mb" ] && [ "$free_mb" -lt "$GPU_MIN_RERANK_MB" ]; then
    RAG_DEVICE="$RAG_FALLBACK_DEVICE"
  fi
  if [ -n "$free_mb" ] && [ "$free_mb" -lt "$AJMC_MIN_GPU_MB_FOR_24B" ] && [ "$AJMC_MODEL_ID" = "$AJMC_MODEL_ID_DEFAULT" ] && [ "$FORCE_AJMC_MODEL_ID" != "1" ]; then
    echo "GPU free memory (${free_mb} MiB) below ${AJMC_MIN_GPU_MB_FOR_24B} MiB; switching AJMC model to fallback."
    AJMC_MODEL_ID="$AJMC_FALLBACK_MODEL_ID"
  fi
fi

# Step 1: Verify sentence-transformers is installed
conda run -n "$LLM_ENV" python -c "from sentence_transformers import CrossEncoder; print('✓ CrossEncoder available')"

# Step 2: Verify retriever fix is applied (check for valid_idx in get_candidates_batch)
if ! grep -q "valid_idx.*Index into results" src/retriever.py; then
  echo "ERROR: Retriever fix not applied. Check that retriever.py was uploaded."
  exit 1
fi
echo "✓ Retriever fix verified"

# Step 3: Clear old NEWSEYE_FI candidates to force re-retrieval
echo "Clearing old NEWSEYE_FI candidates to re-test with fixed retriever..."
rm -f results/NEWSEYE_FI/candidates_test_top*.json

# Step 4: Re-run BELA retrieval
echo "=== Retrieving candidates (BELA) ==="
if ! conda run -n "$BELA_ENV" python get_candidates.py \
  --dataset_path test_data/NEWSEYE_FI \
  --output_dir results/NEWSEYE_FI \
  --top_k 20 \
  --lang fi \
  --batch_size "$BELA_BATCH_SIZE" \
  --device "$BELA_DEVICE"; then
  echo "BELA retrieval failed on $BELA_DEVICE. Retrying on $BELA_FALLBACK_DEVICE..."
  conda run -n "$BELA_ENV" python get_candidates.py \
    --dataset_path test_data/NEWSEYE_FI \
    --output_dir results/NEWSEYE_FI \
    --top_k 20 \
    --lang fi \
    --batch_size "$BELA_FALLBACK_BATCH_SIZE" \
    --device "$BELA_FALLBACK_DEVICE"
fi

echo "✓ NEWSEYE_FI candidates retrieved successfully"

# Step 5: Run RAG pipeline
echo "=== Running RAG Pipeline ==="

# Memory caps for GPU contention (override by exporting in shell)
export MHEL_MAX_GPU_MEM="${MHEL_MAX_GPU_MEM:-6GiB}"
export MHEL_MAX_CPU_MEM="${MHEL_MAX_CPU_MEM:-120GiB}"
export MHEL_DEVICE_MAP="${MHEL_DEVICE_MAP:-auto}"
export MHEL_TORCH_DTYPE="${MHEL_TORCH_DTYPE:-bfloat16}"
export MHEL_OFFLOAD_FOLDER="${MHEL_OFFLOAD_FOLDER:-offload}"
export MHEL_FALLBACK_DEVICE_MAP="${MHEL_FALLBACK_DEVICE_MAP:-cpu}"
export MHEL_FALLBACK_TORCH_DTYPE="${MHEL_FALLBACK_TORCH_DTYPE:-float32}"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

if [ "$RAG_DEVICE" = "cpu" ] || [ "$MHEL_DEVICE_MAP" = "cpu" ]; then
  AJMC_MODEL_ID="$AJMC_FALLBACK_MODEL_ID"
  FI_MODEL_ID="$FI_FALLBACK_MODEL_ID"
fi

mkdir -p "$MHEL_OFFLOAD_FOLDER"

# Verify transformers
conda run -n "$LLM_ENV" python -c "from transformers import pipeline; print('✓ Transformers pipeline OK')"

# AJMC_EN
echo "Processing AJMC_EN..."
if ! conda run -n "$LLM_ENV" python filter_and_prompt_rag.py \
  --json_f results/AJMC_EN/candidates_test_top50_en.json \
  --dataset_path test_data/AJMC_EN \
  --output_dir results/AJMC_EN/rag_mistral_24B_k50_en \
  --n_candidates 20 \
  --model_id "$AJMC_MODEL_ID" \
  --threshold 0.5 \
  --device "$RAG_DEVICE" \
  --resume; then
  echo "RAG AJMC_EN failed on $RAG_DEVICE. Retrying on $RAG_FALLBACK_DEVICE (CPU)..."
  MHEL_DEVICE_MAP="$MHEL_FALLBACK_DEVICE_MAP" \
  MHEL_TORCH_DTYPE="$MHEL_FALLBACK_TORCH_DTYPE" \
  conda run -n "$LLM_ENV" python filter_and_prompt_rag.py \
    --json_f results/AJMC_EN/candidates_test_top50_en.json \
    --dataset_path test_data/AJMC_EN \
    --output_dir results/AJMC_EN/rag_mistral_24B_k50_en \
    --n_candidates 20 \
    --model_id "$AJMC_FALLBACK_MODEL_ID" \
    --threshold 0.5 \
    --device "$RAG_FALLBACK_DEVICE" \
    --resume
fi

conda run -n "$LLM_ENV" python eval.py --path_data test_data/AJMC_EN --path_results results/AJMC_EN/rag_mistral_24B_k50_en

# NEWSEYE_FI
echo "Processing NEWSEYE_FI..."
if ! conda run -n "$LLM_ENV" python filter_and_prompt_rag.py \
  --json_f results/NEWSEYE_FI/candidates_test_top20_fi.json \
  --dataset_path test_data/NEWSEYE_FI \
  --output_dir results/NEWSEYE_FI/rag_poro2_8B_k20_fi \
  --n_candidates 20 \
  --model_id "$FI_MODEL_ID" \
  --threshold 0.5 \
  --device "$RAG_DEVICE" \
  --resume; then
  echo "RAG NEWSEYE_FI failed on $RAG_DEVICE. Retrying on $RAG_FALLBACK_DEVICE (CPU)..."
  MHEL_DEVICE_MAP="$MHEL_FALLBACK_DEVICE_MAP" \
  MHEL_TORCH_DTYPE="$MHEL_FALLBACK_TORCH_DTYPE" \
  conda run -n "$LLM_ENV" python filter_and_prompt_rag.py \
    --json_f results/NEWSEYE_FI/candidates_test_top20_fi.json \
    --dataset_path test_data/NEWSEYE_FI \
    --output_dir results/NEWSEYE_FI/rag_poro2_8B_k20_fi \
    --n_candidates 20 \
    --model_id "$FI_FALLBACK_MODEL_ID" \
    --threshold 0.5 \
    --device "$RAG_FALLBACK_DEVICE" \
    --resume
fi

conda run -n "$LLM_ENV" python eval.py --path_data test_data/NEWSEYE_FI --path_results results/NEWSEYE_FI/rag_poro2_8B_k20_fi

# Step 6: Generate report
echo "=== Generating Improvement Report ==="
conda run -n "$LLM_ENV" python rag_eval_report.py

echo "✓✓✓ RAG Pipeline Complete ==="
echo "Results: rag_improvement_report.html"
echo "Log: rag_test.log (if running with |& tee rag_test.log)"
