from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.database.models import Report, SoilParameterModel, CropPredictionModel
from backend.app.agents.crop_agent import crop_agent

router = APIRouter(prefix="/reports", tags=["crops"])

class CropInputRequest(BaseModel):
    N: Optional[float] = Field(default=None, description="Nitrogen level")
    P: Optional[float] = Field(default=None, description="Phosphorus level")
    K: Optional[float] = Field(default=None, description="Potassium level")
    ph: Optional[float] = Field(default=None, description="Soil pH")
    temperature: Optional[float] = Field(default=None, description="Ambient temperature (°C)")
    humidity: Optional[float] = Field(default=None, description="Relative humidity (%)")
    rainfall: Optional[float] = Field(default=None, description="Annual/seasonal rainfall (mm)")

@router.post("/{report_id}/crops")
async def get_crop_recommendations(
    report_id: str,
    user_inputs: CropInputRequest,
    db: Session = Depends(get_db)
):
    """
    Evaluates ML crop suitability. If environmental factors (temperature, humidity, rainfall)
    are missing, returns INSUFFICIENT_INPUTS. Never invents missing values.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found.")

    # Pull extracted parameters from report
    db_params = db.query(SoilParameterModel).filter(SoilParameterModel.report_id == report_id).all()
    extracted = {}
    for p in db_params:
        if p.value is not None:
            extracted[p.name] = p.value

    # If N is not in report, allow user input or default check
    provided = {k: v for k, v in user_inputs.model_dump().items() if v is not None}

    # Pass to Crop Agent
    result = crop_agent.check_inputs_and_predict(
        provided_inputs=provided,
        extracted_parameters=extracted
    )

    # Save to database if predictions are ready
    if result["status"] == "READY":
        pred_record = CropPredictionModel(
            report_id=report_id,
            inputs_json=result["inputs"],
            status=result["status"],
            predictions_json=result["predictions"],
            explanation=result["explanation"],
            limitations_json=result["limitations"],
            model_version="1.0.0"
        )
        db.add(pred_record)
        db.commit()

    return result
