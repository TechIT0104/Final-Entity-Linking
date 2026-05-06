# Error Analysis Summary

Results folder: results\AJMC_EN\mistral_24B_chain_k50_en

## Metrics (from result.txt)
- Accuracy: 47.019867549668874

## Counts
- True Positives: 71
- False Positives: 80
- False Negatives: 80

## False Positives
Top types:
- WORK: 62
- PER: 18

Top mentions:
- Ph.: 6
- Ant.: 4
- El.: 4
- Phil.: 3
- O. T.: 3
- 1].: 2
- Ag.: 2
- Ajax: 2
- Sophocles: 2
- Pind. P.: 2

NIL predictions in FP: 59
Avg mention length in FP: 6.16 (median 5.00, min 3, max 17)

## False Negatives
Top types:
- WORK: 62
- PER: 18

Top mentions:
- Ph.: 6
- Ant.: 4
- El.: 4
- Phil.: 3
- O. T.: 3
- 1].: 2
- Ag.: 2
- Ajax: 2
- Sophocles: 2
- Pind. P.: 2

Avg mention length in FN: 6.16 (median 5.00, min 3, max 17)

## Notes
- Consider inspecting FP/FN rows with long mentions or NIL-heavy errors.
- Use these counts to justify threshold or reranking changes.
