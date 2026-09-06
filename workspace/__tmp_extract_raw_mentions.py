import zipfile
import os
import sys

# Fix Unicode output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Extract ONLY raw .mentions files for 4 languages we need (test set only)
zip_path = "__xlwikifier_wikidata.zip"
extract_dir = "__mentions_raw_extracted"

os.makedirs(extract_dir, exist_ok=True)

langs = ['de', 'es', 'fr', 'it']
extracted_count = 0

with zipfile.ZipFile(zip_path, 'r') as z:
    for info in z.infolist():
        # Only extract mentions for test set of our 4 languages
        should_extract = False
        for lang in langs:
            if info.filename.endswith('.mentions') and f'/data/{lang}/test/' in info.filename:
                should_extract = True
                break
        
        if should_extract:
            z.extract(info, extract_dir)
            extracted_count += 1
            if extracted_count <= 10:
                fname = os.path.basename(info.filename)
                print(f"Extracted [{lang}]: {fname}")

print(f"\nTotal raw .mentions files extracted: {extracted_count}")
print("Extraction complete!")
