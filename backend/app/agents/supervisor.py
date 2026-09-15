import logging
from typing import Dict, Any
from backend.app.workflows.soil_workflow import soil_workflow_app, SoilAnalysisState

logger = logging.getLogger(__name__)

class SupervisorAgent:
    def execute_analysis(self, report_id: str, file_path: str) -> Dict[str, Any]:
        """
        Plans and manages workflow execution, tracks progress,
        and returns the consolidated state.
        """
        initial_state: SoilAnalysisState = {
            "report_id": report_id,
            "file_path": file_path,
            "raw_text": "",
            "tables": [],
            "soil_profile": None,
            "current_parameter": None,
            "retrieved_evidence": [],
            "generated_claims": [],
            "validation_result": None,
            "retry_count": 0,
            "crop_inputs": {},
            "crop_predictions": [],
            "final_output": None,
            "pipeline_steps": [
                {"step": "Report Received", "detail": f"Report ID: {report_id}", "status": "COMPLETED"}
            ]
        }

        logger.info(f"Supervisor dispatching workflow for Report: {report_id}")
        final_state = soil_workflow_app.invoke(initial_state)
        return final_state

supervisor_agent = SupervisorAgent()
