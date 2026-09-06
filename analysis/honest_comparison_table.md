# Honest Paper Evaluation (Best Settings)
This report evaluates the *existing* run artifacts under `results/` for the paper’s reported best settings.

## Metrics
- **Paper/legacy score**: matches the repo’s original scoring used for the published table (tp/(tp+fp) on joined rows).
- **Strict micro-F1/accuracy**: correct predictions / total gold mentions (doc_id+start_pos join).

## Table
| Dataset | Lang | Paper expected | Paper score | Δ | Strict F1 | Coverage | Gold N | Pred uniq | Pred rows | Missing gold | Extra pred | Run folder |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| HIPE_DE | de | 0.620 | 0.620 | 0.000 | 0.619 | 0.994 | 1089 | 1083 | 1083 | 6 | 0 | `results/HIPE_DE/mistral_24B_chain_median_k30_de` |
| HIPE_EN | en | 0.723 | 0.723 | 0.000 | 0.708 | 0.960 | 425 | 408 | 408 | 17 | 0 | `results/HIPE_EN/mistral_24B_chain_k20_en` |
| HIPE_FR | fr | 0.692 | 0.692 | -0.000 | 0.689 | 0.992 | 1535 | 1522 | 1522 | 13 | 0 | `results/HIPE_FR/mistral_24B_van_k20_fr` |
| NEWSEYE_DE | de | 0.556 | 0.556 | 0.000 | 0.555 | 0.997 | 2230 | 2224 | 2224 | 6 | 0 | `results/NEWSEYE_DE/mistral_24B_chain_k30_de` |
| NEWSEYE_FI | fi | 0.509 | 0.509 | 0.000 | 0.490 | 0.928 | 654 | 607 | 607 | 47 | 0 | `results/NEWSEYE_FI/poro2_8B_chain_k20_fi` |
| NEWSEYE_FR | fr | 0.662 | 0.662 | 0.000 | 0.660 | 0.994 | 2344 | 2329 | 2329 | 15 | 0 | `results/NEWSEYE_FR/mistral_24B_chain_median_k20_fr` |
| NEWSEYE_SV | sv | 0.521 | 0.521 | 0.000 | 0.521 | 1.000 | 587 | 587 | 587 | 0 | 0 | `results/NEWSEYE_SV/gemma_27B_chain_median_k20_sv` |
| AJMC_DE | de | 0.521 | 0.521 | -0.000 | 0.509 | 0.955 | 177 | 169 | 169 | 8 | 0 | `results/AJMC_DE/mistral_24B_van_k50_de` |
| AJMC_EN | en | 0.496 | 0.497 | 0.001 | 0.489 | 0.968 | 156 | 151 | 151 | 5 | 0 | `results/AJMC_EN/mistral_24B_van_k50_en` |
| AJMC_FR | fr | 0.635 | 0.635 | 0.000 | 0.614 | 0.935 | 214 | 200 | 200 | 14 | 0 | `results/AJMC_FR/mistral_24B_van_k20_fr` |
| MHERCL_EN | en | 0.700 | 0.705 | 0.005 | 0.705 | 1.000 | 2311 | 2311 | 2311 | 0 | 0 | `results/MHERCL_EN/mistral_24B_chain_k20_en` |
| MHERCL_IT | it | 0.698 | 0.698 | -0.000 | 0.698 | 1.000 | 2334 | 2334 | 2334 | 0 | 0 | `results/MHERCL_IT/mistral_24B_chain_k20_it` |

## Summary
- Paper-score matched (±0.01): **12/12**
- Strict coverage ~1.0: **3/12**
