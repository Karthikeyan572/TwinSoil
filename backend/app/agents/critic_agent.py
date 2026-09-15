import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.services.llm_service import llm_service
from backend.app.validation.evidence_validator import evidence_validator

logger = logging.getLogger(__name__)

class CriticResult(BaseModel):
    status: str = Field(description="'PASS' or 'RETRY'")
    unsupported_claims: List[str] = Field(default_factory=list)
    numeric_errors: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)

class CriticAgent:
    def validate_parameter_interpretation(
        self,
        parameter_data: Dict[str, Any],
        retrieved_chunks: List[Dict[str, Any]],
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Validates claim-evidence consistency, numerical alignment, and citations.
        Returns CriticResult dictionary.
        """
        unsupported_claims = []
        numeric_errors = []
        missing_evidence = []

        # 1. Check citations presence
        evidence_list = parameter_data.get("evidence", [])
        if not evidence_list and not retrieved_chunks:
            missing_evidence.append(f"No evidence retrieved for parameter {parameter_data.get('name')}.")

        # 2. Check source grounding
        retrieved_sources = {c.get("source") for c in retrieved_chunks}
        for ev in evidence_list:
            if ev.get("source") not in retrieved_sources:
                unsupported_claims.append(f"Evidence source '{ev.get('source')}' was not in retrieved chunks.")

        # 3. Numeric consistency check
        val = parameter_data.get("value")
        status = parameter_data.get("status")
        # Ensure status doesn't contradict value if range is standard
        if val is not None:
            explanation = parameter_data.get("explanation", "").lower()
            if status == "BELOW_OPTIMUM" and "above" in explanation and "below" not in explanation:
                numeric_errors.append("Explanation states parameter is above optimum when status is BELOW_OPTIMUM.")
            elif status == "ABOVE_OPTIMUM" and "below" in explanation and "above" not in explanation:
                numeric_errors.append("Explanation states parameter is below optimum when status is ABOVE_OPTIMUM.")

        # Determine status
        if (unsupported_claims or numeric_errors or missing_evidence) and retry_count < 2:
            status = "RETRY"
        else:
            status = "PASS"

        return {
            "status": status,
            "unsupported_claims": unsupported_claims,
            "numeric_errors": numeric_errors,
            "missing_evidence": missing_evidence
        }

critic_agent = CriticAgent()
