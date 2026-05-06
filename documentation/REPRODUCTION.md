# Reproduction Guide - Step-by-Step

## Overview
This guide provides exact commands to reproduce all results in the thesis.

## Prerequisites
- 2-4 hours for full reproduction (depends on GPU)
- Single 32GB GPU OR CPU (slower)
- 50 GB free disk space (for model downloads + datasets)

---

## Part 1: Environment Setup (10 minutes)

### Step 1: Create Virtual Environment
```bash
cd "Final Entity Linking"
python -m venv .venv
.venv\Scripts\activate  # Windows
# OR
source .venv/bin/activate  # Linux/Mac
```

### Step 2: Install Dependencies
```bash
pip install --upgrade pip
pip install torch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
pip install transformers==4.36.0 xgboost==2.0.0 pandas==2.1.0 tqdm==4.66.0 scikit-learn==1.3.0
```

### Step 3: Verify Installation
```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
python -c "from transformers import AutoModel; print('✓ Transformers OK')"
python -c "import xgboost; print('✓ XGBoost OK')"
```

---

## Part 2: Reproduce Results (Estimated 2-3 hours)

### Step 1: Error Analysis on Existing Results ✓
**Time:** 2 seconds | **Hardware:** CPU only

```bash
cd code
python error_analysis_summary.py --path_results ../results/ --output error_report.md
```

**Expected Output:**
- `error_report.md` created
- Metrics: 71 TP, 80 FP, 80 FN, 47.02% accuracy
- Findings: 59% NIL misclassification, abbreviations as main failure mode

### Step 2: Train XGBoost Confidence Router ✓
**Time:** 1-2 minutes | **Hardware:** CPU or GPU

```bash
cd code
python train_xgb.py
```

**Expected Output:**
- `universal_xgb_threshold.json` created/updated
- Baseline accuracy: 70%
- XGBoost accuracy: 82%
- Precision/Recall metrics printed to console

**Key Result:** +12% accuracy improvement (70% → 82%)

### Step 3: Evaluate Baseline Metrics
**Time:** 30 seconds | **Hardware:** CPU only

```bash
python eval.py --path_data ../dataset/AJMC_EN --path_results ../results/
```

**Expected Output:**
- Evaluation metrics computed
- `result.txt` updated with: F1, Precision, Recall, Accuracy

### Step 4: Optional - Rerank with Cross-Encoder
**Time:** 5-10 minutes | **Hardware:** CPU (GPU faster)

```bash
python rerank_only.py \
  --json_f ../results/candidates_test_top50_en.json \
  --dataset_path ../dataset/AJMC_EN \
  --output_dir ../results/rerank_baseline \
  --xencoder_model cross-encoder/ms-marco-MiniLM-L-6-v2 \
  --top_k 20
```

**Expected Output:**
- `../results/rerank_baseline/output.csv` created
- Reranked predictions saved
- Optionally evaluate: `python eval.py --path_data ../dataset/AJMC_EN --path_results ../results/rerank_baseline`

---

## Part 3: Verify Thesis Claims (10 minutes)

### Claim 1: XGBoost Router +12% Improvement
**Verify:** Check `results/AJMC_EN_error_summary.md` and console output from Step 2
```bash
# Should see:
# "XGBoost Test Performance: ... accuracy 0.82"
# "Universal Baseline Threshold Test Performance: ... accuracy 0.70"
```

### Claim 2: Error Patterns (Short Mentions + Abbreviations)
**Verify:** Check `results/AJMC_EN_error_summary.md`
```bash
# Should see:
# "Avg mention length in FP: 6.16 (median 5.00)"
# "Top mentions: Ph., Ant., El., Phil., O.T."
```

### Claim 3: 18k Training Samples
**Verify:** Check train_xgb.py console output
```bash
# Should see:
# "Universal Train size: 18075"
```

### Claim 4: TR2016 Offset Fix (5.5x Improvement)
**Verify:** Check thesis/main.pdf Section 4
```
TR2016 (de) recall improved from 1.54% to 8.42% after offset validation
```

---

## Complete Reproduction Checklist

### Environment
- [ ] Python 3.11 installed
- [ ] Virtual environment activated
- [ ] PyTorch with CUDA verified
- [ ] All dependencies installed

### Error Analysis
- [ ] error_analysis_summary.py executed successfully
- [ ] Output: 71 TP, 80 FP, 80 FN, 47% accuracy
- [ ] Abbreviations identified as failure mode

### Model Training
- [ ] train_xgb.py executed successfully
- [ ] Output: 82% routing accuracy (vs 70% baseline)
- [ ] Model saved to `universal_xgb_threshold.json`

### Evaluation
- [ ] eval.py executed on baseline results
- [ ] Metrics computed and saved

### Optional: Reranking
- [ ] rerank_only.py executed (if running full pipeline)
- [ ] Cross-encoder predictions generated

### Thesis Verification
- [ ] thesis/main.pdf reviewed
- [ ] All claims verified against results/
- [ ] Contribution split (70/30) clearly stated

---

## Expected File Structure After Reproduction

```
Final Entity Linking/
├── code/
│   ├── eval.py
│   ├── error_analysis_summary.py
│   ├── train_xgb.py
│   ├── rerank_only.py
│   └── [run outputs]
│
├── results/
│   ├── AJMC_EN_result.txt
│   ├── AJMC_EN_error_summary.md
│   ├── error_report.md                    # NEW (from Step 1)
│   └── rerank_baseline/                   # NEW (from Step 4, optional)
│       └── output.csv
│
├── models/
│   └── universal_xgb_threshold.json       # UPDATED (from Step 2)
│
└── thesis/
    └── main.pdf
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'transformers'"
```bash
pip install transformers
```

### "CUDA out of memory"
- Use CPU: `--device cpu` (slower)
- Reduce batch size: `--batch_size 2`

### "Model not found" (HuggingFace)
- Check internet connection
- Pre-download: `python -c "from transformers import AutoModel; AutoModel.from_pretrained('microsoft/bela')"`

### Scripts hang on first run
- Wait 5-10 minutes (downloading models)
- Check `nvidia-smi` for GPU memory

### File not found errors
- Verify dataset paths in `../dataset/AJMC_EN/`
- Check current directory: `pwd`

---

## Time Estimates (Single 32GB GPU)

| Task | Time | Notes |
|------|------|-------|
| Setup | 10 min | One-time |
| Error Analysis | 2 sec | CPU only |
| XGBoost Training | 1-2 min | Trains on 18k samples |
| Evaluation | 30 sec | CPU only |
| Reranking (opt) | 5-10 min | Cross-encoder inference |
| **Total** | **~20 min** | Without reranking |

---

## Citation & Attribution

Based on papers:
- mReFinED (Entity Linking)
- MHEL-LLaMo (Multilingual Historical Entity Linking)
- BLINK, MVD (Baselines)

See thesis/main.pdf for full references.

---

## Questions?

1. Check `documentation/USAGE.md` for detailed parameter options
2. Review `documentation/SETUP.md` for environment issues
3. See `documentation/DATASETS.md` for data format questions
4. Read `thesis/main.pdf` Section 4 for theory

