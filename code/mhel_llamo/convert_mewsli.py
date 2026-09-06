import os
import pandas as pd

def convert_mewsli_to_hipe(base_dir, out_dir):
    """Converts the internal mewsli TSV schema to the HIPE CSV schema for BELA."""
    # We will process English just to test Out-of-Distribution
    lang_dir = os.path.join(base_dir, "en")
    mentions_path = os.path.join(lang_dir, "mentions.tsv")
    docs_path = os.path.join(lang_dir, "docs.tsv")
    
    print("Loading Mewsli TSV files...")
    df_mentions = pd.read_csv(mentions_path, sep='\t')
    df_docs = pd.read_csv(docs_path, sep='\t')
    
    # 1. Convert Annotations
    hipe_annotations = []
    for _, row in df_mentions.iterrows():
        start_pos = int(row['position'])
        end_pos = start_pos + int(row['length'])
        hipe_annotations.append({
            "doc_id": row['docid'],
            "surface": row['mention'],
            "start_pos": start_pos,
            "end_pos": end_pos,
            "type": "UNK",  # Mewsli does not provide NER type
            "identifier": row['qid']
        })
    
    df_anno = pd.DataFrame(hipe_annotations)
    
    # 2. Convert Paragraphs (Docs)
    hipe_docs = []
    for _, row in df_docs.iterrows():
        # Handle whatever column names Mewsli uses for docs.tsv
        cols = list(row.index)
        docid_col = 'docid' if 'docid' in cols else cols[0]
        text_col = 'text' if 'text' in cols else cols[-1]
        
        hipe_docs.append({
            "doc_id": row[docid_col],
            "text": row[text_col]
        })
        
    df_paras = pd.DataFrame(hipe_docs)
    
    # 3. Save to HIPE format
    output_target = os.path.join(out_dir, "MEWSLI_EN")
    os.makedirs(output_target, exist_ok=True)
    
    df_anno.to_csv(os.path.join(output_target, "annotations_test.csv"), index=False)
    df_paras.to_csv(os.path.join(output_target, "paragraphs_test.csv"), index=False)
    
    print(f"Success! Saved HIPE-formatted Mewsli dataset to: {output_target}")
    print(f"Total annotations converted: {len(df_anno)}")
    print(f"Total documents converted: {len(df_paras)}")

if __name__ == "__main__":
    convert_mewsli_to_hipe("/DATA/kmpooja/mrefined_option1/assets/mewsli_9_el_datasets", "test_data")