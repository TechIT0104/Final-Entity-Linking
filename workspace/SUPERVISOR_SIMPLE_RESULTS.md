# Supervisor Results (Evidence-Only)

Date: 2026-05-14

This file contains only metrics that are directly available from current artifacts or from scripts executed in this workspace session.

## 1) MEWSLI-9 Result

### 1.1 mReFinED on MEWSLI-9 (available)
Source: `MEWSLI9_RESULTS_SUMMARY.md`

- Average Recall: **15.37%**
- Micro-averaged F1: **24.99%**
- Languages: ar, de, en, es, fa, ja, sr, ta, tr

### 1.2 MHEL-LLaMo basic result on MEWSLI-9 (available in server artifacts)
Source: `MHEL-LLAMO/results/MEWSLI_EN/candidates_test_top50_en.json`

- Mewsli candidate file exists on the server and was used by `test_mewsli_xgb.py`
- The server run extracted **3 records** for the MEWSLI OOD test

### 1.3 MEWSLI-9 with XGBoost (verified on server)
Executed script: `MHEL-LLAMO/test_mewsli_xgb.py`

Server output:
- `Accuracy: 1.0000`
- Precision: **1.00**
- Recall: **1.00**
- F1: **1.00**
- Support: **3**

Interpretation:
- This is the actual MEWSLI XGBoost output from the server run.
- The test set is very small here, so the score is not representative of a large benchmark, but it is the verified result available in the server artifact.

## 2) All MHEL-LLaMo paper datasets: reproduced vs our changes

### 2.1 Reproduced paper best-setting results (all matched)
Source: `MHEL-LLAMO/reproduction_report.md`

- Checked runs: **12**
- Matched within tolerance (±0.01): **12/12**

| Dataset | Lang | Paper Expected | Reproduced |
|---|---|---:|---:|
| HIPE-2020 | de | 0.620 | 0.620 |
| HIPE-2020 | en | 0.723 | 0.723 |
| HIPE-2020 | fr | 0.692 | 0.692 |
| NewsEye | de | 0.556 | 0.556 |
| NewsEye | fi | 0.509 | 0.509 |
| NewsEye | fr | 0.662 | 0.662 |
| NewsEye | sv | 0.521 | 0.521 |
| AJMC | de | 0.521 | 0.521 |
| AJMC | en | 0.496 | 0.497 |
| AJMC | fr | 0.635 | 0.635 |
| MHERCL | en | 0.700 | 0.705 |
| MHERCL | it | 0.698 | 0.698 |

### 2.2 "Other changes from our end" comparison (vanilla vs best run variant)
Source: `MHEL-LLAMO/honest_all_runs_table.md`

Definition used here:
- Vanilla baseline = `_van_` run for each dataset/language.
- Best variant = best paper-score run among available variants (`chain`, `chain_median`, `ens_median`, `van`).

| Dataset | Lang | Vanilla (paper score) | Best Variant (paper score) | Delta |
|---|---|---:|---:|---:|
| HIPE | de | 0.616 | 0.620 | +0.004 |
| HIPE | en | 0.672 | 0.723 | +0.051 |
| HIPE | fr | 0.692 | 0.692 | +0.000 |
| NewsEye | de | 0.488 | 0.556 | +0.068 |
| NewsEye | fi | 0.470 | 0.509 | +0.039 |
| NewsEye | fr | 0.593 | 0.662 | +0.069 |
| NewsEye | sv | 0.504 | 0.521 | +0.017 |
| AJMC | de | 0.521 | 0.521 | +0.000 |
| AJMC | en | 0.497 | 0.497 | +0.000 |
| AJMC | fr | 0.635 | 0.635 | +0.000 |
| MHERCL | en | 0.703 | 0.705 | +0.002 |
| MHERCL | it | 0.685 | 0.698 | +0.013 |

## 3) XGBoost result actually generated in this session

Executed script: `MHEL-LLAMO/train_xgb.py`

Training/eval summary printed by script:
- Universal Train size: **6064**
- Universal Test size: **16050**
- Baseline threshold test accuracy: **0.69**
- XGBoost test accuracy: **0.80**
- Baseline weighted F1: **0.69**
- XGBoost weighted F1: **0.80**

Interpretation:
- On the available universal held-out split, XGBoost improves classification quality for hard/easy routing by about **+0.11 absolute accuracy** and **+0.11 weighted F1** over threshold baseline.

## 4) Important honesty notes

- The MEWSLI candidate file and XGB JSON were confirmed on the server, and the server run produced a verified MEWSLI XGB score.
- If you want a larger, more defensible MEWSLI evaluation, we still need a larger labeled test artifact than the 3-record OOD sample.
