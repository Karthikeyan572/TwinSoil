import logging
from typing import Dict, Any, List, Optional
from backend.ml.crop_predictor import crop_predictor

logger = logging.getLogger(__name__)

REQUIRED_ML_FEATURES = ["N", "P", "K", "ph", "temperature", "humidity", "rainfall"]

class CropAgent:
    def check_inputs_and_predict(
        self,
        provided_inputs: Dict[str, Any],
        extracted_parameters: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Inspects required ML features. Never fabricates missing temperature, humidity, or rainfall.
        Returns INSUFFICIENT_INPUTS or READY with ranked crop candidates.
        """
        merged_inputs = {}
        # Merge extracted soil parameters (N, P, K, pH)
        if extracted_parameters:
            for k, v in extracted_parameters.items():
                if k in ["N", "P", "K", "pH"] and v is not None:
                    merged_inputs[k.lower() if k == "pH" else k] = float(v)

        # Overlay user provided values
        for k, v in provided_inputs.items():
            if v is not None:
                norm_key = "ph" if k.lower() == "ph" else k
                try:
                    merged_inputs[norm_key] = float(v)
                except (ValueError, TypeError):
                    pass

        # Check for missing features
        missing = [f for f in REQUIRED_ML_FEATURES if f not in merged_inputs or merged_inputs[f] is None]

        if missing:
            return {
                "status": "INSUFFICIENT_INPUTS",
                "missing_inputs": missing,
                "current_inputs": merged_inputs,
                "message": f"Crop suitability requires environmental measurements. Please specify: {', '.join(missing)}."
            }

        # Predict using trained classifier
        N_val = merged_inputs["N"]
        P_val = merged_inputs["P"]
        K_val = merged_inputs["K"]
        temp_val = merged_inputs["temperature"]
        hum_val = merged_inputs["humidity"]
        ph_val = merged_inputs["ph"]
        rain_val = merged_inputs["rainfall"]

        predictions = crop_predictor.predict_crop(
            N=N_val,
            P=P_val,
            K=K_val,
            temperature=temp_val,
            humidity=hum_val,
            ph=ph_val,
            rainfall=rain_val
        )

        # Deterministic suitability explanations grounded in soil values
        reasons = []
        if ph_val < 5.5:
            reasons.append(f"Soil pH ({ph_val}) is acidic, favoring acid-tolerant crops and restricting others.")
        elif ph_val > 7.5:
            reasons.append(f"Soil pH ({ph_val}) is alkaline, which may limit micronutrient availability for certain crops.")

        if K_val < 60:
            reasons.append(f"Potassium level ({K_val} ppm) is low; top crops are selected with lower potassium sensitivity or higher root uptake efficiency.")
        if P_val < 20:
            reasons.append(f"Available phosphorus ({P_val} ppm) is below optimum, prioritizing crops with modest early phosphorus demands.")

        if not reasons:
            reasons.append("Measured soil macronutrients and environmental factors align favorably with the agronomic requirements of the recommended crops.")

        explanation = " ".join(reasons)

        limitations = [
            "This is a model-based suitability prediction, not a guaranteed yield or success probability.",
            "Predictions are derived from empirical agronomic benchmarks and require regional agronomic validation before planting.",
            "Disease pressures, local pest cycles, and microclimatic factors are not captured by the current model."
        ]

        return {
            "status": "READY",
            "inputs": {
                "N": N_val,
                "P": P_val,
                "K": K_val,
                "temperature": temp_val,
                "humidity": hum_val,
                "ph": ph_val,
                "rainfall": rain_val
            },
            "predictions": predictions,
            "explanation": explanation,
            "limitations": limitations
        }

crop_agent = CropAgent()
