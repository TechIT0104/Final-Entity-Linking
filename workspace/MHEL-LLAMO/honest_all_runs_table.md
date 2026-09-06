# Honest Evaluation (All Runs Found)
This table scans `results/*/*/output.csv` and computes both legacy and strict metrics.

| Dataset | Run | Paper score | Strict F1 | Coverage | Gold N | Pred uniq | Pred rows | Missing gold | Extra pred | Folder |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| AJMC_DE | mistral_24B_chain_k50_de | 0.485 | 0.474 | 0.955 | 177 | 169 | 169 | 8 | 0 | `results\AJMC_DE\mistral_24B_chain_k50_de` |
| AJMC_DE | mistral_24B_chain_median_k50_de | 0.479 | 0.468 | 0.955 | 177 | 169 | 169 | 8 | 0 | `results\AJMC_DE\mistral_24B_chain_median_k50_de` |
| AJMC_DE | mistral_24B_ens_median_k50_de | 0.521 | 0.509 | 0.955 | 177 | 169 | 169 | 8 | 0 | `results\AJMC_DE\mistral_24B_ens_median_k50_de` |
| AJMC_DE | mistral_24B_van_k50_de | 0.521 | 0.509 | 0.955 | 177 | 169 | 169 | 8 | 0 | `results\AJMC_DE\mistral_24B_van_k50_de` |
| AJMC_EN | mistral_24B_chain_k50_en | 0.470 | 0.463 | 0.968 | 156 | 151 | 151 | 5 | 0 | `results\AJMC_EN\mistral_24B_chain_k50_en` |
| AJMC_EN | mistral_24B_chain_median_k50_en | 0.464 | 0.456 | 0.968 | 156 | 151 | 151 | 5 | 0 | `results\AJMC_EN\mistral_24B_chain_median_k50_en` |
| AJMC_EN | mistral_24B_ens_median_k50_en | 0.477 | 0.469 | 0.968 | 156 | 151 | 151 | 5 | 0 | `results\AJMC_EN\mistral_24B_ens_median_k50_en` |
| AJMC_EN | mistral_24B_van_k50_en | 0.497 | 0.489 | 0.968 | 156 | 151 | 151 | 5 | 0 | `results\AJMC_EN\mistral_24B_van_k50_en` |
| AJMC_FR | mistral_24B_chain_k20_fr | 0.570 | 0.551 | 0.935 | 214 | 200 | 200 | 14 | 0 | `results\AJMC_FR\mistral_24B_chain_k20_fr` |
| AJMC_FR | mistral_24B_chain_median_k20_fr | 0.570 | 0.551 | 0.935 | 214 | 200 | 200 | 14 | 0 | `results\AJMC_FR\mistral_24B_chain_median_k20_fr` |
| AJMC_FR | mistral_24B_ens_median_k20_fr | 0.600 | 0.580 | 0.935 | 214 | 200 | 200 | 14 | 0 | `results\AJMC_FR\mistral_24B_ens_median_k20_fr` |
| AJMC_FR | mistral_24B_van_k20_fr | 0.635 | 0.614 | 0.935 | 214 | 200 | 200 | 14 | 0 | `results\AJMC_FR\mistral_24B_van_k20_fr` |
| HIPE_DE | mistral_24B_chain_k30_de | 0.587 | 0.586 | 0.994 | 1089 | 1083 | 1083 | 6 | 0 | `results\HIPE_DE\mistral_24B_chain_k30_de` |
| HIPE_DE | mistral_24B_chain_median_k30_de | 0.620 | 0.619 | 0.994 | 1089 | 1083 | 1083 | 6 | 0 | `results\HIPE_DE\mistral_24B_chain_median_k30_de` |
| HIPE_DE | mistral_24B_ens_median_k30_de | 0.619 | 0.617 | 0.994 | 1089 | 1083 | 1083 | 6 | 0 | `results\HIPE_DE\mistral_24B_ens_median_k30_de` |
| HIPE_DE | mistral_24B_van_k30_de | 0.616 | 0.614 | 0.994 | 1089 | 1083 | 1083 | 6 | 0 | `results\HIPE_DE\mistral_24B_van_k30_de` |
| HIPE_EN | mistral_24B_chain_k20_en | 0.723 | 0.708 | 0.960 | 425 | 408 | 408 | 17 | 0 | `results\HIPE_EN\mistral_24B_chain_k20_en` |
| HIPE_EN | mistral_24B_chain_median_k20_en | 0.686 | 0.672 | 0.960 | 425 | 408 | 408 | 17 | 0 | `results\HIPE_EN\mistral_24B_chain_median_k20_en` |
| HIPE_EN | mistral_24B_ens_median_k20_en | 0.615 | 0.603 | 0.960 | 425 | 408 | 408 | 17 | 0 | `results\HIPE_EN\mistral_24B_ens_median_k20_en` |
| HIPE_EN | mistral_24B_van_k20_en | 0.672 | 0.658 | 0.960 | 425 | 408 | 408 | 17 | 0 | `results\HIPE_EN\mistral_24B_van_k20_en` |
| HIPE_FR | mistral_24B_chain_k20_fr | 0.679 | 0.676 | 0.992 | 1535 | 1522 | 1522 | 13 | 0 | `results\HIPE_FR\mistral_24B_chain_k20_fr` |
| HIPE_FR | mistral_24B_chain_median_k20_fr | 0.687 | 0.684 | 0.992 | 1535 | 1522 | 1522 | 13 | 0 | `results\HIPE_FR\mistral_24B_chain_median_k20_fr` |
| HIPE_FR | mistral_24B_ens_median_k20_fr | 0.672 | 0.669 | 0.992 | 1535 | 1522 | 1522 | 13 | 0 | `results\HIPE_FR\mistral_24B_ens_median_k20_fr` |
| HIPE_FR | mistral_24B_van_k20_fr | 0.692 | 0.689 | 0.992 | 1535 | 1522 | 1522 | 13 | 0 | `results\HIPE_FR\mistral_24B_van_k20_fr` |
| MHERCL_EN | mistral_24B_chain_k20_en | 0.705 | 0.705 | 1.000 | 2311 | 2311 | 2311 | 0 | 0 | `results\MHERCL_EN\mistral_24B_chain_k20_en` |
| MHERCL_EN | mistral_24B_chain_median_k20_en | 0.667 | 0.667 | 1.000 | 2311 | 2311 | 2311 | 0 | 0 | `results\MHERCL_EN\mistral_24B_chain_median_k20_en` |
| MHERCL_EN | mistral_24B_ens_median_k20_en | 0.649 | 0.649 | 1.000 | 2311 | 2311 | 2311 | 0 | 0 | `results\MHERCL_EN\mistral_24B_ens_median_k20_en` |
| MHERCL_EN | mistral_24B_van_k20_en | 0.703 | 0.703 | 1.000 | 2311 | 2311 | 2311 | 0 | 0 | `results\MHERCL_EN\mistral_24B_van_k20_en` |
| MHERCL_IT | mistral_24B_chain_k20_it | 0.698 | 0.698 | 1.000 | 2334 | 2334 | 2334 | 0 | 0 | `results\MHERCL_IT\mistral_24B_chain_k20_it` |
| MHERCL_IT | mistral_24B_chain_median_k20_it | 0.629 | 0.629 | 1.000 | 2334 | 2334 | 2334 | 0 | 0 | `results\MHERCL_IT\mistral_24B_chain_median_k20_it` |
| MHERCL_IT | mistral_24B_ens_median_k20_it | 0.627 | 0.627 | 1.000 | 2334 | 2334 | 2334 | 0 | 0 | `results\MHERCL_IT\mistral_24B_ens_median_k20_it` |
| MHERCL_IT | mistral_24B_van_k20_it | 0.685 | 0.685 | 1.000 | 2334 | 2334 | 2334 | 0 | 0 | `results\MHERCL_IT\mistral_24B_van_k20_it` |
| NEWSEYE_DE | mistral_24B_chain_k30_de | 0.556 | 0.555 | 0.997 | 2230 | 2224 | 2224 | 6 | 0 | `results\NEWSEYE_DE\mistral_24B_chain_k30_de` |
| NEWSEYE_DE | mistral_24B_chain_median_k30_de | 0.556 | 0.555 | 0.997 | 2230 | 2224 | 2224 | 6 | 0 | `results\NEWSEYE_DE\mistral_24B_chain_median_k30_de` |
| NEWSEYE_DE | mistral_24B_ens_median_k30_de | 0.444 | 0.444 | 0.997 | 2230 | 2224 | 2224 | 6 | 0 | `results\NEWSEYE_DE\mistral_24B_ens_median_k30_de` |
| NEWSEYE_DE | mistral_24B_van_k30_de | 0.488 | 0.487 | 0.997 | 2230 | 2224 | 2224 | 6 | 0 | `results\NEWSEYE_DE\mistral_24B_van_k30_de` |
| NEWSEYE_FI | poro2_8B_chain_k20_fi | 0.509 | 0.490 | 0.928 | 654 | 607 | 607 | 47 | 0 | `results\NEWSEYE_FI\poro2_8B_chain_k20_fi` |
| NEWSEYE_FI | poro2_8B_chain_median_k20_fi | 0.479 | 0.462 | 0.928 | 654 | 607 | 607 | 47 | 0 | `results\NEWSEYE_FI\poro2_8B_chain_median_k20_fi` |
| NEWSEYE_FI | poro2_8B_ens_median_k20_fi | 0.453 | 0.436 | 0.928 | 654 | 607 | 607 | 47 | 0 | `results\NEWSEYE_FI\poro2_8B_ens_median_k20_fi` |
| NEWSEYE_FI | poro2_8B_van_k20_fi | 0.470 | 0.452 | 0.928 | 654 | 607 | 607 | 47 | 0 | `results\NEWSEYE_FI\poro2_8B_van_k20_fi` |
| NEWSEYE_FR | mistral_24B_chain_k20_fr | 0.647 | 0.645 | 0.994 | 2344 | 2329 | 2329 | 15 | 0 | `results\NEWSEYE_FR\mistral_24B_chain_k20_fr` |
| NEWSEYE_FR | mistral_24B_chain_median_k20_fr | 0.662 | 0.660 | 0.994 | 2344 | 2329 | 2329 | 15 | 0 | `results\NEWSEYE_FR\mistral_24B_chain_median_k20_fr` |
| NEWSEYE_FR | mistral_24B_ens_median_k20_fr | 0.584 | 0.582 | 0.994 | 2344 | 2329 | 2329 | 15 | 0 | `results\NEWSEYE_FR\mistral_24B_ens_median_k20_fr` |
| NEWSEYE_FR | mistral_24B_van_k20_fr | 0.593 | 0.591 | 0.994 | 2344 | 2329 | 2329 | 15 | 0 | `results\NEWSEYE_FR\mistral_24B_van_k20_fr` |
| NEWSEYE_SV | gemma_27B_chain_k20_sv | 0.518 | 0.518 | 1.000 | 587 | 587 | 587 | 0 | 0 | `results\NEWSEYE_SV\gemma_27B_chain_k20_sv` |
| NEWSEYE_SV | gemma_27B_chain_median_k20_sv | 0.521 | 0.521 | 1.000 | 587 | 587 | 587 | 0 | 0 | `results\NEWSEYE_SV\gemma_27B_chain_median_k20_sv` |
| NEWSEYE_SV | gemma_27B_ens_median_k20_sv | 0.504 | 0.504 | 1.000 | 587 | 587 | 587 | 0 | 0 | `results\NEWSEYE_SV\gemma_27B_ens_median_k20_sv` |
| NEWSEYE_SV | gemma_27B_van_k20_sv | 0.504 | 0.504 | 1.000 | 587 | 587 | 587 | 0 | 0 | `results\NEWSEYE_SV\gemma_27B_van_k20_sv` |
