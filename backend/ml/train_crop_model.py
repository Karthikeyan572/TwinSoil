import json
import datetime
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

from backend.ml.prepare_dataset import ensure_crop_dataset, DATASET_PATH
from backend.app.config import settings

def train_and_evaluate():
    ensure_crop_dataset()
    
    df = pd.read_csv(DATASET_PATH)
    print(f"Loaded dataset with {len(df)} rows and columns: {list(df.columns)}")
    
    # 1. Schema validation & missing value handling
    expected_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall", "label"]
    assert all(c in df.columns for c in expected_cols), f"Missing required columns in {df.columns}"
    df = df.dropna()
    
    X = df[["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]]
    y = df["label"]
    
    # 2. Stratified train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    candidates = {
        "RandomForestClassifier": RandomForestClassifier(n_estimators=100, random_state=42),
        "ExtraTreesClassifier": ExtraTreesClassifier(n_estimators=100, random_state=42),
        "GradientBoostingClassifier": GradientBoostingClassifier(n_estimators=50, random_state=42)
    }
    
    best_model = None
    best_name = ""
    best_acc = 0.0
    best_metrics = {}
    
    print("\n--- Model Benchmark Evaluation ---")
    for name, clf in candidates.items():
        clf.fit(X_train, y_train)
        preds = clf.predict(X_test)
        
        acc = accuracy_score(y_test, preds)
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_test, preds, average="macro")
        p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(y_test, preds, average="weighted")
        
        print(f"[{name}] Accuracy: {acc:.4f} | Macro F1: {f1_macro:.4f} | Weighted F1: {f1_weighted:.4f}")
        
        if acc > best_acc:
            best_acc = acc
            best_model = clf
            best_name = name
            best_metrics = {
                "accuracy": round(float(acc), 4),
                "macro_f1": round(float(f1_macro), 4),
                "weighted_f1": round(float(f1_weighted), 4),
                "macro_precision": round(float(p_macro), 4),
                "macro_recall": round(float(r_macro), 4),
            }
            
    print(f"\nBest Selected Model: {best_name} with Accuracy: {best_acc:.4f}")
    
    # Save artifacts
    models_dir = settings.MODELS_DIR
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = models_dir / "crop_recommendation_model.pkl"
    joblib.dump(best_model, model_path)
    
    classes = list(best_model.classes_)
    metadata = {
        "model_name": best_name,
        "dataset": "Kaggle Crop Recommendation Dataset (atharvaingle/crop-recommendation-dataset)",
        "features": ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"],
        "classes": classes,
        "classes_count": len(classes),
        "validation_metrics": best_metrics,
        "training_timestamp": datetime.datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
    
    meta_path = models_dir / "model_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Saved model artifact to {model_path}")
    print(f"Saved model metadata to {meta_path}")

if __name__ == "__main__":
    train_and_evaluate()
