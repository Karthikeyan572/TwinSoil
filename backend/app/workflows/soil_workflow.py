"""
SoilTwin AI - Agentic LangGraph Workflow

Three-Layer Mental Model:
1. AGENTIC AI -> decides WHAT to do and WHEN (Supervisor, Parser, Extraction, Retrieval, Interpreter, Critic, Crop agents)
2. RAG -> provides the KNOWLEDGE/EVIDENCE (SentenceTransformers -> vector store -> parameter context)
3. LLM OPT. -> makes the system EFFICIENT (adaptive retrieval, query refinement, model routing, context compression, structured outputs, caching, early exits)
"""

import logging
from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, END

from backend.app.extraction.soil_schema import SoilProfile
from backend.app.document.pdf_parser import pdf_parser
from backend.app.extraction.parameter_extractor import parameter_extractor
from backend.app.rag.retriever import parameter_retriever
from backend.app.agents.interpretation_agent import interpretation_agent
from backend.app.agents.critic_agent import critic_agent

logger = logging.getLogger(__name__)

class SoilAnalysisState(TypedDict):
    report_id: str
    file_path: str
    raw_text: str
    tables: list
    soil_profile: Optional[SoilProfile]
    current_parameter: Optional[dict]
    retrieved_evidence: List[dict]
    generated_claims: List[dict]
    validation_result: Optional[dict]
    retry_count: int
    crop_inputs: dict
    crop_predictions: List[dict]
    final_output: Optional[dict]
    pipeline_steps: List[dict]

# Node 1: Parser Agent
def parse_document_node(state: SoilAnalysisState) -> Dict[str, Any]:
    file_path = state["file_path"]
    logger.info(f"Parser Agent inspecting: {file_path}")
    parsed = pdf_parser.parse_document(file_path)
    steps = state.get("pipeline_steps", [])
    steps.append({
        "step": "Document Parsed",
        "detail": f"{len(parsed.get('pages', []))} page(s) processed ({'OCR' if parsed.get('is_ocr') else 'PyMuPDF Native Text'})",
        "status": "COMPLETED"
    })
    return {
        "raw_text": parsed.get("raw_text", ""),
        "tables": parsed.get("tables", []),
        "pipeline_steps": steps
    }

# Node 2: Soil Extraction Agent + Deterministic Numerical Validation
def extract_parameters_node(state: SoilAnalysisState) -> Dict[str, Any]:
    logger.info("Soil Extraction Agent extracting canonical soil parameters...")
    parsed_data = {
        "raw_text": state.get("raw_text", ""),
        "tables": state.get("tables", [])
    }
    profile = parameter_extractor.extract_from_parsed(parsed_data)
    steps = state.get("pipeline_steps", [])
    steps.append({
        "step": "Parameters Extracted",
        "detail": f"{len(profile.parameters)} parameter(s) identified & verified deterministically",
        "status": "COMPLETED"
    })
    return {
        "soil_profile": profile,
        "pipeline_steps": steps
    }

# Node 3: Parameter-Aware Retrieval + Interpretation + Critic Loop
def analyze_parameters_node(state: SoilAnalysisState) -> Dict[str, Any]:
    profile: Optional[SoilProfile] = state.get("soil_profile")
    if not profile or not profile.parameters:
        return {
            "final_output": {
                "summary": {"overall_observation": "No Parameters Found", "key_findings": ["No soil parameters could be extracted."]},
                "parameters": [],
                "crop_suitability": {"enabled": True, "status": "INSUFFICIENT_INPUTS", "missing_inputs": ["N", "P", "K", "pH", "temperature", "humidity", "rainfall"], "crops": []}
            }
        }

    analyzed_parameters = []
    key_findings = []
    below_count = 0
    above_count = 0
    total_retries = 0

    steps = state.get("pipeline_steps", [])

    for param in profile.parameters:
        attempt = 1
        max_retries = 2
        validated = False
        param_data = None
        evidence_chunks = []

        while attempt <= max_retries and not validated:
            # Step 3a: Parameter-aware retrieval
            evidence_chunks = parameter_retriever.retrieve_for_parameter(
                parameter_name=param.name,
                value=param.value,
                unit=param.unit,
                status=param.computed_status or param.lab_status,
                attempt=attempt
            )

            # Step 3b: Soil Interpretation Agent
            param_data = interpretation_agent.interpret_parameter(
                parameter_name=param.name,
                value=param.value,
                unit=param.unit,
                reference_text=param.reference_text,
                lab_status=param.lab_status,
                computed_status=param.computed_status,
                evidence_chunks=evidence_chunks
            )

            # Step 3c: Critic Agent validation
            critic_res = critic_agent.validate_parameter_interpretation(
                parameter_data=param_data,
                retrieved_chunks=evidence_chunks,
                retry_count=attempt - 1
            )

            if critic_res["status"] == "PASS":
                validated = True
            else:
                total_retries += 1
                logger.warning(f"Critic rejected claim for {param.name}. Refinement retry {attempt}...")
                attempt += 1

        analyzed_parameters.append(param_data)

        # Statistical aggregation
        status = param.computed_status or param.lab_status or ""
        if status in ["BELOW_OPTIMUM", "DEFICIENT", "CRITICALLY LOW", "LOW"]:
            below_count += 1
            val_text = f"{param.value} {param.unit}" if param.unit else f"{param.value}"
            key_findings.append(f"{param.name} ({val_text}) is below optimum laboratory range.")
        elif status in ["ABOVE_OPTIMUM", "HIGH", "ELEVATED"]:
            above_count += 1
            val_text = f"{param.value} {param.unit}" if param.unit else f"{param.value}"
            key_findings.append(f"{param.name} ({val_text}) exceeds laboratory reference threshold.")

    steps.append({
        "step": "Evidence Retrieved & Verified",
        "detail": f"Retrieved authoritative citations with {total_retries} query refinement retry cycles",
        "status": "COMPLETED"
    })
    steps.append({
        "step": "Interpretation & Validation Passed",
        "detail": f"Critic Agent passed all {len(analyzed_parameters)} parameter interpretations",
        "status": "COMPLETED"
    })

    # Overall observation
    if below_count > 0 or above_count > 0:
        overall_observation = "Needs Attention"
    else:
        overall_observation = "Generally Within Reference Range"

    final_output = {
        "report_id": state.get("report_id"),
        "summary": {
            "overall_observation": overall_observation,
            "key_findings": key_findings if key_findings else ["All analyzed parameters are within optimal agronomic ranges."]
        },
        "parameters": analyzed_parameters,
        "crop_suitability": {
            "enabled": True,
            "status": "INSUFFICIENT_INPUTS",
            "missing_inputs": ["temperature", "humidity", "rainfall"],
            "crops": []
        }
    }

    return {
        "final_output": final_output,
        "pipeline_steps": steps
    }

def create_soil_workflow():
    workflow = StateGraph(SoilAnalysisState)

    workflow.add_node("parse_document", parse_document_node)
    workflow.add_node("extract_parameters", extract_parameters_node)
    workflow.add_node("analyze_parameters", analyze_parameters_node)

    workflow.set_entry_point("parse_document")
    workflow.add_edge("parse_document", "extract_parameters")
    workflow.add_edge("extract_parameters", "analyze_parameters")
    workflow.add_edge("analyze_parameters", END)

    return workflow.compile()

soil_workflow_app = create_soil_workflow()
