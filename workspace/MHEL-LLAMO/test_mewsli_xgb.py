import json
import os
import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, accuracy_score
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


def evaluate_mewsli():
    path = "results/MEWSLI_EN/candidates_test_top50_en.json"
    model_path = "universal_xgb_threshold.json"
    
    if not os.path.exists(path):
        print(f"Error: Could not find Mewsli candidates file at {path}")
        return
        
    if not os.path.exists(model_path):
        print(f"Error: Could not find XGBoost model at {model_path}")
        return

    print("Loading Mewsli MEWSLI_EN OOD data...")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    df = extract_features(data)
    
    if len(df) == 0:
        print("No valid entities extracted from JSON.")
        return
        
    print(f"Extracted {len(df)} records.")
    
    X_test = df.drop(columns=["is_correct"])
    y_test = df["is_correct"]

    # Load model
    print("\nLoading Universal XGBoost Router...")
    model = xgb.XGBClassifier()
    model.load_model(model_path)
    
    xgb_preds = model.predict(X_test)
    xgb_acc = accuracy_score(y_test, xgb_preds)
    
    target_names = ["Send to LLM (0)", "Trust Top1 (1)"]
    print("\n==================================")
    print("Zero-Shot OOD Performance on Mewsli")
    print("==================================")
    print(f"Accuracy: {xgb_acc:.4f}")
    
    try:
        report = classification_report(y_test, xgb_preds, target_names=target_names)
        print(report)
    except ValueError:
        print(classification_report(y_test, xgb_preds))

if __name__ == "__main__":
    evaluate_mewsli()