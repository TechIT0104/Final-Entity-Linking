#!/usr/bin/env bash
set -euo pipefail

# RAG Pipeline Test Harness
# Runs the enhanced RAG pipeline on 1-2 small datasets,
# measures improvement, and generates a report.

BELA_ENV_NAME=${BELA_ENV_NAME:-bela39}
LLM_ENV_NAME=${LLM_ENV_NAME:-llm}
DEVICE=${DEVICE:-cuda:0}
BATCH_SIZE=${BATCH_SIZE:-4}

# Env vars for memory caps (optional)
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}

if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found in PATH" >&2
  exit 1
fi

source "$(conda info --base)/etc/profile.d/conda.sh"

echo "=== RAG Pipeline Test ==="

# Datasets to test (small = fast)
# AJMC_EN: 156 mentions (smallest)
# NEWSEYE_FI: 654 mentions (small, low baseline coverage)
DATASETS=(
  "AJMC_EN|en|mistralai/Mistral-Small-24B-Instruct-2501|50"
  "NEWSEYE_FI|fi|LumiOpen/Llama-Poro-2-8B-Instruct|20"
)

echo "=== Candidate Retrieval (BELA) ==="
conda activate "$BELA_ENV_NAME"

for row in "${DATASETS[@]}"; do
  IFS='|' read -r dataset lang model n_cand <<<"$row"

  dataset_path="test_data/${dataset}"
  out_dir="results/${dataset}"
  mkdir -p "$out_dir"

  lang_code=$(echo "$lang" | cut -c1-2)
  cand_path="$out_dir/candidates_test_top${n_cand}_${lang_code}.json"

  if [[ ! -f "$cand_path" ]]; then
    echo "Retrieving candidates for $dataset ($lang)"
    python ./get_candidates.py \
      --dataset_path "$dataset_path" \
      --output_dir "$out_dir" \
      --top_k "$n_cand" \
      --lang "$lang_code" \
      --batch_size "$BATCH_SIZE" \
      --device "$DEVICE"
  else
    echo "Candidates exist for $dataset; skipping"
  fi
done

echo "=== RAG Pipeline Execution ==="
conda activate "$LLM_ENV_NAME"

# Verify transformers import
python - <<'PY'
try:
  import transformers
  from transformers import pipeline
  print('transformers', transformers.__version__)
  print('pipeline import OK')
except Exception as e:
  print('FATAL: transformers/pipeline import failed:', repr(e))
  raise
PY

for row in "${DATASETS[@]}"; do
  IFS='|' read -r dataset lang model n_cand <<<"$row"

  dataset_path="test_data/${dataset}"
  lang_code=$(echo "$lang" | cut -c1-2)
  
  out_dir="results/${dataset}"
  cand_path="$out_dir/candidates_test_top${n_cand}_${lang_code}.json"
  
  # Output folder for RAG results
  rag_run_dir="$out_dir/rag_${model##*/}_k${n_cand}_${lang_code}"
  mkdir -p "$rag_run_dir"

  echo "Running RAG for $dataset/$rag_run_dir"
  
  python ./filter_and_prompt_rag.py \
    --json_f "$cand_path" \
    --dataset_path "$dataset_path" \
    --output_dir "$rag_run_dir" \
    --n_candidates "$n_cand" \
    --model_id "$model" \
    --threshold 0.5 \
    --device "$DEVICE" \
    --resume

  echo "Evaluating $dataset with RAG results"
  python ./eval.py --path_data "$dataset_path" --path_results "$rag_run_dir"
done

echo "=== Generating Improvement Report ==="
python ./rag_eval_report.py

echo "DONE: RAG Pipeline Test Complete"
echo "Check: rag_improvement_report.html for results"
