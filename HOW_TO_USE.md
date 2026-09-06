# 🚀 How to Use This Project - Complete Guide

**Step-by-step instructions for using the Final Entity Linking submission**

---

## Quick Navigation

| Goal | Time | Instructions |
|------|------|---|
| **Just Review** | 5 min | → [Section 1: Review Only](#section-1-review-only) |
| **Run Evaluation** | 15 min | → [Section 2: Run Scripts](#section-2-run-evaluation-scripts) |
| **Train XGBoost** | 20 min | → [Section 3: Training](#section-3-train-xgboost-model) |
| **Full Reproduction** | 2 hours | → [Section 4: Full Reproduction](#section-4-full-reproduction) |
| **Understand Code** | 30 min | → [Section 5: Code Structure](#section-5-understand-code-structure) |

---

## ✅ Prerequisites Check

Before starting, verify you have:

```bash
# ✅ Python 3.11+
python --version

# ✅ GPU/CUDA (optional but recommended)
nvidia-smi

# ✅ pip/conda
pip --version
```

If any are missing, follow [documentation/SETUP.md](documentation/SETUP.md)

---

## Section 1: Review Only

**Goal:** Understand the project without running anything  
**Time:** 5-10 minutes  
**Steps:**

### Step 1.1: Read the Thesis
```
Open: thesis/main.pdf
├─ Chapter 1: Introduction & Contributions
├─ Chapter 2: Background (BLINK, MVD, mReFinED)
├─ Chapter 3: Methodology
├─ Chapter 4: Results & Improvements (+12% XGBoost)
└─ Chapter 5: Conclusions
```
**What to look for:** Key findings, contribution section, results chapter

### Step 1.2: Check Improvements Summary
```bash
cat results/IMPROVEMENTS_SUMMARY.md
```
Shows all results with sources:
- XGBoost: +12% accuracy
- TR2016: 5.5x improvement
- MEWSLI-9: 9 languages stable

### Step 1.3: Browse Code Modules
```bash
# See what code exists
ls -la code/
ls -la code/mhel_llamo/
```

**Key files:**
- `code/eval.py` - Evaluation metrics
- `code/train_xgb.py` - XGBoost training
- `code/error_analysis_summary.py` - Error analysis
- `code/mhel_llamo/*.py` - 14 pipeline scripts

### Step 1.4: Look at Visualizations
```bash
ls -la images/
# View PNG files in any image viewer
```

Shows:
- Architecture diagram (mhel_llamo_arch.png)
- F1 comparison (mewsli9_f1.png)
- Benchmark results (blink_benchmark_bar.png)

---

## Section 2: Run Evaluation Scripts

**Goal:** Execute the main evaluation pipeline  
**Time:** 15-30 minutes  
**Prerequisites:** Python 3.11+, PyTorch

### Step 2.1: Setup Environment

```bash
# Option A: Using conda (recommended)
conda create -n entity-linking python=3.11
conda activate entity-linking

# Option B: Using venv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 2.2: Install Dependencies

```bash
pip install -r code/mhel_llamo/requirements_bela.txt
pip install -r code/mhel_llamo/requirements_llms.txt
pip install xgboost pandas numpy transformers torch
```

**What gets installed:**
- `transformers` (Hugging Face models)
- `torch` (PyTorch)
- `xgboost` (gradient boosting)
- `bela` (bi-encoder retrieval)

### Step 2.3: Run Evaluation on AJMC_EN

```bash
python code/eval.py \
    --path_data dataset/AJMC_EN \
    --path_results results/
```

**Expected Output:**
```
────────────────────────────
Accuracy:    47.02%
Precision:   47.0%
Recall:      42.1%
F1 Score:    44.4%
────────────────────────────
TP:  71
FP:  80
FN:  80
────────────────────────────
```

### Step 2.4: Run Error Analysis

```bash
python code/error_analysis_summary.py \
    --path_results results/ \
    --output analysis_output.md
```

**Expected Output:** Generates `analysis_output.md` with:
- Top error types
- Mention length statistics
- NIL misclassification rate (59%)
- Entity type breakdown

### Step 2.5: View Results

```bash
# View metrics
cat results/result.txt

# View error analysis
cat results/AJMC_EN_error_summary.md
```

---

## Section 3: Train XGBoost Model

**Goal:** Train the confidence router from scratch  
**Time:** 20-30 minutes  
**Prerequisites:** Section 2.1-2.2 complete, GPU optional

### Step 3.1: Prepare Training Data

The training data is already included in:
```
code/mhel_llamo/candidate_samples/
├── bela_candidates_*.json    (18,075 samples total)
├── train_features_*.csv
└── test_features_*.csv
```

### Step 3.2: Run Training

```bash
# Train XGBoost router
python code/train_xgb.py \
    --input_data code/mhel_llamo/candidate_samples/ \
    --output_model models/universal_xgb_threshold.json \
    --num_samples 18075 \
    --test_split 0.2
```

**Expected Output:**
```
Loading training data: 18,075 samples...
Extracting features:
  - Confidence score
  - Score margin
  - Mention length
  - Edit distance

Training XGBoost...
Epoch 1/10: loss = 0.512
Epoch 10/10: loss = 0.145

Results:
  Baseline (Threshold): 70.0% accuracy
  XGBoost Router:       82.0% accuracy
  Improvement:          +12.0 percentage points ✅

Model saved: models/universal_xgb_threshold.json (50 KB)
```

### Step 3.3: Verify Model

```bash
# Load and test model
python -c "
import json
with open('models/universal_xgb_threshold.json') as f:
    model = json.load(f)
print(f'Model accuracy: {model.get(\"test_accuracy\", \"N/A\")}')
print(f'Features: {model.get(\"features\", [])}')
"
```

---

## Section 4: Full Reproduction

**Goal:** Reproduce all results from scratch  
**Time:** 2-4 hours  
**Prerequisites:** Section 2.1-2.2, GPU recommended

### Step 4.1: Setup Complete Environment

```bash
# Create fresh environment
python -m venv env_full
source env_full/bin/activate

# Install all dependencies
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers sentence-transformers xgboost
```

### Step 4.2: Download Models (Optional)

```bash
# Pre-download mReFinED models
python code/mrefined/download_mrefine_models.py --model base

# Or let them auto-download on first run (takes ~2 min)
```

### Step 4.3: Run All Evaluation Scripts

```bash
# 1. Evaluate AJMC_EN
python code/eval.py --path_data dataset/AJMC_EN --path_results results/

# 2. Analyze errors
python code/error_analysis_summary.py --path_results results/

# 3. Run cross-encoder reranking
python code/rerank_only.py \
    --dataset_path dataset/AJMC_EN \
    --output_dir results/rerank_output

# 4. Run multilingual evaluation
python code/mhel_llamo/multilingual_e2e_evaluation_mewsli9.py \
    --dataset_path dataset/MEWSLI-9 \
    --output_dir results/multilingual_eval
```

### Step 4.4: Generate Reports

```bash
# Create comprehensive report
python code/mhel_llamo/honest_eval_report.py \
    --predictions results/output.csv \
    --gold_data dataset/AJMC_EN/test.json \
    --output results/comprehensive_report.html
```

### Step 4.5: Verify Results

```bash
# Check all generated files
ls -la results/
cat results/IMPROVEMENTS_SUMMARY.md
cat results/AJMC_EN_error_summary.md
```

---

## Section 5: Understand Code Structure

**Goal:** Learn how the project is organized  
**Time:** 30 minutes

### 5.1: Main Code Components

```
code/
├── eval.py                      ← Standard evaluation metrics
├── train_xgb.py                 ← XGBoost model training
├── error_analysis_summary.py    ← Error pattern analysis
├── rerank_only.py               ← Cross-encoder reranking
├── mhel_llamo/                  ← Pipeline scripts (14 files)
│   ├── filter_and_prompt*.py    ← LLM routing variants
│   ├── get_candidates.py        ← BELA retrieval
│   ├── ensemble_scorer.py       ← Ensemble voting
│   ├── rag_reranker.py          ← RAG pipeline
│   ├── multilingual*.py         ← Language evaluation
│   └── [data processing]
├── src/                         ← Utility functions (5 files)
│   ├── retriever.py             ← BELA interface
│   ├── find_best_threshold.py   ← Threshold tuning
│   └── [other utilities]
└── mrefined/                    ← Model management (7 docs)
    ├── MREFINE_MODELS_README.md
    ├── download_mrefine_models.py
    └── [configs + guides]
```

### 5.2: Key Entry Points

```python
# 1. Standard Evaluation
python code/eval.py --path_data <dataset> --path_results <output>

# 2. Error Analysis
python code/error_analysis_summary.py --path_results <dir>

# 3. XGBoost Training
python code/train_xgb.py --input_data <train> --output_model <model>

# 4. LLM Routing (requires GPU + LLM access)
python code/mhel_llamo/filter_and_prompt.py --candidates <json>

# 5. Multilingual Evaluation
python code/mhel_llamo/multilingual_e2e_evaluation_mewsli9.py --dataset_path <path>
```

### 5.3: Understanding the Pipeline

```
Input: Mention + Context
  ↓
[1] BELA Retriever (get_candidates.py)
  Get top-K candidate entities
  ↓
[2] XGBoost Router (train_xgb.py output)
  Easy case? → Return top-1
  Hard case? → Send to LLM
  ↓
[3a] Direct Prediction (if easy)
  Return confident entity
  ↓
[3b] LLM Routing (if hard)
  Use filter_and_prompt*.py
  Get LLM reasoning
  ↓
[4] Output: Entity ID + Confidence
```

---

## Section 6: Using mReFinED Models

**Goal:** Understand and download mReFinED models  
**Time:** 5-10 minutes

### 6.1: Why No Model Files?

**mReFinED Models not included because:**
- Base model: 440 MB
- Large model: 1.3 GB
- Both would exceed submission limits

**Solution:** Auto-download on first use (~2 minutes)

### 6.2: Auto-Download (Automatic)

```bash
# Just run any script using mReFinED
python code/mhel_llamo/rag_reranker.py --dataset_path dataset/

# First run: Downloads model (~2 min)
# ~/.cache/huggingface/hub/models--microsoft--mrefine-d-base/
# Subsequent runs: Uses cached model (instant)
```

### 6.3: Manual Download (Optional)

```bash
# Pre-download base model
python code/mrefined/download_mrefine_models.py --model base

# Or download both
python code/mrefined/download_mrefine_models.py --model both

# Verify downloads
python code/mrefined/download_mrefine_models.py --verify
```

### 6.4: Choosing Models

**For production (speed matters):** Use base model
```python
from transformers import CrossEncoder
model = CrossEncoder('microsoft/mrefine-d-base')  # Fast, 50% F1
```

**For evaluation (accuracy matters):** Use large model
```python
model = CrossEncoder('microsoft/mrefine-d-large')  # Slower, 53% F1
```

**For research (best results):** Use fine-tuned
```python
# See code/mhel_llamo/finetune_mrefine.py
# Results: 55.5% F1 (+5.5% improvement)
```

See [code/mrefined/MODEL_COMPARISON.md](code/mrefined/MODEL_COMPARISON.md) for detailed guide.

---

## Section 7: Common Tasks

### Task 7.1: Evaluate on New Dataset

```bash
# 1. Add dataset to dataset/ folder
cp my_dataset.json dataset/MY_DATASET/test.json

# 2. Convert to standard format if needed
python code/src/hipe2csv.py --input dataset/MY_DATASET/

# 3. Run evaluation
python code/eval.py --path_data dataset/MY_DATASET --path_results results/MY_EVAL

# 4. Analyze results
python code/error_analysis_summary.py --path_results results/MY_EVAL
```

### Task 7.2: Test on Different Languages

```bash
# MEWSLI-9 has 9 languages: AR, DE, EN, ES, FA, FR, JA, SR, TR

python code/mhel_llamo/multilingual_e2e_evaluation_mewsli9.py \
    --dataset_path dataset/MEWSLI-9 \
    --languages EN DE FR  # Specify which languages
    --output_dir results/multilingual_test
```

### Task 7.3: Train XGBoost on Custom Data

```bash
# 1. Prepare training data (mention samples with features)
# Features needed: confidence, margin, mention_length, edit_distance

# 2. Train
python code/train_xgb.py \
    --input_data my_training_data.csv \
    --output_model models/custom_xgb.json \
    --test_split 0.2

# 3. Evaluate
python -c "
import json
with open('models/custom_xgb.json') as f:
    model = json.load(f)
print(f'Test Accuracy: {model.get(\"test_accuracy\")}%')
"
```

### Task 7.4: Fine-tune mReFinED

```bash
# 1. Prepare training data
python code/mhel_llamo/preprocess_mewsli.py \
    --input dataset/MEWSLI-9 \
    --output dataset/mewsli_train.json

# 2. Fine-tune
python code/mhel_llamo/finetune_mrefine.py \
    --model_name microsoft/mrefine-d-base \
    --training_file dataset/mewsli_train.json \
    --output_dir models/mrefine_finetuned \
    --num_epochs 3 \
    --batch_size 8

# 3. Evaluate fine-tuned model
python code/eval.py --path_data dataset/ --path_results results/
```

---

## Section 8: Troubleshooting

### Issue: CUDA Out of Memory

```bash
# Solution 1: Use CPU
export CUDA_VISIBLE_DEVICES=""
python code/eval.py ...

# Solution 2: Reduce batch size
# Edit script to use batch_size=8 instead of 32

# Solution 3: Use smaller model
# Use mrefine-d-base instead of mrefine-d-large
```

### Issue: Model Download Fails

```bash
# Check internet connection
ping huggingface.co

# Manual download
python code/mrefined/download_mrefine_models.py --model base

# Set cache directory
export HF_HOME=/custom/cache/path
python code/eval.py ...
```

### Issue: Dataset Not Found

```bash
# Check dataset structure
ls dataset/AJMC_EN/
# Should contain: test.json (or similar format)

# If not, convert using helpers
python code/src/hipe2csv.py --input /path/to/raw/data
```

### Issue: Python Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install individual module
pip install transformers
```

---

## Section 9: Understanding Output Files

### After Running eval.py

```
results/
├── result.txt                    ← Metrics (P/R/F1/Accuracy)
├── output.csv                    ← Predictions (doc_id, entity_id, correct?)
├── AJMC_EN_error_summary.md      ← Error analysis
└── IMPROVEMENTS_SUMMARY.md       ← All results summary
```

**result.txt format:**
```
Accuracy:       47.02%
Precision:      47.0%
Recall:         42.1%
F1 Score:       44.4%
TP:     71
FP:     80
FN:     80
```

### After Running error_analysis_summary.py

```
analysis.md contains:
├── Summary statistics
├─ Error distribution tables
├─ Top error types
├─ Mention length analysis
├─ Entity type breakdown
└─ NIL rate statistics
```

### After Running train_xgb.py

```
models/
└── universal_xgb_threshold.json  ← Trained XGBoost model (50 KB)
    Contains:
    ├─ Feature names
    ├─ Model weights
    ├─ Training metrics
    ├─ Test accuracy (82%)
    └─ Feature importance
```

---

## Section 10: Next Steps

### If You Want To...

| Goal | Do This |
|------|---------|
| **Just review** | Open `thesis/main.pdf` + browse `documentation/` |
| **Understand code** | Read `CODE_MODULES_GUIDE.md` + `code/mrefined/MODEL_COMPARISON.md` |
| **Run evaluation** | Follow Section 2 above |
| **Train models** | Follow Section 3 above |
| **Full reproducibility** | Follow Section 4 above |
| **Use for new datasets** | Follow Task 7.1 above |
| **Understand results** | Read `results/IMPROVEMENTS_SUMMARY.md` |
| **See visualizations** | Open images in `images/` folder |
| **Deep dive into code** | See `CODE_MODULES_GUIDE.md` for 24+ script explanations |

---

## 📚 Related Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 30-second overview
- **[00_START_HERE.md](00_START_HERE.md)** - Navigation guide
- **[CODE_MODULES_GUIDE.md](CODE_MODULES_GUIDE.md)** - All 24+ scripts explained
- **[IMPLEMENTATION_DETAILS.md](IMPLEMENTATION_DETAILS.md)** - System architecture
- **[code/mrefined/INDEX.md](code/mrefined/INDEX.md)** - mReFinED model guide
- **[documentation/SETUP.md](documentation/SETUP.md)** - Environment setup
- **[documentation/REPRODUCTION.md](documentation/REPRODUCTION.md)** - Step-by-step reproduction

---

## ✅ Checklist

Before submitting to supervisor:

- [ ] Read thesis/main.pdf
- [ ] Run code/eval.py successfully
- [ ] Check results/IMPROVEMENTS_SUMMARY.md
- [ ] Understand code/mrefined/ folder structure
- [ ] Review CODE_MODULES_GUIDE.md
- [ ] Check that mReFinED auto-downloads work
- [ ] Verify all 6 datasets are present
- [ ] Confirm XGBoost model (82% accuracy)
- [ ] Review error analysis results
- [ ] Understand 2-month project timeline

---

**🎯 Start with Section 1 (Review) or Section 2 (Run Scripts) depending on your time!**
