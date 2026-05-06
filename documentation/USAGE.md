# Usage Guide - Running the Entity Linking Pipeline

## Quick Start Commands

### 1. Evaluate Results on Existing Output

```bash
cd Final Entity Linking/code

python eval.py \
  --path_data ../dataset/AJMC_EN \
  --path_results ../results/
```

**Output:** Metrics file with F1, Precision, Recall, Accuracy

### 2. Run Error Analysis

```bash
python error_analysis_summary.py \
  --path_results ../results/ \
  --output error_report.md
```

**Output:** Detailed FP/FN analysis with type and mention patterns

### 3. Train Confidence Router (XGBoost)

```bash
python train_xgb.py
```

**Output:** 
- `universal_xgb_threshold.json` - Trained model
- Routing accuracy metrics (82% on test set)
- Classification report with precision/recall

### 4. Rerank Candidates with Cross-Encoder

```bash
python rerank_only.py \
  --json_f ../results/candidates_test_top50_en.json \
  --dataset_path ../dataset/AJMC_EN \
  --output_dir ../results/rerank_baseline \
  --xencoder_model cross-encoder/ms-marco-MiniLM-L-6-v2 \
  --top_k 20
```

**Output:** `output.csv` with reranked predictions

## Detailed Parameter Reference

### eval.py
Compute evaluation metrics (F1, Precision, Recall, Accuracy)

**Parameters:**
- `--path_data`: Path to dataset directory
- `--path_results`: Path to results directory containing output.csv
- `--metrics_file`: Output file for metrics (default: result.txt)

**Example:**
```bash
python eval.py --path_data dataset/AJMC_EN --path_results results/ --metrics_file eval_metrics.txt
```

### error_analysis_summary.py
Analyze false positives, false negatives, and true positives

**Parameters:**
- `--path_results`: Path to results directory (contains fp_ed.csv, fn_ed.csv, tp_ed.csv, result.txt)
- `--output`: Output markdown file (default: error_summary.md)

**Example:**
```bash
python error_analysis_summary.py --path_results results/AJMC_EN --output error_analysis.md
```

**Output Includes:**
- FP/FN counts and top entity types
- Top mention patterns in errors
- Mention length statistics
- NIL prediction rate analysis

### train_xgb.py
Train XGBoost model for confidence-based routing

**Features Used:**
- Top-1 confidence score
- Confidence margin (top-1 vs top-2)
- Mention length
- Levenshtein distance to top candidate

**Output:**
- `universal_xgb_threshold.json` - Model weights
- Training/test accuracy reports
- Classification metrics (precision, recall, F1)

**Example:**
```bash
python train_xgb.py  # Trains on candidates in current directory
```

### rerank_only.py
Rerank candidates using cross-encoder model

**Parameters:**
- `--json_f`: Path to candidates JSON file
- `--dataset_path`: Path to dataset directory
- `--output_dir`: Output directory for results
- `--xencoder_model`: Cross-encoder model ID (default: cross-encoder/ms-marco-MiniLM-L-6-v2)
- `--top_k`: Top-K candidates to rerank (default: 20)
- `--batch_size`: Batch size (default: 8)
- `--context_window`: Context chars around mention (default: 50)
- `--no_context`: Disable context (flag)
- `--max_mentions`: Max mentions to process (default: all)

**Example:**
```bash
python rerank_only.py \
  --json_f results/candidates_test_top50_en.json \
  --dataset_path dataset/AJMC_EN \
  --output_dir results/rerank_output \
  --top_k 20 \
  --batch_size 16
```

**Output:**
- `output.csv` - Predictions in standard evaluation format
- `rerank.log` - Processing log with timing info

## End-to-End Pipeline Example

### Complete Workflow
```bash
# 1. Run error analysis on existing results
python error_analysis_summary.py --path_results results/ --output error_analysis.md

# 2. Train new confidence router
python train_xgb.py

# 3. Evaluate baseline metrics
python eval.py --path_data dataset/AJMC_EN --path_results results/

# 4. Optionally: Rerank candidates and evaluate
python rerank_only.py --json_f results/candidates_test_top50_en.json --dataset_path dataset/AJMC_EN --output_dir results/rerank_baseline
python eval.py --path_data dataset/AJMC_EN --path_results results/rerank_baseline
```

## Input/Output Formats

### Input: output.csv
```
doc_id,start_pos,end_pos,surface,gt_id,type,identifier,title,answer,score
```

### Input: candidates_test_top50_en.json
```json
{
  "mention_id": {
    "surface": "surface text",
    "paragraph": "context paragraph",
    "start_pos": 0,
    "end_pos": 5,
    "candidates": [
      {"entity_id": "wiki_id", "score": 0.95},
      {"entity_id": "wiki_id2", "score": 0.85}
    ]
  }
}
```

### Output: error_summary.md
- Markdown report with statistics
- FP/FN patterns and top entity types
- Mention length distributions
- NIL rate analysis

### Output: universal_xgb_threshold.json
- XGBoost model weights and thresholds
- Can be loaded for inference without retraining

## Performance Notes

- **eval.py**: ~1 second per 1k samples
- **error_analysis_summary.py**: ~2-5 seconds (depends on file size)
- **train_xgb.py**: ~30-60 seconds (18k training samples)
- **rerank_only.py**: ~1-2 min per 1k samples (batch_size=8)

## Troubleshooting

### "File not found" error
- Check path separators match your OS (/ for Linux/Mac, \\ for Windows)
- Use `pwd` and `ls` to verify directory structure
- Absolute paths work better than relative

### "Out of memory" error
- Reduce `--batch_size` (default 8 → try 2)
- Use `--top_k 5` instead of 20 for reranking
- Run on CPU: `--device cpu`

### Script hangs
- Check GPU/CPU load: `nvidia-smi` (GPU) or `top` (CPU)
- Set timeout: `--max_mentions 100` for testing
- Run with progress output: scripts use `tqdm` by default

## Next Steps

See `documentation/API.md` for detailed function-level documentation.
See `thesis/main.pdf` for theoretical background and results interpretation.
