# Entity Linking - Historical NER & Entity Linking System

**Final Submission Package** | May 6, 2026

This package contains the complete implementation, evaluation results, and thesis documentation for the Entity Linking project covering BLINK, mReFinED, MHEL-LLaMo, and multilingual historical entity linking benchmarks.

## 📋 Project Overview

**Main Contributions:**
1. Reproduction of BLINK and MVD entity linking baselines
2. mReFinED multilingual entity linking on MEWSLI-9 benchmark
3. MHEL-LLaMo: Confidence-based routing for historical entity linking
4. **New (30% of work):**
   - XGBoost confidence router (82% routing accuracy)
   - Systematic error analysis on FP/FN patterns
   - Hardware adaptation for single-GPU reproducibility
   - Offset validation fixes for TR2016

**Contribution Split:** ~70% paper-inspired, ~30% engineering/tuning

## 📂 Folder Structure

```
Final Entity Linking/
├── thesis/                  # Final thesis PDF and source
├── code/                    # Key implementation scripts
├── results/                 # Evaluation metrics and outputs
├── models/                  # Trained models (XGBoost router)
├── dataset/                 # Sample datasets & metadata
├── documentation/           # Setup guides and API docs
└── README.md               # This file
```

### 1. **thesis/** - Final Thesis Document
- `main.pdf` - Complete thesis with all contributions and results
- Contains:
  - Contribution breakdown (30/70 split with evidence)
  - XGBoost router metrics (+12% routing accuracy)
  - Error analysis findings
  - MEWSLI-9 reproduction results
  - TR2016 offset validation improvements

### 2. **code/** - Implementation & Evaluation Scripts
Essential Python scripts for running the pipeline:
- `eval.py` - Evaluation metric computation (F1, Precision, Recall, Accuracy)
- `rerank_only.py` - Cross-encoder reranking baseline (CPU-friendly)
- `error_analysis_summary.py` - FP/FN pattern analysis
- `train_xgb.py` - XGBoost confidence router training

### 3. **results/** - Key Evaluation Results
- **AJMC_EN Results:**
  - `error_summary.md` - Error analysis with FP/FN patterns
  - Baseline metrics (47% accuracy, 71 TP, 80 FP, 80 FN)
  
- **MEWSLI-9 Results:**
  - Per-language F1 scores across 9 languages
  - Findings on Latin vs non-Latin script performance
  
- **XGBoost Router Performance:**
  - 82% routing accuracy (vs 70% threshold-based baseline)
  - Precision/Recall on easy/hard sample discrimination
  - Training data: 18,075 mentions

### 4. **models/** - Trained Models
- `universal_xgb_threshold.json` - Trained XGBoost router model
  - Features: confidence score, margin, mention length, edit distance
  - Can be deployed without retraining LLM
  - Improves routing decisions from 70% to 82% accuracy

### 5. **dataset/** - Benchmark Information
- Links to official datasets (AJMC, MEWSLI-9, NEWSEYE, HIPE, MHERCL)
- Sample data format specifications
- Dataset statistics and language breakdown
- Historical entity linking dataset overview

### 6. **documentation/** - Setup & Execution Guides
- `SETUP.md` - Environment setup (conda, CUDA, dependencies)
- `USAGE.md` - How to run each component
- `API.md` - Function signatures and parameter descriptions
- `REPRODUCTION.md` - Step-by-step reproduction guide

## 🚀 Quick Start

### 1. Environment Setup
```bash
conda create -n entity-linking python=3.11
conda activate entity-linking
pip install torch transformers xgboost pandas tqdm
```

### 2. Run Evaluation
```bash
python code/eval.py --path_data dataset/ --path_results results/
```

### 3. Error Analysis
```bash
python code/error_analysis_summary.py --path_results results/AJMC_EN --output error_report.md
```

### 4. Train Confidence Router
```bash
python code/train_xgb.py
```

## 📊 Key Results

### Model Tuning Achievement
| Component | Baseline | Our Improvement | Gain |
|-----------|----------|-----------------|------|
| Confidence Router | 70% (threshold) | 82% (XGBoost) | +12% accuracy |
| TR2016 (de) Recall | 1.54% | 8.42% | +5.5x improvement |
| MEWSLI-9 Stability | Partial | All 9 languages | Full reproducibility |

### Error Analysis Findings
- **Systematic Failures:** Abbreviations (Ph., Ant., El.), short mentions (median 5 chars)
- **NIL Misclassification:** 59% of false positives predicted as NIL
- **Top Error Types:** WORK entities (62 FPs/FNs), PER entities (18 FPs/FNs)
- **Key Insight:** Short mentions + rare entities require LLM routing

## 📝 Thesis Highlights

### Contributions Section
- Clear 30/70 split breakdown with evidence
- XGBoost router: model tuning contribution with 82% accuracy
- Error analysis: systematic investigation of FP/FN patterns
- Hardware adaptation: mixed precision, gradient accumulation

### Results Chapter
- New "Model Tuning: XGBoost Confidence Router" section
- Parameter tuning justification table
- Measured improvements from engineering work
- Post-mid findings summary with quantified improvements

## 🔧 Technical Details

**Hardware Used:**
- GPU: Single 32GB VRAM (mixed precision, gradient accumulation)
- Frameworks: PyTorch, Transformers, XGBoost
- Models: Mistral 24B, BELA (bi-encoder), ms-marco-MiniLM (cross-encoder)

**Datasets Evaluated:**
- AJMC (Ancient Greek/German/French)
- MEWSLI-9 (9 languages across 3 benchmarks)
- NEWSEYE, HIPE, MHERCL (historical datasets)

## 📞 Contact & Questions

For questions about reproduction or implementation:
- See `documentation/REPRODUCTION.md` for step-by-step guide
- Check `documentation/API.md` for function details
- Review thesis for theoretical background

## ✅ Checklist for Submission

- [x] Thesis PDF with contributions clearly marked
- [x] All evaluation scripts in code/
- [x] Key results and metrics documented
- [x] Trained models included
- [x] Setup and usage documentation
- [x] Dataset references and formats
- [x] Error analysis findings

---

**Prepared for:** Academic Submission
**Date:** May 6, 2026
**Status:** Ready for supervisor review
