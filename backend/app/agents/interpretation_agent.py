import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.services.llm_service import llm_service
from backend.app.config import settings

logger = logging.getLogger(__name__)

class ExplanationSchema(BaseModel):
    explanation: str = Field(description="Evidence-grounded explanation of what the measured value means relative to the lab range.")
    why_it_matters: str = Field(description="Agronomic importance and plant impact without unsupported catastrophic claims.")
    confidence: str = Field(default="HIGH", description="Confidence level based on retrieved evidence (HIGH, MEDIUM, LOW).")

class InterpretationAgent:
    def interpret_parameter(
        self,
        parameter_name: str,
        value: Optional[float],
        unit: Optional[str],
        reference_text: Optional[str],
        lab_status: Optional[str],
        computed_status: Optional[str],
        evidence_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesizes an evidence-grounded explanation for a single soil parameter.
        Uses context compression: sends only relevant chunks for this parameter.
        """
        val_str = f"{value} {unit}" if (value is not None and unit) else (f"{value}" if value is not None else "Not reported")
        range_str = reference_text or "Not specified by lab"
        status_str = lab_status or computed_status or "Unknown"

        # Context compression: build compact evidence context
        evidence_context = "\n".join([
            f"Source [{c.get('source')}, Page {c.get('page', 'N/A')}]: {c.get('content')}"
            for c in evidence_chunks[:3]
        ])

        system_prompt = (
            "You are an expert agricultural soil scientist. Explain the parameter and its measured value "
            "strictly using the provided retrieved extension evidence. Never make unsupported causal claims or "
            "prescribe fertilizer quantities without evidence. Distinguish 'the lab reports below optimum' from "
            "'this will cause crop failure'."
        )

        prompt = (
            f"Parameter: {parameter_name}\n"
            f"Measured Value: {val_str}\n"
            f"Lab Range: {range_str}\n"
            f"Assigned Status: {status_str}\n\n"
            f"Retrieved Extension Evidence:\n{evidence_context}\n\n"
            f"Provide an accurate explanation and why it matters."
        )

        try:
            # Model routing: use strong model for interpretation synthesis
            response: ExplanationSchema = llm_service.generate_structured(
                prompt=prompt,
                response_schema=ExplanationSchema,
                system_prompt=system_prompt,
                use_strong_model=True
            )
            explanation = response.explanation
            why_it_matters = response.why_it_matters
            confidence = response.confidence
        except Exception as e:
            logger.warning(f"Structured interpretation fallback for {parameter_name}: {e}")
            if evidence_chunks:
                first_chunk = evidence_chunks[0]
                explanation = f"The measured {parameter_name} of {val_str} is evaluated as {status_str} relative to the reference range of {range_str}. {first_chunk.get('content')}"
                why_it_matters = f"Maintaining optimal {parameter_name} levels is critical for balanced soil chemistry and root nutrient uptake."
                confidence = "HIGH"
            else:
                explanation = f"The reported {parameter_name} is {val_str} with status {status_str}."
                why_it_matters = f"Essential soil parameter for crop productivity."
                confidence = "MEDIUM"

        # Map evidence items to output schema
        cited_evidence = []
        for c in evidence_chunks[:2]:
            cited_evidence.append({
                "source": c.get("source", "Agricultural Extension Reference"),
                "page": c.get("page", 1),
                "text": c.get("content", ""),
                "relevance": c.get("relevance", "HIGH")
            })

        return {
            "name": parameter_name,
            "value": value,
            "unit": unit,
            "status": computed_status or lab_status or "UNKNOWN",
            "explanation": explanation,
            "why_it_matters": why_it_matters,
            "confidence": confidence,
            "evidence": cited_evidence
        }

interpretation_agent = InterpretationAgent()
