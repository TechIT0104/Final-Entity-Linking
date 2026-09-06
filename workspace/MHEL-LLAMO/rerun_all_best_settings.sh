#!/usr/bin/env bash
set -euo pipefail

BELA_ENV_NAME=${BELA_ENV_NAME:-bela39}
LLM_ENV_NAME=${LLM_ENV_NAME:-llm}
DEVICE=${DEVICE:-cuda:0}
TOP_K=${TOP_K:-50}
BATCH_SIZE=${BATCH_SIZE:-4}
FORCE_CANDIDATES=${FORCE_CANDIDATES:-0}
SKIP_CANDIDATES=${SKIP_CANDIDATES:-0}
FORCE_LLM=${FORCE_LLM:-0}

if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found in PATH" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$(conda info --base)/etc/profile.d/conda.sh"

# Format: DATASET|LANG|SCRIPT|N_CAND|THRESHOLD_OR_EMPTY|MODEL_ID|RUN_NAME
RUNS=(
  "HIPE_DE|de|filter_and_prompt_chain.py|30|21.4|mistralai/Mistral-Small-24B-Instruct-2501|mistral_24B_chain_median_k30_de"
  "HIPE_EN|en|filter_and_prompt_chain.py|20||mistralai/Mistral-Small-24B-Instruct-2501|mistral_24B_chain_k20_en"
  "HIPE_FR|fr|filter_and_prompt.py|20||mistralai/Mistral-Small-24B-Instruct-2501|mistral_24B_van_k20_fr"

  "NEWSEYE_DE|de|filter_and_prompt_chain.py|30|25.0|mistralai/Mistral-Small-24B-Instruct-2501|mistral_24B_chain_k30_de"
  "NEWSEYE_FI|fi|filter_and_prompt_chain.py|20||LumiOpen/Llama-Poro-2-8B-Instruct|poro2_8B_chain_k20_fi"
  "NEWSEYE_FR|fr|filter_and_prompt_chain.py|20|21.35|mistralai/Mistral-Small-24B-Instruct-2501|mistral_24B_chain_median_k20_fr"
  "NEWSEYE_SV|sv|filter_and_prompt_chain.py|20|25.0|google/gemma-3-27b-it|gemma_27B_chain_median_k20_sv"

  "AJMC_DE|de|filter_and_prompt.py|50|21.5|mistralai/Mistral-Small-24B-Instruct-2501|mistral_24B_van_k50_de"
  "AJMC_EN|en|filter_and_prompt.py|50||mistralai/Mistral-Small-24B-Instruct-2501|mistral_24B_van_k50_en"
  "AJMC_FR|fr|filter_and_prompt.py|20||mistralai/Mistral-Small-24B-Instruct-2501|mistral_24B_van_k20_fr"

  "MHERCL_EN|en|filter_and_prompt_chain.py|20||mistralai/Mistral-Small-24B-Instruct-2501|mistral_24B_chain_k20_en"
  "MHERCL_IT|it|filter_and_prompt_chain.py|20||mistralai/Mistral-Small-24B-Instruct-2501|mistral_24B_chain_k20_it"
)

mkdir -p results

if [[ "$SKIP_CANDIDATES" != "1" ]]; then
  echo "=== Candidate retrieval (BELA) ==="
  conda activate "$BELA_ENV_NAME"

  for row in "${RUNS[@]}"; do
    IFS='|' read -r dataset lang _script _n_cand _thr _model run_name <<<"$row"

    dataset_path="test_data/${dataset}"
    if [[ "$dataset" == "MHERCL_IT" ]]; then
      dataset_path="test_data/MHERCL_it"
    fi

    out_dir="results/${dataset}"
    mkdir -p "$out_dir"

    cand_path="$out_dir/candidates_test_top${TOP_K}_${lang}.json"
    if [[ ! -f "$cand_path" || "$FORCE_CANDIDATES" == "1" ]]; then
      echo "Retrieving candidates for $dataset ($lang) -> $cand_path"
      python ./get_candidates.py --dataset_path "$dataset_path" --output_dir "$out_dir" --top_k "$TOP_K" --lang "$lang" --batch_size "$BATCH_SIZE" --device "$DEVICE"
    else
      echo "Candidates exist for $dataset ($lang); skipping"
    fi
  done
fi

echo "=== LLM prompting + evaluation ==="
conda activate "$LLM_ENV_NAME"

# Helpful for fragmentation-related OOMs on long runs (safe default on newer torch).
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}

# Preflight: transformers pipeline must import cleanly. If torchvision is installed but broken,
# text-generation will crash at import time. Uninstalling torchvision typically fixes it.
python - <<'PY'
try:
  import transformers
  from transformers import pipeline
  print('transformers', transformers.__version__)
  print('pipeline import OK')
except Exception as e:
  print('FATAL: transformers/pipeline import failed:', repr(e))
  print('If you see torchvision::nms errors, uninstall torchvision in this env:')
  print('  pip uninstall -y torchvision || true')
  print('  conda remove -y torchvision || true')
  raise
PY

for row in "${RUNS[@]}"; do
  IFS='|' read -r dataset lang script n_cand thr model run_name <<<"$row"

  dataset_path="test_data/${dataset}"
  if [[ "$dataset" == "MHERCL_IT" ]]; then
    dataset_path="test_data/MHERCL_it"
  fi

  dataset_results_dir="results/${dataset}"
  cand_path="$dataset_results_dir/candidates_test_top${TOP_K}_${lang}.json"
  if [[ ! -f "$cand_path" ]]; then
    echo "Missing candidates file: $cand_path" >&2
    exit 1
  fi

  run_dir="$dataset_results_dir/$run_name"
  mkdir -p "$run_dir"

  # Resume at the run-folder level: if output already exists, do not redo LLM unless forced.
  if [[ "$FORCE_LLM" != "1" && -f "$run_dir/output.csv" ]]; then
    echo "output.csv exists for $dataset/$run_name; skipping LLM (set FORCE_LLM=1 to rerun)"
  else

    echo "Running $dataset/$run_name using $script"
    args=(
      "./$script"
      --json_f "$cand_path"
      --dataset_path "$dataset_path"
      --output_dir "$run_dir"
      --n_candidates "$n_cand"
      --model_id "$model"
      --resume
    )
    if [[ -n "$thr" ]]; then
      args+=(--threshold "$thr")
    fi
    python "${args[@]}"
  fi

  echo "Evaluating $dataset/$run_name"
  python ./eval.py --path_data "$dataset_path" --path_results "$run_dir"

done

echo "=== Honest comparison tables ==="
python ./honest_eval_report.py

echo "DONE"
