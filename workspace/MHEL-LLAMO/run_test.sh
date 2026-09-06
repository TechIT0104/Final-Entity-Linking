#!/bin/bash

# Initialize conda
source ~/miniconda3/etc/profile.d/conda.sh

# MHEL-LLAMO Complete Pipeline Test Script
# This script runs the full pipeline on a test dataset with Mistral-8B

set -e  # Exit on error

DATASET="HIPE_EN"
LANG="en"
TOP_K=20
N_CANDIDATES=20
MODEL_ID="mistralai/Ministral-8B-Instruct-2410"

echo "================================"
echo "MHEL-LLAMO Pipeline Test"
echo "================================"
echo "Dataset: $DATASET"
echo "Language: $LANG"
echo "Model: $MODEL_ID"
echo "Top K candidates: $TOP_K"
echo "N candidates for LLM: $N_CANDIDATES"
echo "================================"
echo ""

PROJECT_DIR="$HOME/MHEL-LLAMO"
cd "$PROJECT_DIR"

# ============================================
# STEP 1: BELA Candidate Retrieval
# ============================================
echo "[STEP 1/3] Running BELA Candidate Retrieval..."
echo "Command: python get_candidates.py --dataset_path ./test_data/$DATASET --output_dir ./results/$DATASET --top_k $TOP_K --lang $LANG"
echo ""

conda activate bela310

python get_candidates.py \
  --dataset_path "./test_data/$DATASET" \
  --output_dir "./results/$DATASET" \
  --top_k $TOP_K \
  --lang $LANG

echo ""
echo "✓ Step 1 complete. Candidates saved to: results/$DATASET/candidates_test_top${TOP_K}_${LANG}.json"
echo ""

# ============================================
# STEP 2: LLM Filtering & Selection
# ============================================
echo "[STEP 2/3] Running LLM Filtering and Candidate Selection..."
echo "Model: $MODEL_ID"
echo ""

conda activate llm310

# Determine if threshold is needed for this dataset
THRESHOLD_ARG=""
case $DATASET in
  HIPE_DE)
    THRESHOLD_ARG="--threshold 21.4"
    ;;
  NEWSEYE_DE)
    THRESHOLD_ARG="--threshold 25"
    ;;
  NEWSEYE_FR)
    THRESHOLD_ARG="--threshold 21.35"
    ;;
  NEWSEYE_SV)
    THRESHOLD_ARG="--threshold 25"
    ;;
esac

python filter_and_prompt_chain.py \
  --json_f "results/$DATASET/candidates_test_top${TOP_K}_${LANG}.json" \
  --dataset_path "./test_data/$DATASET" \
  --output_dir "./results/$DATASET" \
  --n_candidates $N_CANDIDATES \
  --model_id "$MODEL_ID" \
  $THRESHOLD_ARG

echo ""
echo "✓ Step 2 complete. LLM predictions saved to: results/$DATASET/"
echo ""

# ============================================
# STEP 3: Evaluate Results
# ============================================
echo "[STEP 3/3] Evaluating Results..."
echo ""

python eval.py \
  --path_data "./test_data/$DATASET" \
  --path_results "./results/$DATASET"

echo ""
echo "================================"
echo "✓ Pipeline Complete!"
echo "================================"
echo ""
echo "Results saved in: results/$DATASET/"
echo ""
echo "Next steps:"
echo "  1. Check results/$DATASET/ for output files"
echo "  2. Review the F1/Precision/Recall metrics above"
echo "  3. Try with other datasets or models"
echo ""
