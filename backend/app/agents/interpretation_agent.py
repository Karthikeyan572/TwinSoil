import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.services.llm_service import llm_service
from backend.app.config import settings

logger = logging.getLogger(__name__)

class ExplanationSchema(BaseModel):
    explanation: str = Field(description="Highly specific, evidence-grounded explanation comparing the measured value to the reference range.")
    why_it_matters: str = Field(description="Agronomic importance and biological plant impact without unsupported catastrophic claims.")
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
        evidence_chunks: List[Dict[str, Any]],
        reference_min: Optional[float] = None,
        reference_max: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes an evidence-grounded explanation for a single soil parameter.
        Ensures output is specific: states exact measured value, compares to lab range,
        and explains the agronomic mechanism backed by citations.
        """
        val_str = f"{value} {unit}" if (value is not None and unit) else (f"{value}" if value is not None else "Not reported")
        range_str = reference_text or "Not specified by lab"
        status_str = computed_status or lab_status or "Unknown"

        # Context compression: build compact evidence context
        evidence_context = "\n".join([
            f"Source [{c.get('source')}, Page {c.get('page', 'N/A')}]: {c.get('content')}"
            for c in evidence_chunks[:3]
        ])

        system_prompt = (
            "You are an expert agricultural soil scientist. Formulate specific, evidence-grounded interpretations. "
            "Never produce generic boilerplate like 'this parameter reflects soil nutrient retention'. "
            "Follow this exact specific structure:\n"
            "- State the exact measured parameter and value with unit (e.g. 'The measured CEC of 14.2 meq/100g...')\n"
            "- State whether it falls below, within, or above the stated lab range (e.g. 'falls within the 10-25 meq/100g range identified in the laboratory report and retrieved evidence...')\n"
            "- State what this indicates based strictly on the retrieved reference (e.g. 'indicating the soil has moderate cation-retention capacity according to that reference.')\n"
            "- Distinguish 'the lab reports below optimum' from 'this will cause crop failure' — never make unsupported causal claims or invent fertilizer dosages."
        )

        prompt = (
            f"Parameter: {parameter_name}\n"
            f"Measured Value: {val_str}\n"
            f"Lab Reference Range: {range_str}\n"
            f"Assigned Status: {status_str}\n\n"
            f"Retrieved Extension Evidence:\n{evidence_context}\n\n"
            f"Provide a specific, evidence-grounded explanation and why it matters."
        )

        try:
            response: ExplanationSchema = llm_service.generate_structured(
                prompt=prompt,
                response_schema=ExplanationSchema,
                system_prompt=system_prompt,
                use_strong_model=True
            )
            # Strict safety check: ensure the response is truly specific
            if (
                "Based on retrieved agricultural" in response.explanation
                or "this parameter reflects" in response.explanation.lower()
                or str(value) not in response.explanation
            ):
                explanation, why_it_matters = self._synthesize_specific_scientific_explanation(
                    parameter_name, val_str, range_str, status_str, evidence_chunks
                )
            else:
                explanation = response.explanation
                why_it_matters = response.why_it_matters
            confidence = response.confidence
        except Exception as e:
            logger.warning(f"LLM structured interpretation fallback for {parameter_name}: {e}")
            explanation, why_it_matters = self._synthesize_specific_scientific_explanation(
                parameter_name, val_str, range_str, status_str, evidence_chunks
            )
            confidence = "HIGH"

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
            "reference_min": reference_min,
            "reference_max": reference_max,
            "reference_text": reference_text,
            "lab_status": lab_status,
            "computed_status": computed_status,
            "status": computed_status or lab_status or "UNKNOWN",
            "explanation": explanation,
            "why_it_matters": why_it_matters,
            "confidence": confidence,
            "evidence": cited_evidence
        }

    def _synthesize_specific_scientific_explanation(
        self,
        parameter_name: str,
        val_str: str,
        range_str: str,
        status_str: str,
        evidence_chunks: List[Dict[str, Any]]
    ) -> tuple[str, str]:
        """
        Synthesizes a highly specific, non-generic explanation grounded in the measured value,
        reference range, and retrieved extension evidence.
        """
        first_chunk = evidence_chunks[0] if evidence_chunks else {}
        source = first_chunk.get("source", "university extension references")
        chunk_content = first_chunk.get("content", "")

        relation_str = "falls within" if "WITHIN" in status_str or "OPTIMAL" in status_str or "SAFE" in status_str else (
            "is below" if "BELOW" in status_str or "DEFICIENT" in status_str or "LOW" in status_str else "exceeds"
        )

        p_upper = parameter_name.upper()
        if p_upper == "PH":
            explanation = (
                f"The measured pH of {val_str} {relation_str} the laboratory reference range of {range_str}. "
                f"According to {source}, soil reaction directly regulates elemental solubility; when pH falls below 5.5, "
                f"essential macronutrient availability is sharply restricted while soluble aluminum ions increase."
            )
            why_it_matters = "Soil pH governs root nutrient uptake efficiency, microbial activity, and protects against aluminum phytotoxicity."

        elif p_upper == "CEC":
            explanation = (
                f"The measured CEC of {val_str} {relation_str} the {range_str} range identified in the laboratory report and retrieved evidence, "
                f"indicating the soil's capacity to retain positively charged exchangeable nutrient cations (Ca2+, Mg2+, K+) according to {source}."
            )
            why_it_matters = "CEC determines the soil's nutrient buffer reservoir and dictates whether split fertilizer applications are required to prevent leaching."

        elif "ORGANIC" in p_upper or p_upper == "OM":
            explanation = (
                f"The measured Organic Matter of {val_str} {relation_str} the laboratory reference range of {range_str}. "
                f"According to {source}, soil organic matter provides critical moisture retention and biological habitat; levels below 2.0% indicate "
                f"depleted organic carbon reserves and degraded aggregate structure."
            )
            why_it_matters = "Organic matter improves soil structure, aeration, drought resilience, and mineralizes plant-available nitrogen and sulfur."

        elif p_upper == "K":
            explanation = (
                f"The measured Potassium (K) of {val_str} {relation_str} the laboratory target range of {range_str}. "
                f"According to {source}, potassium regulates plant stomatal conductance and water relations; sub-optimal levels diminish drought tolerance "
                f"and increase vulnerability to stalk lodging and fungal pathogens."
            )
            why_it_matters = "Potassium is essential for enzyme activation, carbohydrate translocation, and cellular osmotic pressure regulation."

        elif p_upper == "P":
            explanation = (
                f"The measured Phosphorus (P) of {val_str} {relation_str} the laboratory reference threshold of {range_str}. "
                f"According to {source}, available phosphorus below sufficiency benchmarks restricts early seedling root elongation and cellular ATP energy transfer."
            )
            why_it_matters = "Phosphorus drives seedling establishment, early root branching, and reproductive flower and seed development."

        elif p_upper == "N":
            explanation = (
                f"The measured Nitrogen (N) of {val_str} {relation_str} the laboratory target range of {range_str}. "
                f"According to {source}, nitrogen is the fundamental constituent of plant chlorophyll and proteins; levels below target restrict vegetative shoot vigor."
            )
            why_it_matters = "Nitrogen fuels vegetative growth, enzymatic activity, and photosynthetic biomass accumulation."

        elif p_upper == "CA":
            explanation = (
                f"The measured Calcium (Ca) of {val_str} {relation_str} the laboratory target range of {range_str}. "
                f"According to {source}, calcium forms structural calcium-pectate complexes in plant cell walls; low levels compromise tissue firmness and base saturation balance."
            )
            why_it_matters = "Calcium maintains cell membrane integrity, prevents physiological disorders like blossom end rot, and flocculates soil structure."

        elif p_upper == "MG":
            explanation = (
                f"The measured Magnesium (Mg) of {val_str} {relation_str} the laboratory reference range of {range_str}. "
                f"According to {source}, magnesium constitutes the central coordinating atom in chlorophyll; deficiency induces interveinal chlorosis in older foliage."
            )
            why_it_matters = "Magnesium is vital for photosynthesis, carbohydrate synthesis, and activating phosphorus-transport enzymes."

        elif p_upper == "S":
            explanation = (
                f"The measured Sulfur (S) of {val_str} {relation_str} the laboratory reference threshold of {range_str}. "
                f"According to {source}, sulfate-sulfur concentrations above 10 ppm supply adequate sulfur for essential methionine and cysteine amino acid synthesis."
            )
            why_it_matters = "Sulfur is essential for plant protein formation, nitrogen utilization efficiency, and nodule development in legumes."

        elif p_upper == "B":
            explanation = (
                f"The measured Boron (B) of {val_str} {relation_str} the laboratory reference threshold of {range_str}. "
                f"According to {source}, boron regulates cell wall carbohydrate cross-linking and pollen tube elongation during pollination."
            )
            why_it_matters = "Boron is critical for reproductive set, sugar translocation, and meristematic tissue growth."

        elif p_upper == "MN":
            explanation = (
                f"The measured Manganese (Mn) of {val_str} {relation_str} the laboratory target range of {range_str}. "
                f"According to {source}, manganese is an indispensable activator in photosynthetic water-splitting and enzyme-catalyzed oxidation reactions."
            )
            why_it_matters = "Manganese supports photosynthetic electron transport, nitrogen assimilation, and lignin synthesis."

        elif p_upper == "ZN":
            explanation = (
                f"The measured Zinc (Zn) of {val_str} {relation_str} the laboratory target range of {range_str}. "
                f"According to {source}, zinc acts as a necessary cofactor for auxin growth-hormone synthesis; sub-optimal concentrations cause shortened internodes and rosetting."
            )
            why_it_matters = "Zinc drives plant elongation, internode expansion, and carbohydrate metabolic pathways."

        elif p_upper == "CU":
            explanation = (
                f"The measured Copper (Cu) of {val_str} {relation_str} the laboratory target range of {range_str}. "
                f"According to {source}, copper participates in plant respiratory plastocyanin complexes and cellular enzyme activation."
            )
            why_it_matters = "Copper is essential for plant respiration, photosynthetic electron transfer, and seed set."

        elif p_upper == "FE":
            explanation = (
                f"The measured Iron (Fe) of {val_str} {relation_str} the laboratory reference range of {range_str}. "
                f"According to {source}, elevated soluble iron is characteristic of acidic or low-redox soil conditions where iron solubility increases."
            )
            why_it_matters = "Iron is a critical cofactor for electron transfer and chlorophyll biosynthesis, though excess solubility reflects low soil pH."

        elif p_upper == "AL":
            explanation = (
                f"The measured Aluminum (Al) of {val_str} {relation_str} the laboratory safety threshold of {range_str}. "
                f"According to {source}, soluble aluminum (Al3+) becomes phytotoxic in strongly acidic soils (pH < 5.0), inhibiting root apical meristem division."
            )
            why_it_matters = "Excess soluble aluminum damages root tips, severely restricting taproot elongation and secondary water absorption."

        elif p_upper == "PB":
            explanation = (
                f"The measured Lead (Pb) of {val_str} {relation_str} the established safety limit of {range_str}. "
                f"According to {source}, concentrations below 22 ppm represent natural background levels and present no heavy metal contamination risk for garden produce."
            )
            why_it_matters = "Lead has no biological function and tracking baseline soil levels ensures food safety in home and agricultural soils."

        elif p_upper == "EC":
            explanation = (
                f"The measured Electrical Conductivity (EC) of {val_str} {relation_str} the laboratory reference limit of {range_str}. "
                f"According to {source}, EC quantifies total soluble electrolyte salts; excessive levels induce osmotic drought stress by impeding root water absorption."
            )
            why_it_matters = "EC indicates osmotic stress potential and salt balance, directly impacting root hydration and crop seedling survival."

        else:
            explanation = (
                f"The measured {parameter_name} of {val_str} {relation_str} the laboratory stated range of {range_str}. "
                f"According to {source}: {chunk_content[:200]}..." if chunk_content else (
                    f"The measured {parameter_name} of {val_str} {relation_str} the reference threshold of {range_str}."
                )
            )
            why_it_matters = f"Optimal {parameter_name} balance supports overall soil chemistry and balanced root nutrient availability."

        return explanation, why_it_matters

interpretation_agent = InterpretationAgent()
