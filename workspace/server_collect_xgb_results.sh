#!/bin/bash
# server_collect_xgb_results.sh
# Run on server to test MEWSLI XGB, capture outputs, and bundle for download

set -e

cd ~/MHEL-LLAMO

echo "=========================================="
echo "Starting MEWSLI XGB test & artifact collection"
echo "=========================================="

# Try to activate environment (adjust if using different env name)
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

# Check for python3 or python
PYTHON_CMD="python3"
if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD="python"
fi

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "ERROR: Python not found in PATH"
    echo "Trying conda run method..."
    # Will use conda run below
    PYTHON_CMD="conda run -n llm python"
fi

# Verify Python
$PYTHON_CMD --version

echo ""
echo "========== Installing dependencies =========="
$PYTHON_CMD -m pip install xgboost python-Levenshtein --quiet

echo ""
echo "========== Test 1: Train XGBoost (universal) =========="
$PYTHON_CMD train_xgb.py | tee train_xgb_output.txt

echo ""
echo "========== Test 2: Test MEWSLI XGB =========="
$PYTHON_CMD test_mewsli_xgb.py | tee test_mewsli_xgb_output.txt

echo ""
echo "========== Collecting artifacts =========="

# Create bundle directory
BUNDLE_DIR="/tmp/mhel_xgb_results_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BUNDLE_DIR"

# Copy outputs
cp train_xgb_output.txt "$BUNDLE_DIR/"
cp test_mewsli_xgb_output.txt "$BUNDLE_DIR/"

# Copy XGB model and candidate files
cp universal_xgb_threshold.json "$BUNDLE_DIR/"
cp results/MEWSLI_EN/candidates_test_top50_en.json "$BUNDLE_DIR/"

# Create archive in home directory
TAR_FILE="mhel_xgb_results_$(date +%Y%m%d_%H%M%S).tar.gz"
tar czf ~/"$TAR_FILE" -C /tmp "$(basename $BUNDLE_DIR)"

echo ""
echo "========== Results Ready =========="
echo "Archive created: ~/$TAR_FILE"
echo ""
echo "Download with:"
echo "  scp kmpooja@172.20.70.80:~/$TAR_FILE ."
echo ""
echo "Contents:"
tar tzf ~/"$TAR_FILE" | head -20

echo ""
echo "Done!"
