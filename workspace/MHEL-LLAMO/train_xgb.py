import json
import os
import glob
import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
import Levenshtein

def normalize_id(raw_id):
    raw_id = (raw_id or "").strip()
    return raw_id if raw_id.upper().startswith("Q") else "NIL"

def extract_features(data):
    rows = []
    
    for item in data:
        # Ground truth
        gt_id = normalize_id(item.get("identifier", ""))
        
        # If there are no candidates, it automatically goes to LLM probably, or we just fail.
        cands = item.get("candidates", [])
        if len(cands) == 0:
            continue
            
        # Top 1 Prediction
        top1 = cands[0]
        top1_id = normalize_id(top1.get("wb_id", ""))
        top1_score = top1.get("score", 0.0)
        
        # Top 2 Prediction
        top2_score = 0.0
        if len(cands) > 1:
            top2_score = cands[1].get("score", 0.0)
            
        mention = item.get("surface", "").lower()
        cand_label = top1.get("label", "").lower()
        
        # Determine if we should trust top 1 (is it correct?)
        is_correct = 1 if (gt_id == top1_id and gt_id != "NIL") else 0
            
        # Features
        features = {
            "top1_score": top1_score,
            "top1_top2_diff": top1_score - top2_score,
            "mention_len": len(mention),
            "lev_dist": Levenshtein.distance(mention, cand_label),
            "is_correct": is_correct
        }
        
        rows.append(features)
        
    return pd.DataFrame(rows)

def train_and_eval():
    base_results_dir = "results"
    
    # We will collect all DataFrames
    all_dfs = []
    
    print("Loading all universal datasets...")
    for root, dirs, files in os.walk(base_results_dir):
        for file in files:
            if not file.endswith(".json") or "candidates" not in file:
                continue
            
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    df = extract_features(data)
                    all_dfs.append(df)
            except Exception as e:
                print(f"Skipping {file_path}: {e}")

    if not all_dfs:
        print("No data found!")
        return

    df_all = pd.concat(all_dfs, ignore_index=True)
    
    X = df_all.drop(columns=["is_correct"])
    y = df_all["is_correct"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    
    print(f"Universal Train size: {len(X_train)}, Class balance: {y_train.mean():.3f}")
    print(f"Universal Test size: {len(X_test)}, Class balance: {y_test.mean():.3f}")
    
    model = xgb.XGBClassifier(
        n_estimators=200, 
        max_depth=4, 
        learning_rate=0.1,
        eval_metric='logloss',
        use_label_encoder=False
    )
    model.fit(X_train, y_train)
    
    # Baseline comparison across all datasets combined
    best_thresh, best_acc = 0, 0
    for t in np.linspace(10, 20, 50):
        preds = (X_train["top1_score"] >= t).astype(int)
        acc = accuracy_score(y_train, preds)
        if acc > best_acc:
            best_acc = acc
            best_thresh = t
            
    print(f"\nUniversal Baseline Threshold on Train: {best_thresh:.2f}")
    test_base_preds = (X_test["top1_score"] >= best_thresh).astype(int)
    print("Universal Baseline Threshold Test Performance:")
    print(classification_report(y_test, test_base_preds, target_names=["Hard (Send to LLM)", "Easy (Trust Top1)"]))
    
    xgb_preds = model.predict(X_test)
    print("\nUniversal XGBoost Test Performance:")
    print(classification_report(y_test, xgb_preds, target_names=["Hard (Send to LLM)", "Easy (Trust Top1)"]))
    
    model.save_model("universal_xgb_threshold.json")
    print("Model saved to universal_xgb_threshold.json")
    
if __name__ == "__main__":
    train_and_eval()
