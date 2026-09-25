import re
from typing import Optional, List, Tuple
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.database.models import Report, SoilParameterModel, EvidenceModel, AnalysisRun
from backend.app.rag.retriever import parameter_retriever
from backend.app.services.llm_service import llm_service
from backend.app.config import settings

router = APIRouter(prefix="/reports", tags=["chat"])

class QuestionRequest(BaseModel):
    question: str = Field(description="Agronomic question scoped to the report.")
    gemini_api_key: Optional[str] = Field(default=None, description="Optional Google Gemini API key.")

class SourceCitation(BaseModel):
    source: str
    page: Optional[int] = None
    text: str

class QuestionResponse(BaseModel):
    question: str
    answer: str
    citations: List[SourceCitation]
    provider: str = "gemini"


# Common greetings and casual phrases
GREETINGS_PATTERN = re.compile(
    r"^(hi|hello|hey|greetings|howdy|good\s+(morning|afternoon|evening|day)|"
    r"who\s+are\s+you|what\s+are\s+you|what\s+can\s+you\s+do|what\s+is\s+soiltwin|"
    r"help|thanks|thank\s+you|bye|goodbye|namaste)[\s.?!]*$",
    re.IGNORECASE
)

# Obvious off-topic keywords
OFF_TOPIC_TERMS = [
    "world cup", "football", "soccer", "cricket", "basketball", "nba", "ipl",
    "binary tree", "python code", "javascript", "react", "html", "css", "c++",
    "write code", "algorithm", "capital of", "who is the president", "prime minister",
    "movie", "song", "lyrics", "celebrity", "hollywood", "bollywood", "bitcoin",
    "crypto", "stock market", "joke", "tell me a joke", "write a poem", "recipe for cake"
]

# Soil & Agronomic keywords to protect valid agricultural queries
AGRONOMIC_KEYWORDS = [
    "soil", "ph", "nitrogen", "phosphorus", "potassium", "nutrient", "fertilizer",
    "lime", "liming", "organic matter", "cec", "calcium", "magnesium", "sulfur",
    "zinc", "iron", "manganese", "copper", "boron", "aluminum", "crop", "plant",
    "loam", "clay", "sand", "yield", "compost", "manure", "deficien", "acid", "alkali",
    "salin", "report", "test", "amendment", "npk", "ppm"
]

# Canonical parameter map for fast lookup
PARAM_SYNONYMS = {
    "ph": "pH",
    "soil ph": "pH",
    "nitrogen": "N",
    "n": "N",
    "nitrate": "N",
    "phosphorus": "P",
    "p": "P",
    "phosphate": "P",
    "potassium": "K",
    "k": "K",
    "potash": "K",
    "calcium": "Ca",
    "ca": "Ca",
    "magnesium": "Mg",
    "mg": "Mg",
    "sulfur": "S",
    "sulphur": "S",
    "s": "S",
    "boron": "B",
    "b": "B",
    "manganese": "Mn",
    "mn": "Mn",
    "zinc": "Zn",
    "zn": "Zn",
    "copper": "Cu",
    "cu": "Cu",
    "iron": "Fe",
    "fe": "Fe",
    "aluminum": "Al",
    "aluminium": "Al",
    "al": "Al",
    "organic matter": "Organic Matter",
    "om": "Organic Matter",
    "cec": "CEC",
    "cation exchange capacity": "CEC",
}


def classify_intent(q: str) -> str:
    """
    Module 5: Fast local intent classification (<5ms)
    Returns: 'GREETING', 'OFF_TOPIC', 'REPORT_LOOKUP', or 'INTERPRETATION'
    """
    clean_q = q.strip().lower()

    # 1. Check GREETING / CASUAL
    if GREETINGS_PATTERN.match(clean_q) or clean_q in ["hi", "hello", "hey", "help", "thanks", "thank you"]:
        return "GREETING"

    # 2. Check OFF_TOPIC (only if no agronomic terms present)
    has_agronomic_term = any(term in clean_q for term in AGRONOMIC_KEYWORDS)
    if not has_agronomic_term:
        if any(term in clean_q for term in OFF_TOPIC_TERMS):
            return "OFF_TOPIC"
        # If question has no agronomic or soil terms and asks generic general knowledge
        if clean_q.startswith(("who won", "what is the capital", "write a code", "write python", "tell me a joke")):
            return "OFF_TOPIC"

    # 3. Check REPORT_LOOKUP (factual questions asking for measured value)
    lookup_patterns = [
        r"^what is my (?:soil\s+)?([a-z0-9\s]+)\??$",
        r"^what is the (?:soil\s+)?([a-z0-9\s]+)\??$",
        r"^how much ([a-z0-9\s]+) (?:do i have|is in my soil)\??$",
        r"^is my ([a-z0-9\s]+) (?:low|high|optimal|deficient|good|bad)\??$",
        r"^what (?:did|does) my report say about ([a-z0-9\s]+)\??$",
        r"^(?:show|tell) me (?:my\s+)?([a-z0-9\s]+) value\??$",
        r"^what are (?:all\s+)?my parameters\??$",
    ]
    for pat in lookup_patterns:
        if re.search(pat, clean_q):
            return "REPORT_LOOKUP"

    # 4. Default to INTERPRETATION & RECOMMENDATION (requires reasoning/evidence)
    return "INTERPRETATION"


def match_parameter_from_question(clean_q: str, parameters: List[SoilParameterModel]) -> Optional[SoilParameterModel]:
    """Finds which parameter is targeted in the question, if any."""
    # Check exact synonym matches first
    for syn, canonical in PARAM_SYNONYMS.items():
        # Check boundary match or word match
        if re.search(r"\b" + re.escape(syn) + r"\b", clean_q):
            for p in parameters:
                if p.name.upper() == canonical.upper():
                    return p

    # Fallback to direct name match
    for p in parameters:
        if p.name.lower() in clean_q:
            return p

    return None


@router.post("/{report_id}/ask", response_model=QuestionResponse)
async def ask_soil_ai(
    report_id: str,
    request: QuestionRequest,
    x_gemini_api_key: Optional[str] = Header(None, alias="X-Gemini-API-Key"),
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found.")

    clean_q = request.question.strip()
    intent = classify_intent(clean_q)

    # -------------------------------------------------------------
    # INTENT 1: GREETING / CASUAL (Module 5)
    # Instant, 0 citations, no LLM / RAG call
    # -------------------------------------------------------------
    if intent == "GREETING":
        return QuestionResponse(
            question=request.question,
            answer=(
                "Hello! I am SoilTwin AI, your evidence-grounded agronomic assistant. "
                "I can help you interpret your soil test report, evaluate nutrient levels (pH, N, P, K, etc.), "
                "understand fertilizer & lime recommendations, or discuss suitable crops based on your soil chemistry. "
                "What would you like to explore regarding your soil report?"
            ),
            citations=[],
            provider="SoilTwin Assistant"
        )

    # -------------------------------------------------------------
    # INTENT 2: UNRELATED / OFF-TOPIC (Module 5)
    # Politely decline, 0 citations, no LLM / RAG call
    # -------------------------------------------------------------
    if intent == "OFF_TOPIC":
        return QuestionResponse(
            question=request.question,
            answer=(
                "I am SoilTwin AI, specialized strictly in soil health analysis and agricultural recommendations. "
                "I can assist you with your soil test report, nutrient management, soil amendments, or crop suitability. "
                "How can I help you with your soil analysis today?"
            ),
            citations=[],
            provider="SoilTwin Assistant"
        )

    # Fetch report parameters for domain queries
    parameters = db.query(SoilParameterModel).filter(SoilParameterModel.report_id == report_id).all()
    if not parameters:
        raise HTTPException(status_code=400, detail="Report has not been analyzed yet.")

    matched_param = match_parameter_from_question(clean_q.lower(), parameters)

    # -------------------------------------------------------------
    # INTENT 3: REPORT LOOKUP (Module 6)
    # Fast factual lookup directly from structured database records
    # -------------------------------------------------------------
    if intent == "REPORT_LOOKUP" and matched_param:
        val_str = f"{matched_param.value} {matched_param.unit or ''}".strip()
        status_str = (matched_param.computed_status or matched_param.lab_status or "REPORTED").replace("_", " ")
        
        range_str = matched_param.reference_text or (
            f"{matched_param.reference_min} - {matched_param.reference_max} {matched_param.unit or ''}"
            if matched_param.reference_min is not None and matched_param.reference_max is not None
            else "standard agronomic baseline"
        )

        answer_text = (
            f"According to your analyzed soil report, your {matched_param.name} is {val_str}, "
            f"which is classified as {status_str} (optimal reference range is {range_str})."
        )
        # Fetch clean citations already associated with this parameter
        ev_records = (
            db.query(EvidenceModel)
            .join(AnalysisRun, EvidenceModel.analysis_run_id == AnalysisRun.id)
            .filter(AnalysisRun.report_id == report_id, EvidenceModel.parameter_name == matched_param.name)
            .all()
        )
        if ev_records and ev_records[0].claim:
            answer_text += f" {ev_records[0].claim}"

        citations: List[SourceCitation] = []
        for ev in ev_records[:2]:
            clean_snippet = (ev.excerpt or ev.claim or "").strip()
            if len(clean_snippet) > 200:
                clean_snippet = clean_snippet[:200] + "..."
            citations.append(
                SourceCitation(
                    source=ev.source or "University Agricultural Extension",
                    page=ev.page,
                    text=clean_snippet
                )
            )

        return QuestionResponse(
            question=request.question,
            answer=answer_text,
            citations=citations,
            provider="SoilTwin Report Database"
        )

    # -------------------------------------------------------------
    # INTENT 4: INTERPRETATION & RECOMMENDATION (Module 6)
    # Reasoning over extension evidence context with Gemini / LLM
    # -------------------------------------------------------------
    # Retrieve relevant extension evidence
    chunks = parameter_retriever.retrieve_for_parameter(
        parameter_name=matched_param.name if matched_param else "soil",
        value=matched_param.value if matched_param else None,
        unit=matched_param.unit if matched_param else None,
        status=matched_param.computed_status if matched_param else None
    )

    evidence_context = "\n\n".join([
        f"[{c.get('source', 'Agricultural Extension')}, Page {c.get('page', 1)}]: {c.get('content', '')}"
        for c in chunks
    ])

    param_summary = "\n".join([
        f"- {p.name}: {p.value} {p.unit or ''} ({p.computed_status or p.lab_status or 'Reported'})"
        for p in parameters
    ])

    system_prompt = (
        "You are an expert agricultural scientist advising a grower or farm manager. "
        "Answer the user's specific agronomic question clearly and actionable based on their soil test measurements "
        "and the provided university extension guidelines.\n"
        "Guidelines:\n"
        "1. Directly address what the finding means and what specific corrective actions (fertilizer, lime, organic amendments) are recommended.\n"
        "2. Synthesize clear, readable agricultural prose. Do NOT dump raw database chunks or internal code.\n"
        "3. Keep the response concise, grounded, and practical."
    )

    prompt = (
        f"Client Soil Report Measurements:\n{param_summary}\n\n"
        f"Relevant Agricultural Guidelines & Evidence:\n{evidence_context}\n\n"
        f"Question: {request.question}\n\n"
        f"Provide a synthesized, practical agronomic explanation and recommendation:"
    )

    header_key = x_gemini_api_key if isinstance(x_gemini_api_key, str) and x_gemini_api_key.strip() else None
    req_key = request.gemini_api_key if isinstance(request.gemini_api_key, str) and request.gemini_api_key.strip() else None
    env_key = settings.GEMINI_API_KEY if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip() else None

    effective_gemini_key = req_key or header_key or env_key
    provider_used = "Google Gemini 1.5 Flash" if effective_gemini_key else "SoilTwin Agronomic Engine"

    # LLM generation with graceful deterministic fallback
    try:
        raw_answer = llm_service.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            use_strong_model=False,
            gemini_api_key=effective_gemini_key
        )
    except Exception as exc:
        raw_answer = None

    if not raw_answer or "mock" in provider_used.lower() or not effective_gemini_key:
        # Fallback to high quality deterministic domain explanation
        if matched_param:
            ev_records = (
                db.query(EvidenceModel)
                .join(AnalysisRun, EvidenceModel.analysis_run_id == AnalysisRun.id)
                .filter(AnalysisRun.report_id == report_id, EvidenceModel.parameter_name == matched_param.name)
                .all()
            )
            obs = ev_records[0].claim if ev_records else f"{matched_param.name} is currently measured at {matched_param.value}."
            raw_answer = (
                f"Regarding your question on {matched_param.name}: According to your report, the measured level is "
                f"{matched_param.value} {matched_param.unit or ''} ({matched_param.computed_status or matched_param.lab_status or 'Reported'}). "
                f"{obs} Standard extension recommendations advise adjusting application rates or applying appropriate soil amendments "
                f"to bring levels into the optimal agronomic range."
            )
        else:
            raw_answer = (
                "Based on your soil test report and agricultural extension guidelines, soil nutrient balance and pH "
                "directly control nutrient availability. Refer to the specific parameter tabs in your dashboard for tailored management recommendations."
            )

    # Prepare clean, concise citations (first 1-2 clean sentences, max 200 chars, no raw dump)
    clean_citations: List[SourceCitation] = []
    for c in chunks[:2]:
        text_body = c.get("content", "").strip()
        first_sentence = text_body.split(". ")[0] + "." if ". " in text_body else text_body
        if len(first_sentence) > 220:
            first_sentence = first_sentence[:220] + "..."
        clean_citations.append(
            SourceCitation(
                source=c.get("source", "University Extension Soil Guide"),
                page=c.get("page", 1),
                text=first_sentence
            )
        )

    return QuestionResponse(
        question=request.question,
        answer=raw_answer,
        citations=clean_citations,
        provider=provider_used
    )
