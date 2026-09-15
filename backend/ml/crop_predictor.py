import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np
from backend.app.config import settings

logger = logging.getLogger(__name__)

class CropPredictor:
    def __init__(self):
        self.model = None
        self.metadata = None
        self._load_artifacts()

    def _load_artifacts(self):
        models_dir = settings.MODELS_DIR
        model_path = models_dir / "crop_recommendation_model.pkl"
        meta_path = models_dir / "model_metadata.json"

        if model_path.exists():
            self.model = joblib.load(model_path)
            logger.info("Loaded Crop Recommendation Model artifact.")
        if meta_path.exists():
            with open(meta_path, "r") as f:
                self.metadata = json.load(f)

    def predict_crop(
        self,
        N: float,
        P: float,
        K: float,
        temperature: float,
        humidity: float,
        ph: float,
        rainfall: float,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Predicts top candidate crops with model confidence probability.
        Strict disclaimer: This is a model-based suitability prediction, not a guaranteed yield or success probability.
        """
        if self.model is None:
            self._load_artifacts()
            if self.model is None:
                raise RuntimeError("Crop Recommendation Model is not trained or loaded.")

        feature_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
        features_df = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]], columns=feature_cols)
        probabilities = self.model.predict_proba(features_df)[0]
        classes = self.model.classes_

        # Rank by probability descending
        ranked_indices = np.argsort(probabilities)[::-1][:top_k]

        candidates = []
        for idx in ranked_indices:
            prob = float(probabilities[idx])
            if prob > 0.01:  # filter negligible probabilities
                candidates.append({
                    "crop": str(classes[idx]).capitalize(),
                    "probability": round(prob, 4),
                    "confidence_label": "Model Confidence / Prediction Probability",
                    "disclaimer": "This is a model-based suitability prediction, not a guaranteed yield or success probability."
                })

        return candidates

crop_predictor = CropPredictor()
