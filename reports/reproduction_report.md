# MHEL-LLaMo — Paper Reproduction Report
This report compares the paper/README best-setting scores against the run artifacts currently in `results/`.
- Runs checked: **12**
- Matched within tolerance (±0.01): **12/12**

## Table
| Dataset | Lang | Expected (paper) | Observed (from result.txt) | Δ | Status | Run folder |
|---|---:|---:|---:|---:|---:|---|
| HIPE-2020 | de | 0.620 | 0.620 | 0.000 | OK | `results/HIPE_DE/mistral_24B_chain_median_k30_de` |
| HIPE-2020 | en | 0.723 | 0.723 | 0.000 | OK | `results/HIPE_EN/mistral_24B_chain_k20_en` |
| HIPE-2020 | fr | 0.692 | 0.692 | -0.000 | OK | `results/HIPE_FR/mistral_24B_van_k20_fr` |
| NewsEye | de | 0.556 | 0.556 | 0.000 | OK | `results/NEWSEYE_DE/mistral_24B_chain_k30_de` |
| NewsEye | fi | 0.509 | 0.509 | 0.000 | OK | `results/NEWSEYE_FI/poro2_8B_chain_k20_fi` |
| NewsEye | fr | 0.662 | 0.662 | 0.000 | OK | `results/NEWSEYE_FR/mistral_24B_chain_median_k20_fr` |
| NewsEye | sv | 0.521 | 0.521 | 0.000 | OK | `results/NEWSEYE_SV/gemma_27B_chain_median_k20_sv` |
| AJMC | de | 0.521 | 0.521 | -0.000 | OK | `results/AJMC_DE/mistral_24B_van_k50_de` |
| AJMC | en | 0.496 | 0.497 | 0.001 | OK | `results/AJMC_EN/mistral_24B_van_k50_en` |
| AJMC | fr | 0.635 | 0.635 | 0.000 | OK | `results/AJMC_FR/mistral_24B_van_k20_fr` |
| MHERCL | en | 0.700 | 0.705 | 0.005 | OK | `results/MHERCL_EN/mistral_24B_chain_k20_en` |
| MHERCL | it | 0.698 | 0.698 | -0.000 | OK | `results/MHERCL_IT/mistral_24B_chain_k20_it` |
