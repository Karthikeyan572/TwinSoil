import json
from backend.ml.crop_predictor import crop_predictor

def main():
    with open("backend/models/model_metadata.json", "r") as f:
        meta = json.load(f)

    print("=========================================================")
    print("      SOILTWIN AI - ML CROP PREDICTOR EXECUTION         ")
    print("=========================================================")
    print(f"Model Architecture: {meta['model_name']} (v{meta['version']})")
    print(f"Dataset:            {meta['dataset']}")
    print(f"Validation Accuracy: {meta['validation_metrics']['accuracy'] * 100:.2f}%")
    print(f"Macro F1 Score:      {meta['validation_metrics']['macro_f1'] * 100:.2f}%")
    print(f"Supported Crops ({meta['classes_count']}): {', '.join(meta['classes'][:8])}...")
    print("---------------------------------------------------------")

    test_scenarios = [
        {
            "name": "Scenario 1: High Moisture & Nitrogen (e.g. Wetland / Paddy)",
            "inputs": {"N": 90, "P": 42, "K": 43, "temperature": 25.5, "humidity": 82.0, "ph": 6.5, "rainfall": 230.0}
        },
        {
            "name": "Scenario 2: Moderate Semi-Arid & Balanced Nutrients (e.g. Maize/Corn)",
            "inputs": {"N": 75, "P": 48, "K": 20, "temperature": 23.0, "humidity": 65.0, "ph": 6.2, "rainfall": 70.0}
        },
        {
            "name": "Scenario 3: High Potassium & Moderate Rainfall (e.g. Chickpea / Legumes)",
            "inputs": {"N": 40, "P": 67, "K": 79, "temperature": 18.5, "humidity": 17.0, "ph": 7.3, "rainfall": 80.0}
        }
    ]

    for sc in test_scenarios:
        print(f"\n▶ {sc['name']}")
        print(f"  Inputs: {sc['inputs']}")
        preds = crop_predictor.predict_crop(**sc['inputs'])
        print("  Predictions:")
        for idx, p in enumerate(preds[:3]):
            print(f"    {idx+1}. {p['crop']} — {p['probability']*100:.2f}% ({p['confidence_label']})")
            print(f"       Notice: {p['disclaimer']}")

    print("\n=========================================================")
    print("Model inference completed successfully!")

if __name__ == "__main__":
    main()
