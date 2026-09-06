# RAG Pipeline Complete Fix & Deploy (Step-by-Step)

## Problem Fixed

**Root cause**: In `src/retriever.py`, the `_encode_text()` method filters out invalid mentions (those with length=0), returning fewer representations than total mentions in the batch. But `get_candidates_batch()` was trying to access results for ALL mentions, causing `IndexError: list index out of range`.

**Solution**: 
1. Track valid mentions separately with `valid_idx` (not `example_idx`)
2. Only increment `valid_idx` when we actually have a result
3. Added error handling in `get_entity_info()` to gracefully handle missing entities
4. Added try-except blocks to catch and log errors instead of crashing

---

## Deploy & Run on Server (Copy-Paste)

### Step 1: Upload the FIXED retriever.py
**On your Windows machine:**
```powershell
scp c:\Users\Dhruv\MHEL-LLAMO\src\retriever.py kmpooja@172.20.70.80:~/MHEL-LLAMO/src/
```
(Enter password when prompted)

**Verify on server:**
```bash
ssh kmpooja@172.20.70.80
cd ~/MHEL-LLAMO
grep "valid_idx.*Index into results" src/retriever.py
# Should print: valid_idx = 0  # Index into results (scores/indices)
```

### Step 2: Upload deployment script
**On Windows:**
```powershell
scp c:\Users\Dhruv\MHEL-LLAMO\run_rag_deploy.sh kmpooja@172.20.70.80:~/MHEL-LLAMO/
```

### Step 3: Run the full pipeline on server
**On server:**
```bash
cd ~/MHEL-LLAMO

# Install cross-encoder (one-time, already done but doesn't hurt)
conda activate llm
pip install sentence-transformers

# Run the complete fixed pipeline
chmod +x run_rag_deploy.sh
bash ./run_rag_deploy.sh |& tee rag_deploy.log
```

This will:
1. ✓ Verify retriever fix is applied
2. ✓ Clear old NEWSEYE_FI candidates (force re-test)
3. ✓ Re-run BELA retrieval with FIXED retriever
4. ✓ Run RAG on AJMC_EN (~1.5h)
5. ✓ Run RAG on NEWSEYE_FI (~2.5h)
6. ✓ Evaluate both and generate report

**Total time:** ~4.5 hours (accounting for GPU contention)

### Step 4: Get results
**On Windows:**
```powershell
scp kmpooja@172.20.70.80:~/MHEL-LLAMO/rag_improvement_report.html .
scp kmpooja@172.20.70.80:~/MHEL-LLAMO/rag_deploy.log .
```

Then open `rag_improvement_report.html` in your browser.

---

## What Changed in retriever.py

**Before (BROKEN):**
```python
example_idx = 0
for text, lengths in zip(texts, mention_lengths):
    if length > 0:  # Valid mention
        ex_indices = indices[example_idx]  # BUG: example_idx > len(indices) when some mentions invalid
        ...
    example_idx += 1  # Increments even for invalid mentions!
```

**After (FIXED):**
```python
valid_idx = 0  # Index into FAISS results
for text, lengths in zip(texts, mention_lengths):
    if length > 0:  # Valid mention
        ex_indices = indices[valid_idx]  # CORRECT: only access valid results
        ...
        valid_idx += 1  # Only increment for valid mentions
    predictions.append(candidates)  # Append empty list for invalid
```

---

## Fallback: If you can't run the script

**Run manually on server:**
```bash
cd ~/MHEL-LLAMO
conda activate bela39

# Re-retrieve NEWSEYE_FI with fixed retriever
rm -f results/NEWSEYE_FI/candidates_test_top*.json
python get_candidates.py --dataset_path test_data/NEWSEYE_FI --output_dir results/NEWSEYE_FI --top_k 20 --lang fi --batch_size 4 --device cuda:0

# If that succeeds, then run RAG:
conda activate llm
export MHEL_MAX_GPU_MEM="20GiB"
export MHEL_MAX_CPU_MEM="120GiB"

python filter_and_prompt_rag.py --json_f results/NEWSEYE_FI/candidates_test_top20_fi.json --dataset_path test_data/NEWSEYE_FI --output_dir results/NEWSEYE_FI/rag_poro2_8B_k20_fi --n_candidates 20 --model_id LumiOpen/Llama-Poro-2-8B-Instruct --threshold 0.5 --device cuda:0 --resume

python eval.py --path_data test_data/NEWSEYE_FI --path_results results/NEWSEYE_FI/rag_poro2_8B_k20_fi
```

---

## Expected Results

**If all works:**
- ✅ No `IndexError` during candidate retrieval
- ✅ AJMC_EN: 0.497 → 0.52–0.55 (+3–8%)
- ✅ NEWSEYE_FI: 0.509 → 0.53–0.55 (+2–5%)
- ✅ `rag_improvement_report.html` generated

**If still failing:**
- Check `rag_deploy.log` for the exact error
- Report the error message and we'll patch further
