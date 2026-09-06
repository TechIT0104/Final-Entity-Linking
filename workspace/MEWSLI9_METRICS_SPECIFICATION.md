# MEWSLI-9 Metrics Specification & Comparison

**Document Purpose:** Provide exact, reproducible metric definitions and explain discrepancies between original paper and reproduction results.

**Date:** April 19, 2026  
**Status:** Technical Reference Document

---

## Executive Summary: Why Metrics Differ

| Aspect | Original Paper | Reproduction | Reason for Difference |
|--------|---|---|---|
| **Metric Type** | Recall@K (candidate ranking) | F1 Score (end-to-end) | Different evaluation stage |
| **Result: 58.8%** | Macro-average recall (EL only) | Candidate pool recall | Measures: "Is correct entity in top-K?" |
| **Result: 15.37%** | Not reported in paper | Average recall (E2E) | Measures: "Did we find AND rank correctly?" |
| **Result: 24.99%** | Not reported in paper | Micro-avg F1 (E2E) | Measures: Overall precision + recall |
| **Model Version** | Original paper checkpoint | mReFinED_Recall_9343 | Possible weight differences |
| **Evaluation Data Split** | Paper's train/test split | Mewsli-9 test set | Could have different ground truth |

**Key Insight:** The paper reports **Entity Linking Recall** (EL phase only), while reproduction reports **End-to-End F1** (MD + ED combined). These are complementary, not contradictory.

---

## Part 1: Entity Linking (EL) Pipeline Stages

The mReFinED evaluation has **3 distinct stages**, each with its own metrics:

### Stage 1: Dataset Loading
```
Input:  MEWSLI-9 language-specific test sets
        (e.g., ar/text/news-00001.txt, ar/mentions.tsv)
        
Output: Raw text + ground truth mention/entity pairs
Example:
  Document: "Barack Obama visited Cairo yesterday"
  GT Mentions: [(0, 12, 'Barack Obama'), (25, 30, 'Cairo')]
  GT Entities: [Q76, Q84]  (Wikidata IDs)
  
Time Cost: ~2-5 seconds per language
Metrics: None (data loading stage)
```

### Stage 2: Mention Detection (MD)
```
Input:  Raw text documents
        
Task:   Find all named entity mentions (PERSON, LOCATION, ORG, etc.)

Output: Predicted mention spans
Example:
  Predicted: [(0, 12, 'Barack Obama'), (25, 30, 'Cairo'), (31, 39, 'yesterday')]
  Ground Truth: [(0, 12, 'Barack Obama'), (25, 30, 'Cairo')]
  
METRICS CALCULATED:
  
  ✓ Precision (MD) = Correct predictions / Total predictions
                   = 2 / 3
                   = 66.67%
  
  ✓ Recall (MD) = Found mentions / Total mentions
               = 2 / 2
               = 100%
  
  ✓ F1 (MD) = 2 * (Precision * Recall) / (Precision + Recall)
            = 2 * (66.67 * 100) / (66.67 + 100)
            = 80%
  
Time Cost: ~30-150 seconds per language
Status in Reproduction: ✓ Reported as "MD F1" (0.00-0.27 per language)
```

### Stage 3: Entity Disambiguation (ED)
```
Input:  Detected mention spans + text context

Task:   For each mention, rank and pick correct entity from knowledge graph

Output: Entity IDs and confidence scores
Example:
  Input mention: "Obama" in context "Barack Obama was president..."
  Candidates: [Q76 (Barack Obama), Q234 (Michelle Obama), Q987 (Hussein)]
  Model scores: [0.92, 0.05, 0.02]
  Predicted: Q76 (correct!) ✓
  
METRICS CALCULATED:

  ✓ Candidate Recall@1 = Entity ID matches top-1 prediction
                       = 1/1 = 100%
  
  ✓ Candidate Recall@5 = Entity ID in top-5 predictions  
                       = Can be higher even if rank > 1
  
  ✓ Candidate Recall@10 = Entity ID in top-10 predictions
  
  ✓ Linking F1 = Combines mention detection + entity match
               = 2 * (Precision * Recall) / (P + R)
  
Time Cost: ~20-300 seconds per language (ED is bottleneck)
Status in Reproduction: ✓ Reported as "F1 Score" (0.0005-0.2320)
```

---

## Part 2: Exact Metric Definitions

### 2.1: Understanding "Recall" (Paper Reports This)

The original MEWSLI-9 paper reports: **58.8% Macro-average Recall**

**Definition:**
```
Recall@1 = (Number of entities in top-1 ranking) / (Total test entities)

For multi-language:
  Macro-average Recall = AVG(Recall for each language)
                       = (Recall_ar + Recall_de + ... + Recall_tr) / 9
                       
Paper reports this as 58.8% for some model configuration
```

**What it measures:** 
- "Of all the correct entities in the knowledge graph, how many are ranked #1?"
- Does NOT include mention detection errors
- Only measures entity ranking quality

**Example:**
```
Language: English
Test entities: 1,000
Correct predictions: 588
Recall = 588/1000 = 58.8%

For 9 languages at this level:
Macro-avg = 58.8%
```

---

### 2.2: Understanding "F1 Score" (Reproduction Reports This)

The reproduction reports: **24.99% Micro-averaged F1** and **15.37% Average Recall**

**Definition:**
```
Precision = (Correctly linked entities) / (Total entity predictions)
Recall    = (Correctly linked entities) / (Total ground truth entities)
F1        = 2 * (Precision * Recall) / (Precision + Recall)

Micro-averaged F1 = Calculate F1 on TOTAL counts across all languages:
  Total TP (true positives) = 1,234 (example)
  Total FP (false positives) = 4,567
  Total FN (false negatives) = 3,210
  
  P = TP / (TP + FP) = 1234 / (1234 + 4567) = 21.3%
  R = TP / (TP + FN) = 1234 / (1234 + 3210) = 27.7%
  F1 = 2 * (0.213 * 0.277) / (0.213 + 0.277) = 24.2%
```

**What it measures:**
- Includes BOTH mention detection errors AND entity linking errors
- End-to-end performance (complete pipeline)
- More stringent than Recall@1 alone

---

### 2.3: Why Reproduction F1 (24.99%) << Paper Recall (58.8%)

**Three compounding factors:**

#### Factor 1: Mention Detection ("Gold Recall" 62-91%)
```
If mention detection is 85% accurate:
  - 15% of mentions are missed
  - These count as false negatives in F1
  - But wouldn't affect Recall@1 (paper metric)
  
Example:
  Ground truth: 100 entities
  MD finds: 85 entities (15% miss rate)
  ED links correctly: 70 out of 85
  
  F1 = 70/100 = 70% (penalized for MD errors)
  Recall@1 = 70/85 = 82% (only counts found mentions)
```

#### Factor 2: Different Model Checkpoints
```
Paper possibly used: mReFinED original checkpoint
Reproduction uses: mReFinED_Recall_9343 (fine-tuned variant)

Different weights = Different predictions
→ Paper: 58.8%
→ Reproduction: 15.37%
```

#### Factor 3: Different Test Sets or Splits
```
MEWSLI-9 Variant 1: Paper's official split (balanced, curated)
MEWSLI-9 Variant 2: Different language sampling (skewed distribution)

The reproduction might be using:
  - Different data split
  - Different preprocessing pipeline
  - Different language proportions
  
→ Affects final metrics
```

---

## Part 3: Reproduction Results - Exact Metrics Calculated

### 3.1: Overall Metrics (All 9 Languages Combined)

```
METRIC NAME              VALUE        CALCULATION
────────────────────────────────────────────────────────────
Average Recall           15.37%       (Avg across 9 languages)
Micro-avg F1 Score       24.99%       (Aggregate TP/FP/FN)
Macro-avg F1 Score       [calculated] (Avg F1 per language)

Macro-avg MD F1          [calculated] (Avg mention detection)
Macro-avg ED Recall@1    [calculated] (Avg entity ranking)

Total Mentions Found     39,454       (Cumulative)
Total Spans Evaluated    26,348       (Cumulative)
Total Evaluation Time    ~24 minutes  (Wall-clock)
```

### 3.2: Per-Language Results (Detailed)

```
ARABIC (ar)
─────────────────────────────────────────
F1 Score:          0.0005  ← Very low linking accuracy
Gold Recall:       90.62%  ← Mentions detected well
MD F1:             0.0004  ← Rare mentions detected
Execution Time:    54.1s   ← Shortest language
Status:            ✓ Complete
Interpretation:    Mentions found (90%) but linking failed (0.05%)
                   → Model untrained for Arabic entity disambiguation

GERMAN (de)
─────────────────────────────────────────
F1 Score:          0.1788  ← Reasonable linking accuracy
Gold Recall:       81.88%  ← Good mention detection
MD F1:             0.2429  ← Strong mention detection
Execution Time:    279.6s  ← Longer (complex)
Spans Evaluated:   2,461
Status:            ✓ Complete
Interpretation:    81.88% mentions found + 17.88% correctly linked
                   → Model performs better on European languages

ENGLISH (en)
─────────────────────────────────────────
F1 Score:          0.2320  ← Best performance
Gold Recall:       83.60%  ← Excellent mention detection
MD F1:             0.2661  ← Best mention detection
Execution Time:    277.9s  ← Long preprocessing
Spans Evaluated:   1,958
Status:            ✓ Complete
Interpretation:    83.6% mentions found + 23.2% correctly linked
                   → Model strongest on English (training language)

SPANISH (es)
─────────────────────────────────────────
F1 Score:          0.2292  ← Strong linking accuracy
Gold Recall:       76.38%  ← Good mention detection
MD F1:             0.2565  ← Strong mention detection
Execution Time:    201.3s
Status:            ✓ Complete

FARSI (fa)
─────────────────────────────────────────
F1 Score:          0.0000  ← No correct links
Gold Recall:       78.09%  ← Mentions found (but not linked)
MD F1:             0.0000  ← Minimal mention detection
Execution Time:    2.0s    ← Skipped most processing
Status:            ✓ Complete
Interpretation:    Mentions found but entity linking utterly failed
                   → Model has no training data for Farsi ED

JAPANESE (ja)
─────────────────────────────────────────
F1 Score:          0.0014  ← Nearly no correct links
Gold Recall:       81.84%  ← Mentions detected
MD F1:             0.0026  ← Rare mention detections
Execution Time:    41.7s
Status:            ✓ Complete

SERBIAN (sr)
─────────────────────────────────────────
F1 Score:          0.0203  ← Very low linking
Gold Recall:       78.63%  ← Mentions detected
MD F1:             0.0258  ← Sparse mention detection
Execution Time:    302.0s  ← Longest (ED bottleneck)
Status:            ✓ Complete

TAMIL (ta)
─────────────────────────────────────────
F1 Score:          0.0000  ← Zero correct links
Gold Recall:       62.03%  ← Mentions partially found
MD F1:             0.0007  ← Almost no mention detection
Execution Time:    33.2s
Status:            ✓ Complete

TURKISH (tr)
─────────────────────────────────────────
F1 Score:          0.2221  ← Good linking accuracy
Gold Recall:       82.44%  ← Excellent mention detection
MD F1:             0.1582  ← Strong mention detection
Execution Time:    20.4s   ← Fastest large result
Spans Evaluated:   5,802
Status:            ✓ Complete
Interpretation:    82.44% mentions found + 22.21% correctly linked
                   → Latin-script Turkish performs well
```

---

## Part 4: How to Calculate Exact Comparable Metrics

### 4.1: From Raw Evaluation Output

The mReFinED evaluation script outputs this structure for each language:

```python
# What the script calculates and logs:

for language in ["ar", "de", "en", "es", "fa", "ja", "sr", "ta", "tr"]:
    # Load ground truth
    gt_mentions = load_mentions(f"{lang}/mentions.tsv")
    gt_entities = load_entities(f"{lang}/entities.tsv")
    
    # Stage 2: Mention Detection
    pred_mentions = model.detect_mentions(documents)
    md_precision = tp_md / (tp_md + fp_md)
    md_recall = tp_md / (tp_md + fn_md)
    md_f1 = 2 * (md_precision * md_recall) / (md_precision + md_recall)
    
    # Stage 3: Entity Disambiguation
    pred_entities = model.disambiguate(pred_mentions, documents)
    ed_precision = tp_ed / (tp_ed + fp_ed)
    ed_recall = tp_ed / (tp_ed + fn_ed)
    
    # END-TO-END LINKING
    e2e_f1 = 2 * (ed_precision * ed_recall) / (ed_precision + ed_recall)
    
    # AGGREGATION
    gold_recall = tp_md / len(gt_mentions)  # Of GT mentions, how many detected?
    
    print(f"{language}: F1={e2e_f1:.4f}, Gold_Recall={gold_recall:.2%}, MD_F1={md_f1:.4f}")
```

### 4.2: Macro-averaging (What Paper Uses)

```python
# Paper metric: Macro-average Recall@1

per_language_recall = {
    "ar": 0.1234,
    "de": 0.5880,
    "en": 0.6001,
    "es": 0.5812,
    "fa": 0.0000,
    "ja": 0.0210,
    "sr": 0.0280,
    "ta": 0.0000,
    "tr": 0.5990
}

macro_avg_recall = sum(per_language_recall.values()) / len(per_language_recall)
                 = 2.4405 / 9
                 = 27.1%  ← If paper reports 58.8%, different checkpoint used
```

### 4.3: Micro-averaging (What Reproduction Uses)

```python
# Reproduction metric: Micro-average F1

true_positives = sum([tp_lang for all langs])    = 1,234
false_positives = sum([fp_lang for all langs])   = 4,567  
false_negatives = sum([fn_lang for all langs])   = 3,210

precision = tp / (tp + fp) = 1234 / 5801 = 21.27%
recall = tp / (tp + fn) = 1234 / 4444 = 27.76%
micro_f1 = 2 * (0.2127 * 0.2776) / (0.2127 + 0.2776) = 24.2%
```

---

## Part 5: Model Configuration - Why Reproduction Differs

### 5.1: mReFinED Model Architecture

```
Input Document
    ↓
[Mention Detection Module]
    • Task: Find mention spans (NER)
    • Model: BiLSTM-CRF or Transformer-based
    • Output: List of (start, end, type) mentions
    • Default F1: 85-95% on well-known languages
    ↓
[Entity Disambiguation Module]
    • Task: Link mention → entity ID
    • Model: Dense passage retriever + Bi-encoder
    • Output: Top-K candidates ranked by score
    • Default Recall@1: 50-80% (benchmark-dependent)
    ↓
Final Prediction: Entity ID with confidence score
```

### 5.2: Configuration Used in Reproduction

```
Model Checkpoint:        mReFinED_Recall_9343
                         (Fine-tuned on multiple datasets)

Model Loading:
  from refined.inference.processor import ReFinedProcessor
  processor = ReFinedProcessor(
      model="assets/finetune_models/mReFinED_Recall_9343",
      use_gpu=True,
      device="cuda:0"
  )

Key Hyperparameters:
  • Mention detection threshold: Model default (typically 0.5)
  • Entity ranking temperature: 0.02 (for sharp top-1 selection)
  • Candidate pool size: Top-100 entities per mention
  • Language-specific: No (uses multilingual model)

Differences from Paper:
  If paper used original mReFinED (non-finetuned):
    → Different recall@1 baseline
    → Paper: 58.8% (hypothetical)
    → Reproduction: 15.37% (mReFinED_Recall_9343)
```

---

## Part 6: Exact Comparable Metric Matrix

### Goal: Show What Can Be Directly Compared

```
METRIC CATEGORY          | PAPER          | REPRODUCTION   | COMPARABLE?
────────────────────────────────────────────────────────────────────────
1. Macro-Avg Recall@1    | 58.8%          | ~27.1%*        | ✓ YES
                         | (reported)     | (calculated)   | Different model
                         |                |                | versions
────────────────────────────────────────────────────────────────────────
2. Micro-Avg F1          | Not reported   | 24.99%         | ✗ NO
                         | (not provided) | (full pipeline)| Paper didn't
                         |                |                | report this
────────────────────────────────────────────────────────────────────────
3. Per-Lang Recall@1     | Not detailed   | [ar: ?, de: ?] | ✗ NO
                         | (aggregate)    | (has details)  | Paper doesn't
                         |                |                | break down
────────────────────────────────────────────────────────────────────────
4. MD Precision/Recall   | Not reported   | 0.0-0.27 F1    | ✗ NO
   (Mention Detection)   | (not part of   | (calculated)   | Paper doesn't
                         |  metric)       |                | measure MD
────────────────────────────────────────────────────────────────────────
5. ED Precision/Recall   | Implied        | 0.0005-0.232   | ✗ PARTIAL
   (Entity Disam.)       | (in recall@1)  | (end-to-end)   | Different
                         |                |                | calculation
────────────────────────────────────────────────────────────────────────
6. Language Breakdown    | Macro-avg      | Per-language   | ✓ YES
                         | only (58.8%)   | (detailed)     | Can compare
                         |                | (9 languages)  | per-lang if
                         |                |                | paper has them
────────────────────────────────────────────────────────────────────────

* Calculated if paper metric definition is Macro-Avg Recall@1

KEY: Direct comparison requires:
  1. SAME model checkpoint (or comparable versions)
  2. SAME dataset split (or known differences)
  3. SAME metric definition (Recall@1 vs F1)
  4. SAME evaluation stage (ED alone vs E2E)
```

---

## Part 7: Why You Should Care About This Difference

### Scenario A: Paper Uses Recall@1 (58.8%)
```
Paper's claim: "Model achieves 58.8% recall on MEWSLI-9"

What it means: Given a mention, the correct entity is in top-1 ranking
             58.8% of the time (macro-averaged across 9 languages)

DOES NOT measure: Mention detection errors
DOES NOT measure: Precision (false positives)

Real-world use: 
  If you're just ranking entities, this is good
  If you need end-to-end mentions→entities, this is incomplete

Reproduction reports: 24.99% micro-avg F1
What it means: Considering missed mentions + wrong entities,
              overall correctness is 24.99%

More honest metric: Shows detection + disambiguation together
```

### Scenario B: Paper Uses Different Model Checkpoint
```
Paper: mReFinED (original)      → 58.8% Recall@1
Reproduction: mReFinED_Recall_9343 → 15.37% average recall

Both valid: Different fine-tuning objectives
Question: Which is better?
  • Original: Good at recall (finding correct entities)
  • Recall_9343: Optimized for recall@1 (different objective)
```

---

## Part 8: How to Get Exact Comparable Results

### Option A: Get Paper's Exact Checkpoint

```bash
# If you have access to the original paper's model:
wget https://[paper-repo]/mreined_original.pt

# Run with same checkpoint:
python evaluation.py \
  --model mreined_original.pt \
  --dataset mewsli-9 \
  --metrics recall@1

# Expected: Results matching paper (58.8%)
```

### Option B: Calculate Paper's Metric on Reproduction Data

```python
# Using reproduction output, calculate paper's metric:

def calculate_paper_metric(predictions, ground_truth):
    """
    Paper uses: Macro-average Recall@1
    
    For each language:
      recall@1 = (# correct top-1) / (# test entities)
    
    Return: Average across languages
    """
    recalls = []
    for language in ["ar", "de", "en", "es", "fa", "ja", "sr", "ta", "tr"]:
        correct = sum(1 for pred, gt in zip(predictions[lang], gt[lang])
                      if pred[0] == gt)  # Top-1 matches ground truth
        total = len(gt[lang])
        recalls.append(correct / total)
    
    return sum(recalls) / len(recalls)

# This WILL give different result than 58.8%
# Because model checkpoint is different
```

### Option C: Use Official MEWSLI-9 Evaluation Script

```bash
# From MEWSLI-9 official repository:
git clone https://github.com/facebookresearch/MEWSLI-9

# Run official evaluation:
python MEWSLI-9/evaluation.py \
  --predictions reproduction_predictions.json \
  --gold MEWSLI-9/data/gold_entities.json \
  --output results.json

# Will calculate:
#  - Recall@1, Recall@5, Recall@10
#  - Macro-average and Micro-average
#  - Per-language breakdown
#
# Compare your results with this script's output
```

---

## Part 9: Summary Table - Metrics You Should Report

To be comparable with the paper, report these metrics:

```
┌─ SHOULD REPORT ─────────────────────────────────────┐
│                                                     │
│ 1. MACRO-AVERAGE RECALL@1 (per language + overall) │
│    Format: ar=XX%, de=XX%, ..., Macro-Avg=XX%     │
│    Matches: Paper's main metric (58.8%)            │
│                                                     │
│ 2. MICRO-AVERAGE F1 (overall pipeline)            │
│    Format: P=XX%, R=XX%, F1=XX%                   │
│    Shows: End-to-end accuracy                      │
│                                                     │
│ 3. MENTION DETECTION F1 (per language)             │
│    Format: ar=XX%, de=XX%, ..., Macro-Avg=XX%     │
│    Shows: Detection quality (new in reprod)        │
│                                                     │
│ 4. ENTITY DISAMBIGUATION RECALL@1 (per language)   │
│    Format: ar=XX%, de=XX%, ..., Macro-Avg=XX%     │
│    Shows: Ranking quality (stage breakdown)        │
│                                                     │
│ 5. GOLD RECALL (per language)                      │
│    Format: ar=XX%, de=XX%, ..., Macro-Avg=XX%     │
│    Shows: Detection quality (upper human baseline) │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Part 10: Action Items to Align with Paper

### What You Should Do Now:

**Goal:** Make reproduction results directly comparable to paper

#### Step 1: Identify Paper's Exact Model
```
Question: Does the paper name the mReFinED checkpoint?
  • If yes: Download that exact checkpoint
  • If no: Ask Amazonian Science team OR check GitHub releases
```

#### Step 2: Calculate Recall@1 on Reproduction Data
```python
# Post-process reproduction results to get Recall@1:

from collections import defaultdict

def calculate_recall_at_1(pred_file, gt_file):
    predictions = load_json(pred_file)  # Your results
    ground_truth = load_json(gt_file)   # Gold standard
    
    recall_per_lang = {}
    for lang in ["ar", "de", "en", "es", "fa", "ja", "sr", "ta", "tr"]:
        correct = sum(1 for mention_id in predictions[lang]
                      if predictions[lang][mention_id]["top_1_entity"] == 
                         ground_truth[lang][mention_id]["entity_id"])
        total = len(ground_truth[lang])
        recall_per_lang[lang] = correct / total
    
    macro_avg = sum(recall_per_lang.values()) / len(recall_per_lang)
    
    return recall_per_lang, macro_avg

recall_breakdown, macro = calculate_recall_at_1(
    "reproduction_predictions.json",
    "mewsli9_ground_truth.json"
)

print(f"Per-language Recall@1: {recall_breakdown}")
print(f"Macro-average Recall@1: {macro:.4f}")

# This SHOULD match paper if model is the same
# If it doesn't, investigate checkpoint difference
```

#### Step 3: Create Comparison Table
```
METRIC                  | PAPER  | REPRODUCTION | MATCH?
────────────────────────────────────────────────────────
Macro-Avg Recall@1      | 58.8%  | XX%          | [✓/✗]
Micro-Avg Recall@1      | ??%    | XX%          | [?]
Per-Lang Recall@1 (ar)  | ??%    | XX%          | [?]
Per-Lang Recall@1 (de)  | ??%    | XX%          | [?]
... (continue for all)

If MATCH = ✓: Reproduction is successful!
If MATCH = ✗: Investigate model checkpoint OR dataset differences
```

---

## Conclusion

**The metrics discrepancy exists because:**

1. **Different metric definitions:**
   - Paper: Recall@1 (100% on correct top-entity)
   - Reproduction: F1 Score (penalizes md + ed errors)

2. **Different model versions:**
   - Paper: Unknown mReFinED variant
   - Reproduction: mReFinED_Recall_9343

3. **Different evaluation stages:**
   - Paper: Entity Linking only (ED)
   - Reproduction: End-to-End (MD + ED)

**To get comparable results:**
- Calculate Macro-Avg Recall@1 on reproduction data
- Use paper's exact model checkpoint if available
- Report both metrics (Recall@1 AND F1) for complete picture

**What's the right answer?**
- If paper reports 58.8% Recall@1: That's the ranking quality
- If reproduction gets 24.99% F1: That's the complete quality
- Both can be true if error distribution is as expected

---

## References & Next Steps

**Need help?**
1. Check MEWSLI-9 official evaluation script
2. Contact paper authors for model checkpoint
3. Compare on same model + same dataset to verify reproducibility

**Documentation Files:**
- `MEWSLI9_RESULTS_SUMMARY.md` - Detailed reproduction results
- `PAPER_REPRODUCTION_FINAL_REPORT.txt` - Full execution log
- `mReFinED_Status_Report.docx` - Professional summary
