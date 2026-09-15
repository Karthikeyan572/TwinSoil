import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.database.database import get_db, SessionLocal
from backend.app.database.models import Report, SoilParameterModel, AnalysisRun, EvidenceModel
from backend.app.services.storage_service import storage_service
from backend.app.agents.supervisor import supervisor_agent
from backend.app.config import settings

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/upload")
async def upload_report(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a soil test report (PDF, PNG, JPG).
    """
    allowed_extensions = [".pdf", ".png", ".jpg", ".jpeg"]
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. Please upload a PDF, PNG, or JPG file."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Max size 15 MB
    if len(file_bytes) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds maximum 15 MB limit.")

    file_id, file_path = storage_service.save_file(file_bytes, file.filename)

    report = Report(
        id=file_id,
        filename=file.filename,
        storage_url=file_path,
        status="UPLOADED"
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "filename": report.filename,
        "status": report.status,
        "uploaded_at": report.uploaded_at.isoformat()
    }

@router.post("/{report_id}/analyze")
async def analyze_report(report_id: str, db: Session = Depends(get_db)):
    """
    Triggers the LangGraph agentic workflow on the uploaded report.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found.")

    report.status = "PROCESSING"
    db.commit()

    try:
        workflow_result = supervisor_agent.execute_analysis(
            report_id=report.id,
            file_path=report.storage_url
        )
        final_output = workflow_result.get("final_output", {})

        # Clear existing parameters and runs if re-analyzing
        db.query(SoilParameterModel).filter(SoilParameterModel.report_id == report_id).delete()
        db.query(AnalysisRun).filter(AnalysisRun.report_id == report_id).delete()

        # Save analysis run
        summary_data = final_output.get("summary", {})
        analysis_run = AnalysisRun(
            report_id=report.id,
            summary=summary_data,
            overall_observation=summary_data.get("overall_observation", "Needs Attention"),
            confidence="HIGH",
            retrieval_attempts=1,
            retry_count=0
        )
        db.add(analysis_run)
        db.flush()

        # Save extracted parameters and evidence
        for param in final_output.get("parameters", []):
            db_param = SoilParameterModel(
                report_id=report.id,
                name=param["name"],
                value=param.get("value"),
                unit=param.get("unit"),
                computed_status=param.get("status"),
                source_page=1
            )
            db.add(db_param)

            for ev in param.get("evidence", []):
                db_ev = EvidenceModel(
                    analysis_run_id=analysis_run.id,
                    parameter_name=param["name"],
                    claim=param.get("explanation", ""),
                    source=ev.get("source", "Agricultural Extension Reference"),
                    page=ev.get("page", 1),
                    excerpt=ev.get("text", ""),
                    relevance=ev.get("relevance", "HIGH")
                )
                db.add(db_ev)

        report.status = "COMPLETED"
        db.commit()

        return {
            **final_output,
            "pipeline_steps": workflow_result.get("pipeline_steps", [])
        }
    except Exception as e:
        report.status = "FAILED"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/{report_id}")
async def get_report(report_id: str, db: Session = Depends(get_db)):
    """
    Retrieves the report metadata and latest analysis summary.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found.")

    latest_run = db.query(AnalysisRun).filter(AnalysisRun.report_id == report_id).order_by(AnalysisRun.started_at.desc()).first()
    
    return {
        "report_id": report.id,
        "filename": report.filename,
        "status": report.status,
        "uploaded_at": report.uploaded_at.isoformat(),
        "summary": latest_run.summary if latest_run else None,
        "overall_observation": latest_run.overall_observation if latest_run else None
    }

@router.get("/{report_id}/parameters")
async def get_report_parameters(report_id: str, db: Session = Depends(get_db)):
    params = db.query(SoilParameterModel).filter(SoilParameterModel.report_id == report_id).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "value": p.value,
            "unit": p.unit,
            "reference_min": p.reference_min,
            "reference_max": p.reference_max,
            "reference_text": p.reference_text,
            "lab_status": p.lab_status,
            "computed_status": p.computed_status
        }
        for p in params
    ]

@router.get("/{report_id}/evidence")
async def get_report_evidence(report_id: str, db: Session = Depends(get_db)):
    latest_run = db.query(AnalysisRun).filter(AnalysisRun.report_id == report_id).order_by(AnalysisRun.started_at.desc()).first()
    if not latest_run:
        return []
    
    ev_items = db.query(EvidenceModel).filter(EvidenceModel.analysis_run_id == latest_run.id).all()
    return [
        {
            "parameter": e.parameter_name,
            "claim": e.claim,
            "source": e.source,
            "page": e.page,
            "text": e.excerpt,
            "relevance": e.relevance
        }
        for e in ev_items
    ]

@router.post("/demo/duffy-rear")
async def load_demo_duffy_rear(db: Session = Depends(get_db)):
    """
    Loads the canonical Duffy Rear fixture instantly for Demo Mode / judge evaluation.
    """
    fixtures_dir = settings.BASE_DIR / "tests" / "fixtures"
    fixture_pdf = fixtures_dir / "duffy_rear.pdf"
    
    if not fixture_pdf.exists():
        from backend.tests.fixtures.generate_synthetic_reports import generate_all_fixtures
        generate_all_fixtures()

    with open(fixture_pdf, "rb") as f:
        file_bytes = f.read()

    file_id, file_path = storage_service.save_file(file_bytes, "duffy_rear_synthetic.pdf")
    report = Report(
        id=file_id,
        filename="duffy_rear_synthetic.pdf",
        storage_url=file_path,
        status="PROCESSING"
    )
    db.add(report)
    db.commit()

    # Execute workflow
    workflow_result = supervisor_agent.execute_analysis(
        report_id=report.id,
        file_path=report.storage_url
    )
    final_output = workflow_result.get("final_output", {})

    summary_data = final_output.get("summary", {})
    analysis_run = AnalysisRun(
        report_id=report.id,
        summary=summary_data,
        overall_observation=summary_data.get("overall_observation", "Needs Attention"),
        confidence="HIGH"
    )
    db.add(analysis_run)
    db.flush()

    for param in final_output.get("parameters", []):
        db_param = SoilParameterModel(
            report_id=report.id,
            name=param["name"],
            value=param.get("value"),
            unit=param.get("unit"),
            computed_status=param.get("status")
        )
        db.add(db_param)

        for ev in param.get("evidence", []):
            db_ev = EvidenceModel(
                analysis_run_id=analysis_run.id,
                parameter_name=param["name"],
                claim=param.get("explanation", ""),
                source=ev.get("source", "Agricultural Extension Reference"),
                page=ev.get("page", 1),
                excerpt=ev.get("text", ""),
                relevance=ev.get("relevance", "HIGH")
            )
            db.add(db_ev)

    report.status = "COMPLETED"
    db.commit()

    return {
        "report_id": report.id,
        **final_output,
        "pipeline_steps": workflow_result.get("pipeline_steps", [])
    }
