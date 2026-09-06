# RAG Pipeline Execution Roadmap (10–12 Hours)

## Overview
Deploy a lightweight **RAG pipeline** that:
1. **Reranks** candidates using a cross-encoder (improves retrieval quality)
2. **Augments** prompts with mention context (richer LLM input)
3. **Ensembles** retrieval + cross-encoder + LLM confidence (robust decisions)

**Expected improvement:** +3–8% F1 on test datasets

---

## Architecture

```
Baseline Pipeline:
  BELA retrieval → Candidate list → LLM prompt → Decision → Output

RAG Pipeline:
  BELA retrieval → Cross-encoder rerank → Context augment → LLM prompt → Ensemble score → Decision → Output
                    (new)                  (new)                           (new)
```

---

## Time Budget (10–12 hours)

| Phase | Time | Task |
|---|---|---|
| 1 | 30 min | Upload RAG modules to server |
| 2 | 2–3 hours | Candidate retrieval (BELA) for 2 datasets |
| 3 | 3–4 hours | RAG prompting on AJMC_EN (156 mentions, fast) |
| 4 | 2–3 hours | RAG prompting on NEWSEYE_FI (654 mentions) |
| 5 | 1 hour | Evaluation + comparison report |
| **Total** | **9–11.5 hours** | ✅ Fits in 10–12 hour window |

---

## Pre-requisites: Server Setup

### 1. Install cross-encoder model (new dependency)
On server, in `llm` environment:

```bash
conda activate llm
pip install sentence-transformers
```

This adds the cross-encoder for reranking (~800 MB download, ~1 min).

### 2. Verify sentence-transformers import
```bash
python -c "from sentence_transformers import CrossEncoder; print('OK')"
```

---

## Execution Steps (Run on Server)

### Phase 1: Upload RAG modules (30 min)
On your **Windows machine**:

```powershell
scp .\rag_reranker.py .\context_augmenter.py .\ensemble_scorer.py `
    .\filter_and_prompt_rag.py .\rag_eval_report.py .\run_rag_test.sh `
    kmpooja@172.20.70.80:~/MHEL-LLAMO/
```

### Phase 2–5: Run RAG pipeline (8–11 hours)
On **server**:

```bash
ssh kmpooja@172.20.70.80
cd ~/MHEL-LLAMO

# Set memory caps (reduce GPU contention)
export MHEL_MAX_GPU_MEM="20GiB"
export MHEL_MAX_CPU_MEM="120GiB"

# Make script executable
chmod +x run_rag_test.sh

# Run (this handles all phases: retrieval → RAG → eval → report)
bash ./run_rag_test.sh |& tee rag_test.log
```

This will:
1. Retrieve candidates for AJMC_EN and NEWSEYE_FI (BELA, ~15 min)
2. Run RAG on AJMC_EN (~1.5 hours, 156 mentions)
3. Run RAG on NEWSEYE_FI (~2.5 hours, 654 mentions)
4. Evaluate both against baselines (~30 min)
5. Generate `rag_improvement_report.html` (instant)

### Phase 5: Retrieve results
On your **Windows machine**:

```powershell
scp kmpooja@172.20.70.80:~/MHEL-LLAMO/rag_improvement_report.html .
scp kmpooja@172.20.70.80:~/MHEL-LLAMO/rag_test.log .
```

---

## Expected Outcomes

### Success Case (High-confidence RAG works):
- **AJMC_EN**: 0.497 (baseline) → 0.52–0.55 (RAG) = +3–8% improvement
- **NEWSEYE_FI**: 0.509 (baseline) → 0.53–0.55 (RAG) = +2–5% improvement
- **Report**: `rag_improvement_report.html` showing side-by-side metrics

### Partial Success (Some improvement):
- At least 1 dataset improves by +1–3%
- Still publishable; iterate in follow-up work

### If Things Go Wrong:
- Check `rag_test.log` for error messages
- Most common: `cross-encoder` model not found (→ pip install sentence-transformers)
- GPU OOM: reduce `--n_candidates` or increase `MHEL_MAX_GPU_MEM`

---

## Files Created

| File | Purpose |
|---|---|
| `rag_reranker.py` | Cross-encoder reranking module |
| `context_augmenter.py` | Context enrichment module |
| `ensemble_scorer.py` | Confidence scoring module |
| `filter_and_prompt_rag.py` | Main RAG pipeline script |
| `rag_eval_report.py` | Generates improvement report |
| `run_rag_test.sh` | Test harness (runs everything) |

---

## Advanced: Tune RAG Hyperparameters

If results are suboptimal, adjust in `filter_and_prompt_rag.py`:

```python
# Line: scorer = EnsembleScorer(...)
scorer = EnsembleScorer(
    retrieval_weight=0.3,    # ← Lower = less penalize low BELA rank
    xencoder_weight=0.4,     # ← Higher = trust cross-encoder more
    llm_weight=0.3,          # ← Higher = trust LLM confidence more
)

# Line: decision = self.scorer.make_decision(...)
decision = self.scorer.make_decision(
    ...,
    threshold=0.5,  # ← Lower = accept more, higher recall; higher = precision-focused
)
```

---

## Summary

**What you're doing:**
- Testing a lightweight RAG pipeline (retrieval reranking + context + ensemble scoring)
- Validating on 2 small datasets (AJMC_EN, NEWSEYE_FI)
- Measuring F1 improvement vs. baseline

**Why 10–12 hours is realistic:**
- RAG scripts are designed for minimal latency overhead
- Only 2 small datasets (fast iteration)
- GPU-contention-friendly (memory caps, resume capability)

**Next steps after validation:**
- If improvement ≥ +3%: scale to all 12 datasets
- If improvement < +1%: debug or switch to fine-tuned reranker approach
- If improvement ≥ +5%: publish as enhancement to original paper
