import zipfile
import os
import sys

print("=" * 80)
print("Option B: Regenerate .mentions.new files with CORRECTED OFFSETS from source")
print("=" * 80)

# Setup
zip_path = "__xlwikifier_wikidata.zip"
output_dir = "__mentions_new_corrected"
os.makedirs(output_dir, exist_ok=True)

langs = ['de', 'es', 'fr', 'it']

def normalize(text):
    text = (text or '').strip().replace('_', ' ')
    import re
    text = re.sub(r'\s+', ' ', text)
    return text.lower()

print("\nStep 1: Reading source data from zip and validating offsets...")
print("-" * 80)

offset_stats = {lang: {'total': 0, 'valid': 0, 'invalid': 0, 'corrupted': []} for lang in langs}
corrected_mentions = {lang: {} for lang in langs}  # {filename: [(start, end, title, q_id), ...]}

with zipfile.ZipFile(zip_path, 'r') as z:
    # For each language, process test set
    for lang in langs:
        print(f"\n[{lang}] Processing mentions...")
        base_path = f"xlwikifier-wikidata/data/{lang}/test/"
        
        # Get all .txt files for this lang/test
        txt_files = [n for n in z.namelist() if n.startswith(base_path) and n.endswith('.txt')]
        
        for txt_file in txt_files:
            mention_file = txt_file.replace('.txt', '.mentions')
            
            if mention_file not in z.namelist():
                continue
            
            # Read text and mentions
            try:
                text = z.read(txt_file).decode('utf-8', errors='ignore')
                mentions_raw = z.read(mention_file).decode('utf-8', errors='ignore').strip()
            except:
                continue
            
            filename = os.path.basename(txt_file).replace('.txt', '')
            corrected_mentions[lang][filename] = []
            
            # Parse mentions and validate offsets
            for line in mentions_raw.split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split('\t')
                if len(parts) < 5:
                    continue
                
                try:
                    start = int(parts[0])
                    end = int(parts[1])
                    title = parts[3]
                    q_id = parts[4]
                    
                    offset_stats[lang]['total'] += 1
                    
                    # Validate: does text[start:end] match title?
                    if 0 <= start <= end <= len(text):
                        extracted = text[start:end]
                        extracted_norm = normalize(extracted)
                        title_norm = normalize(title)
                        
                        if extracted_norm == title_norm:
                            offset_stats[lang]['valid'] += 1
                            corrected_mentions[lang][filename].append((start, end, title, q_id))
                        else:
                            offset_stats[lang]['invalid'] += 1
                            if len(offset_stats[lang]['corrupted']) < 3:
                                offset_stats[lang]['corrupted'].append({
                                    'file': filename, 'title': title, 
                                    'extracted': extracted[:50], 'offsets': (start, end)
                                })
                    else:
                        offset_stats[lang]['invalid'] += 1
                        
                except Exception as e:
                    offset_stats[lang]['invalid'] += 1
        
        total = offset_stats[lang]['total']
        valid = offset_stats[lang]['valid']
        pct = (100.0 * valid / total) if total > 0 else 0
        print(f"  Valid offsets: {valid}/{total} ({pct:.1f}%)")
        if offset_stats[lang]['corrupted']:
            print(f"  Sample corrupted: {offset_stats[lang]['corrupted'][0]['title']}")

print("\n\nStep 2: Creating corrected .mentions.new files...")
print("-" * 80)

# Write corrected mentions files
files_created = 0
for lang in langs:
    output_subdir = os.path.join(output_dir, lang)
    os.makedirs(output_subdir, exist_ok=True)
    
    for filename, mentions_list in corrected_mentions[lang].items():
        if not mentions_list:
            continue
        
        # Sanitize filename for Windows (remove invalid characters)
        safe_filename = filename.replace(':', '_').replace('<', '_').replace('>', '_').replace('"', '_').replace('|', '_').replace('?', '_').replace('*', '_')
        output_file = os.path.join(output_subdir, f"{safe_filename}.mentions.new")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for start, end, title, q_id in mentions_list:
                # Output format matching XLWikifier: start\tend\tis_hard\ttitle\tq_id
                f.write(f"{start}\t{end}\t1\t{title}\t{q_id}\n")
        
        files_created += 1
        if files_created % 500 == 0:
            print(f"  Created {files_created} corrected mention files...")

print(f"\nTotal corrected .mentions.new files: {files_created}")

print("\n\nSUMMARY:")
print("-" * 80)
for lang in langs:
    total = offset_stats[lang]['total']
    valid = offset_stats[lang]['valid']
    pct = (100.0 * valid / total) if total > 0 else 0
    print(f"[{lang}] {valid:5d}/{total:5d} mentions valid ({pct:5.1f}%)")

print("\n" + "=" * 80)
print("Option B preparation complete!")
print(f"Corrected mentions ready at: {output_dir}/")
print("=" * 80)
