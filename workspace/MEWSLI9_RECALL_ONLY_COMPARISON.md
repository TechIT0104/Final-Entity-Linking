# MEWSLI-9 Recall-Only Comparison

Date: April 19, 2026

## Exact Metric Used for Comparison

Paper-comparable metric used here: **Recall only**

- Paper reference metric: **Macro-average Recall = 58.8%**
- Reproduced metric from server log: **Average recall = 15.37%**

## Evidence (From Evaluator Output)

Source log:
- `/DATA/kmpooja/mrefined_option1/logs/mewsli9_final_20260416_232428.log`

Extracted lines:
- `Average recall:0.15371511337909285`
- `Micro-avg:24.99`

Code-level definition used by evaluator:
- Per-language recall: `metrics.get_recall()`
- Macro-average recall: `all_recall / len(languages)`
- Micro-average recall: `tp / (tp + fn)` (printed as `Micro-avg`)

## Recall-Only Comparison Table

| Metric | Paper | Reproduction | Difference |
|---|---:|---:|---:|
| Macro-average Recall | 58.80% | 15.37% | -43.43 points |
| Micro-average Recall | N/A in paper table | 24.99% | N/A |

## Important Clarification

For strict paper comparison, use **Macro-average Recall** only.

This means the correct direct comparison is:
- **58.8% (paper)** vs **15.37% (reproduced)**

No F1 is required for this primary comparison.
