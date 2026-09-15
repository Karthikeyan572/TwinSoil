from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.database.models import Report, SoilParameterModel, EvidenceModel, AnalysisRun
from backend.app.rag.retriever import parameter_retriever
from backend.app.services.llm_service import llm_service

router = APIRouter(prefix="/reports", tags=["chat"])

class QuestionRequest(BaseModel):
    question: str = Field(description="Agronomic question scoped to the report.")

class SourceCitation(BaseModel):
    source: str
    page: Optional[int] = None
    text: str

class QuestionResponse(BaseModel):
    question: str
    answer: str
    citations: List[SourceCitation]

@router.post("/{report_id}/ask", response_model=QuestionResponse)
async def ask_soil_ai(report_id: str, request: QuestionRequest, db: Session = Depends(get_db)):
    """
    Ask an evidence-backed agronomic question strictly scoped to the report and RAG knowledge base.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found.")

    parameters = db.query(SoilParameterModel).filter(SoilParameterModel.report_id == report_id).all()
    if not parameters:
        raise HTTPException(status_code=400, detail="Report has not been analyzed yet.")

    # Find relevant parameter if mentioned
    user_q = request.question.lower()
    matched_param = None
    for p in parameters:
        if p.name.lower() in user_q or (p.name == "K" and "potassium" in user_q) or (p.name == "P" and "phosphorus" in user_q) or (p.name == "N" and "nitrogen" in user_q):
            matched_param = p
            break

    param_context = "\n".join([
        f"- {p.name}: {p.value} {p.unit or ''} (Status: {p.computed_status or p.lab_status or 'N/A'})"
        for p in parameters
    ])

    # Retrieve relevant extension evidence
    chunks = parameter_retriever.retrieve_for_parameter(
        parameter_name=matched_param.name if matched_param else "soil",
        value=matched_param.value if matched_param else None,
        unit=matched_param.unit if matched_param else None,
        status=matched_param.computed_status if matched_param else None
    )

    evidence_context = "\n\n".join([
        f"[{c.get('source')}, Page {c.get('page', 'N/A')}]: {c.get('content')}"
        for c in chunks
    ])

    system_prompt = (
        "You are an agricultural soil scientist answering farmer inquiries strictly based on their soil test report "
        "and authoritative university extension citations. Never hallucinate facts or give unbacked recommendations. "
        "Keep answers concise, direct, and farmer-accessible."
    )

    prompt = (
        f"Report Parameters:\n{param_context}\n\n"
        f"Authoritative Scientific Evidence:\n{evidence_context}\n\n"
        f"Farmer's Question: {request.question}\n\n"
        f"Answer clearly and cite the sources."
    )

    answer = llm_service.generate_text(
        prompt=prompt,
        system_prompt=system_prompt,
        use_strong_model=False
    )

    citations = [
        SourceCitation(
            source=c.get("source", "Agricultural Reference"),
            page=c.get("page", 1),
            text=c.get("content", "")
        )
        for c in chunks[:2]
    ]

    return QuestionResponse(
        question=request.question,
        answer=answer,
        citations=citations
    )
