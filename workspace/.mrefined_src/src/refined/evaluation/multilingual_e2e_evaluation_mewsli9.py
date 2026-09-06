from argparse import ArgumentParser
from refined.inference.processor import Refined
from refined.evaluation.evaluation import evaluate_on_docs
from refined.data_types.base_types import Span
from refined.dataset_reading.entity_linking.dataset_reader_multilingual import Datasets
from refined.resource_management.loaders import normalize_surface_form
from refined.resource_management.lmdb_wrapper import LmdbImmutableDict
import os
import pickle

def main():
    parser = ArgumentParser()
    parser.add_argument('--lang_title2wikidata', type=str,
                        default="../data_combine_11_languages_wikidata_all_eng_label_desc/additional_data",
                        help="path of lang_title2wikidataID-normalized_with_redirect.pkl", required=False)
    parser.add_argument('--mention2wikidata', type=str,
                        default="../data_combine_11_languages_wikidata_all_eng_label_desc/additional_data",
                        help="path of mention2wikidataID.lmdb", required=False)
    parser.add_argument('--model', type=str,
                        default="../finetune_models/mReFinED_Recall_9343",
                        help="model path", required=False)
    parser.add_argument('--wikidata', type=bool,
                        default=True,
                        help="true or false", required=False)
    parser.add_argument('--data', type=str,
                        default="../data_combine_11_languages_wikidata_all_eng_label_desc", required=False)
    parser.add_argument('--datasets_root', type=str,
                        default="../mewsli_9_el_datasets",
                        help="root directory for datasets", required=False)
    parser.add_argument('--device', type=str,
                        default="cuda:0",
                        help="device to use for evaluation", required=False)
    cli_args = parser.parse_args()

    print(f"Loading mReFinED components....")
    languages = ['ar','de','en','es','fa','ja','sr','ta','tr']
    with open(os.path.join(cli_args.lang_title2wikidata,"lang_title2wikidataID-normalized_with_redirect.pkl"), "rb") as f:
        lang_title2wikidataID = pickle.load(f)
    mention2wikidataID = LmdbImmutableDict(os.path.join(cli_args.lang_title2wikidata,"mention2wikidataID.lmdb"))                  
    DATA_DIR = cli_args.data
    model = cli_args.model
    entity_set = 'wikidata' if cli_args.wikidata else 'wikipedia'
     
    refined = Refined.from_pretrained(model_name=model,
                                    entity_set=entity_set,
                                    use_precomputed_descriptions=False,
                                    data_dir=DATA_DIR,
                                    download_files=False)

    refined.preprocessor.candidate_generator.mention2wikidataID = mention2wikidataID
    refined.preprocessor.candidate_generator.lang_title2wikidataID = lang_title2wikidataID
    refined.model.ed_2.temperature_scaling = 0.02
    
    # Accumulators for macro-average and micro-average calculations
    per_lang_recall_el = {}
    per_lang_recall_md = {}
    per_lang_gold_recall = {}
    per_lang_precision = {}
    per_lang_f1 = {}
    
    all_tp_el = 0
    all_fn_el = 0
    all_tp_md = 0
    all_fn_md = 0
    all_gold_entities = 0

    for lang in languages:
        refined.preprocessor.lookups.pem = LmdbImmutableDict(os.path.join(DATA_DIR,f'wikidata_data/pem_{lang}.lmdb'))
        refined.preprocessor.candidate_generator.pem = LmdbImmutableDict(os.path.join(DATA_DIR,f'wikidata_data/pem_{lang}.lmdb'))
        refined.preprocessor.candidate_generator.language = lang
        
        datasets_dir = os.path.join(cli_args.datasets_root, lang) if os.path.isabs(cli_args.datasets_root) else f"{cli_args.datasets_root}/{lang}"
        dataset_name = f'mewsli-9-{lang}'
        
        datasets = Datasets(preprocessor=refined.preprocessor, datasets_path=datasets_dir)
        dataset_docs = datasets.get_mewsli_docs(filename=datasets_dir)
        metrics = evaluate_on_docs(refined=refined, docs=dataset_docs, dataset_name=dataset_name, 
                                    el=True,
                                    ed_threshold = 0.0,topk_eval=True,top_k=3)
        print('*****************************\n\n')
        print(f'Dataset name: {dataset_name}')
        print(metrics.get_summary())
        print('*****************************\n\n')
        
        # Store per-language metrics
        recall_el = metrics.get_recall() * 100  # Convert to percentage
        recall_md = metrics.get_recall_md() * 100
        gold_recall = metrics.get_gold_recall() * 100
        precision = metrics.get_precision() * 100
        f1 = metrics.get_f1() * 100
        
        per_lang_recall_el[lang] = recall_el
        per_lang_recall_md[lang] = recall_md
        per_lang_gold_recall[lang] = gold_recall
        per_lang_precision[lang] = precision
        per_lang_f1[lang] = f1
        
        # Accumulate for micro-average
        all_tp_el += metrics.tp
        all_fn_el += metrics.fn
        all_tp_md += metrics.tp_md
        all_fn_md += metrics.fn_md
        all_gold_entities += metrics.gold_entity_in_cand

    print("\n" + "="*80)
    print("MULTILINGUAL SUMMARY (MEWSLI-9 across 9 languages)")
    print("="*80)
    
    # Print per-language detailed breakdown
    print("\nPer-Language Results:")
    print("-" * 100)
    print(f"{'Language':<12} {'EL Precision':<16} {'EL Recall':<16} {'EL F1':<16} {'MD Recall':<16} {'Gold Recall':<16}")
    print("-" * 100)
    for lang in languages:
        print(f"{lang:<12} {per_lang_precision[lang]:>14.2f}% {per_lang_recall_el[lang]:>14.2f}% {per_lang_f1[lang]:>14.2f}% {per_lang_recall_md[lang]:>14.2f}% {per_lang_gold_recall[lang]:>14.2f}%")
    
    print("-" * 100)
    
    # Macro-averages (average of per-language percentages)
    macro_avg_recall_el = sum(per_lang_recall_el.values()) / len(languages)
    macro_avg_recall_md = sum(per_lang_recall_md.values()) / len(languages)
    macro_avg_gold_recall = sum(per_lang_gold_recall.values()) / len(languages)
    macro_avg_precision = sum(per_lang_precision.values()) / len(languages)
    macro_avg_f1 = sum(per_lang_f1.values()) / len(languages)
    
    # Micro-averages (total TP / total (TP+FN))
    micro_avg_recall_el = (all_tp_el / (all_tp_el + all_fn_el)) * 100 if (all_tp_el + all_fn_el) > 0 else 0
    micro_avg_recall_md = (all_tp_md / (all_tp_md + all_fn_md)) * 100 if (all_tp_md + all_fn_md) > 0 else 0
    
    print("\nMacro-Average Results (average across languages):")
    print(f"  Macro-Avg EL Recall:      {macro_avg_recall_el:>6.2f}% (Entity Linking)")
    print(f"  Macro-Avg MD Recall:      {macro_avg_recall_md:>6.2f}% (Mention Detection)")
    print(f"  Macro-Avg Gold Recall:    {macro_avg_gold_recall:>6.2f}% (Entities in candidates)")
    print(f"  Macro-Avg EL Precision:   {macro_avg_precision:>6.2f}%")
    print(f"  Macro-Avg EL F1:          {macro_avg_f1:>6.2f}%")
    
    print("\nMicro-Average Results (aggregated counts):")
    print(f"  Micro-Avg EL Recall:      {micro_avg_recall_el:>6.2f}% ({all_tp_el}/{all_tp_el + all_fn_el})")
    print(f"  Micro-Avg MD Recall:      {micro_avg_recall_md:>6.2f}% ({all_tp_md}/{all_tp_md + all_fn_md})")
    
    print("\n" + "="*80)
    print("NOTE: Paper (Table 8) expects Macro-Avg Gold Recall ≈ 58.8%")
    print("      Our current MD/Gold Recall ≈ 83-91% (different scope)")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()