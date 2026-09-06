#!/usr/bin/env python3
"""
Script to organize files for Multilingual Entity Linking project.
Copies necessary files and removes unwanted ones.
"""
import os
import shutil
from pathlib import Path

source_dir = Path(r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking")
target_dir = Path(r"c:\Users\Dhruv\OneDrive\Desktop\Multilingual entity linking")

# Define what to copy
FILES_TO_COPY = {
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\MEWSLI9_DETAILED_PROBLEMS_AND_SOLUTIONS.txt": 
        r"c:\Users\Dhruv\OneDrive\Desktop\Multilingual entity linking\Documentation",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\MEWSLI9_RESULTS_SUMMARY.md": 
        r"c:\Users\Dhruv\OneDrive\Desktop\Multilingual entity linking\Documentation",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\MANUAL_TR2016_COMMANDS.txt": 
        r"c:\Users\Dhruv\OneDrive\Desktop\Multilingual entity linking\Documentation",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\TR2016_EVALUATION_REPORT.txt": 
        r"c:\Users\Dhruv\OneDrive\Desktop\Multilingual entity linking\Documentation",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\TR2016_EXECUTION_GUIDE.txt": 
        r"c:\Users\Dhruv\OneDrive\Desktop\Multilingual entity linking\Documentation",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\PAPER_REPRODUCTION_FINAL_REPORT.txt":
        r"c:\Users\Dhruv\OneDrive\Desktop\Multilingual entity linking\Documentation",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\tr2016_executor_paramiko.py":
        r"c:\Users\Dhruv\OneDrive\Desktop\Multilingual entity linking\EvaluationScripts",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\tr2016_executor.py":
        r"c:\Users\Dhruv\OneDrive\Desktop\Multilingual entity linking\EvaluationScripts",
}

# Define folders to copy (entire directories)
FOLDERS_TO_COPY = {
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\.mrefined_src":
        r"c:\Users\Dhruv\OneDrive\Desktop\Multilingual entity linking\SourceCode\.mrefined_src",
}

# Files to DELETE (unwanted)
FILES_TO_DELETE = [
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\beamercolorthemeComingClean.sty",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\beamercolorthemeConspicuousCreep.sty",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\beamercolorthemeEntrepreneur.sty",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\beamerthemeLLT-poster.sty",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\format.tex",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\report.tex",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\report.aux",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\report.log",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\report.out",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\report.pdf",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\entity_linking_demo.html",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\evaluation_results.html",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\presentation.html",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\Entity_Linking_Board_Presentation.pptx",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\2305.17371.txt",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\2023.findings-emnlp.1007 (1).txt",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\extract_demo_examples.py",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\fix_blink_data.py",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\fix_blink_data_v2.py",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\fix_data_utils.py",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\patch_data_utils.py",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\el_demo_examples.json",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\sync_files.py",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\sync_and_verify.sh",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\sync_and_run_fresh.ps1",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\organize_files.py",
]

# Folders to DELETE (entire directories)
FOLDERS_TO_DELETE = [
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\BLINK",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\MVD",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\results",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\experiments",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\tmp_mrefined",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\_tmp_mrefined",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\_upstream_mrefined",
    r"c:\Users\Dhruv\OneDrive\Desktop\Entity Linking\.mulrel_nel_src",
]

def copy_files():
    """Copy specified files to target directories."""
    print("Copying files to Multilingual entity linking folder...")
    for src, dst in FILES_TO_COPY.items():
        if os.path.exists(src):
            os.makedirs(dst, exist_ok=True)
            shutil.copy2(src, dst)
            print("  OK: {}".format(os.path.basename(src)))
        else:
            print("  SKIP: {} (not found)".format(src))

def copy_folders():
    """Copy entire folders to target directories."""
    print("\nCopying folders to Multilingual entity linking...")
    for src, dst in FOLDERS_TO_COPY.items():
        if os.path.exists(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print("  OK: {} folder copied".format(os.path.basename(src)))
        else:
            print("  SKIP: {} (not found)".format(src))

def delete_unwanted_files():
    """Delete unwanted files from original location."""
    print("\nDeleting unwanted files...")
    count = 0
    for file_path in FILES_TO_DELETE:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                count += 1
            except Exception as e:
                print("  ERROR deleting {}: {}".format(file_path, str(e)))
    print("  Deleted {} files".format(count))

def delete_unwanted_folders():
    """Delete unwanted folders from original location."""
    print("\nDeleting unwanted folders...")
    count = 0
    for folder_path in FOLDERS_TO_DELETE:
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
                count += 1
            except Exception as e:
                print("  ERROR deleting {}: {}".format(folder_path, str(e)))
    print("  Deleted {} folders".format(count))

def create_readme():
    """Create README in the new Multilingual entity linking folder."""
    readme_content = """# Multilingual Entity Linking with mReFinED

This folder contains all necessary files for multilingual entity linking evaluation using the mReFinED model.

## Folder Structure

- **SourceCode/**: Contains the mReFinED source code (.mrefined_src)
- **Documentation/**: Contains detailed documentation and reproduction reports  
- **EvaluationScripts/**: Contains Python scripts for running evaluations

## Key Files

### Documentation
- `MEWSLI9_DETAILED_PROBLEMS_AND_SOLUTIONS.txt` - Detailed technical guide
- `MEWSLI9_RESULTS_SUMMARY.md` - Summary of MEWSLI-9 results
- `PAPER_REPRODUCTION_FINAL_REPORT.txt` - Complete paper reproduction report
- `TR2016_EVALUATION_REPORT.txt` - TR2016 benchmark evaluation report

### Evaluation Scripts
- `tr2016_executor_paramiko.py` - SSH executor for remote evaluation

## Metrics

The evaluation correctly reports:
- **Macro-Avg Recall**: Average of per-language recall percentages
- **Micro-Avg Recall**: Aggregated TP / (TP + FN) across all mentions  
- **EL Recall**: Entity linking (disambiguation) performance
- **MD Recall**: Mention detection performance
- **Gold Recall**: Percentage of gold entities in candidate pool

## Results

- MEWSLI-9 (9 languages): Macro-Avg EL Recall ~15.37%, Gold Recall ~85%
- Paper baseline: Macro-Avg Recall 58.8%, F1 27.6%
- Current F1: ~24.99% (comparable to paper)
"""
    
    readme_path = os.path.join(r"c:\Users\Dhruv\OneDrive\Desktop\Multilingual entity linking", "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("  Created: README.md")

if __name__ == "__main__":
    # Ensure target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files and folders
    copy_files()
    copy_folders()
    
    # Create README
    print("\nCreating documentation...")
    create_readme()
    
    # Delete unwanted files
    delete_unwanted_files()
    delete_unwanted_folders()
    
    print("\n" + "="*80)
    print("COMPLETED: Organization finished!")
    print("="*80)
    print("\nNew folder: c:\\Users\\Dhruv\\OneDrive\\Desktop\\Multilingual entity linking")
    print("Unwanted files have been cleaned from original location.")
