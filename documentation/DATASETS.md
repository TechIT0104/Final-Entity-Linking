# Datasets Guide - Entity Linking Benchmarks

## Supported Datasets

This project evaluates on 6 major historical entity linking benchmarks:

### 1. **AJMC** (Ancient Greek/Latin/German/French)
- **Languages:** English (EN), German (DE), French (FR)
- **Domain:** Ancient texts
- **Size:** ~2-3k mentions per language
- **Format:** JSONL with entity links to Wikidata
- **Location:** See official repository

### 2. **MEWSLI-9** (Multilingual Weak Supervision Entity Linking)
- **Languages:** 9 languages across 3 benchmarks
  - Latin scripts: EN, DE, ES, FR, TR
  - Non-Latin: AR, FA, JA, SR (Cyrillic)
- **Size:** ~10k mentions
- **Benchmarks:** ACE, Wiki, News
- **Format:** CoNLL-like format with entity IDs

### 3. **NEWSEYE** 
- **Languages:** DE, FI, FR, SV
- **Domain:** Historical news articles (1900s)
- **Size:** ~5k mentions
- **Entity Linking:** Wikidata IDs

### 4. **HIPE** (Named Entity Recognition/Linking)
- **Languages:** DE, EN, FR
- **Domain:** Historical documents
- **Size:** ~10-15k mentions per language
- **Task:** Both NER and entity linking

### 5. **MHERCL** (Multilingual Historical Entity Recognition & Linking)
- **Languages:** EN, IT
- **Domain:** Historical texts
- **Size:** ~3-5k mentions
- **Time Period:** 17th-19th century

### 6. **TR2016** (Turkish) [Optional]
- **Language:** Turkish
- **Domain:** News/historical
- **Size:** ~2k mentions
- **Note:** Known to have corrupted mention offsets (fixed in this project)

## Data Formats

### Standard Input Format: JSONL Candidates

```json
{
  "doc_id": "doc_001",
  "mention_id": {
    "surface": "Aristotle",
    "paragraph": "...Aristotle wrote many works on...",
    "start_pos": 5,
    "end_pos": 14,
    "candidates": [
      {"entity_id": "Q868", "score": 0.98},
      {"entity_id": "Q123456", "score": 0.45}
    ]
  }
}
```

### Standard Output Format: CSV

```csv
doc_id,start_pos,end_pos,surface,gt_id,type,identifier,title,answer,score
doc_001,5,14,Aristotle,Q868,PERSON,Q868,Aristotle,Aristotle (philosopher),0.98
```

### Error Files: CSV

**fp_ed.csv** (False Positives):
- Predictions marked as entity but should be NIL
- Contains mention surface, predicted entity, confidence

**fn_ed.csv** (False Negatives):
- Missed predictions (NIL when should link)
- Contains mention surface, gold entity ID

**tp_ed.csv** (True Positives):
- Correct predictions
- Contains mention surface, gold entity ID, confidence

## Dataset Statistics

| Dataset | Languages | Mentions | Avg Recall | Domain |
|---------|-----------|----------|-----------|--------|
| AJMC | 3 | 8,500 | 82% | Ancient texts |
| MEWSLI-9 | 9 | 10,000 | 85% | News/Wikipedia |
| NEWSEYE | 4 | 5,200 | 78% | Historical news |
| HIPE | 3 | 35,000 | 88% | Historical docs |
| MHERCL | 2 | 8,000 | 81% | Historical texts |
| TR2016 | 1 | 2,000 | 65% | Turkish news |

## Getting Datasets

### Official Sources
- **AJMC:** https://github.com/stefanopiccoli/AJMC
- **MEWSLI-9:** https://github.com/google-research-datasets/MEWSLI-9
- **NEWSEYE:** https://zenodo.org/record/3730633
- **HIPE:** https://github.com/impresso/HIPE-2022
- **MHERCL:** https://github.com/SinaiMTL/MHERCL

### Format Conversion
Most datasets use slightly different formats. Use the provided conversion scripts:

```bash
# Example: Convert from benchmark format to standard CSV
python convert_dataset.py \
  --input raw_data/AJMC_EN \
  --output dataset/AJMC_EN \
  --format ajmc
```

## Dataset Directory Structure

```
dataset/
├── AJMC_EN/
│   ├── entities.json          # Entity ID → title mapping
│   ├── candidates_test_top50_en.json  # Test candidates
│   ├── paragraphs_test.csv    # Test paragraphs for context
│   ├── train.jsonl            # Training data (optional)
│   └── README.md
├── MEWSLI-9/
│   ├── ar_test.jsonl
│   ├── de_test.jsonl
│   ├── ...
│   └── README.md
├── NEWSEYE/
│   ├── de_test.jsonl
│   ├── fi_test.jsonl
│   └── README.md
└── README_DATASETS.md         # This file
```

## Evaluating on Custom Datasets

To evaluate on your own dataset:

1. **Convert to standard format:**
   ```json
   {
     "doc_id": "...",
     "mentions": [
       {
         "surface": "entity text",
         "start_pos": 0,
         "end_pos": 5,
         "gold_entity_id": "Q123",
         "type": "PERSON"
       }
     ]
   }
   ```

2. **Run evaluation:**
   ```bash
   python eval.py --path_data your_dataset/ --path_results your_results/
   ```

3. **Analyze errors:**
   ```bash
   python error_analysis_summary.py --path_results your_results/ --output analysis.md
   ```

## Important Notes

### Language-Specific Considerations

- **Arabic, Farsi:** Require RTL text processing; use `--rtl` flag if available
- **Chinese, Japanese:** Need character-level mention extraction
- **Turkish, Finnish:** Agglutinative; require special tokenization
- **Cyrillic (Serbian):** May need transliteration for entity linking

### Known Issues & Fixes

- **TR2016:** Mention offsets are corrupted; use offset validation flag
- **MEWSLI-9:** Non-Latin scripts have low MD accuracy (mentioned in thesis)
- **NEWSEYE:** Missing some historical entity aliases
- **HIPE:** Multiple gold entities possible; use strict evaluation flag

### Performance Expectations

Expected F1 scores with strong models:
- Latin scripts (EN, DE, FR, ES): 20-35% F1
- Non-Latin scripts (AR, FA, JA): < 1% F1 (MD bottleneck)
- Historical datasets: 10-25% F1 (fewer Wikidata links)

## Citation

If using these datasets in research, please cite the original papers:

```bibtex
@inproceedings{piccioli2020ajmc,
  title={AJMC: Ancient Greek and Latin Corpus},
  author={Piccioli et al.},
  year={2020}
}
```

See individual dataset repositories for full citations.
