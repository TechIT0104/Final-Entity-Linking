import os
import pandas as pd
from datasets import load_dataset

def download_mewsli():
    print("Downloading Mewsli-X (Mewsli-9 variant) from Hugging Face...")
    
    try:
        # Load Mewsli-X from the active Hugging Face repository
        dataset = load_dataset("izhx/mewsli-x")
        print("Dataset downloaded successfully!\n")
        
        # Create the local directory
        output_dir = "test_data/MEWSLI"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save each split to a CSV file
        for split in dataset.keys():
            df = dataset[split].to_pandas()
            output_path = os.path.join(output_dir, f"mewsli9_{split}.csv")
            df.to_csv(output_path, index=False)
            print(f"Saved '{split}' split to {output_path} (Total rows: {len(df)})")
            
        print("\nAll done! The dataset is ready.")
        
    except Exception as e:
        print(f"Error downloading the dataset: {e}")

if __name__ == '__main__':
    download_mewsli()