import datetime
import uuid
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    storage_url = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="UPLOADED") # UPLOADED, PROCESSING, COMPLETED, FAILED

    parameters = relationship("SoilParameterModel", back_populates="report", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="report", cascade="all, delete-orphan")
    crop_predictions = relationship("CropPredictionModel", back_populates="report", cascade="all, delete-orphan")

class SoilParameterModel(Base):
    __tablename__ = "soil_parameters"

    id = Column(String, primary_key=True, default=generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    reference_min = Column(Float, nullable=True)
    reference_max = Column(Float, nullable=True)
    reference_text = Column(String, nullable=True)
    lab_status = Column(String, nullable=True)
    computed_status = Column(String, nullable=True) # BELOW_OPTIMUM, WITHIN_RANGE, ABOVE_OPTIMUM
    source_page = Column(Integer, nullable=True)

    report = relationship("Report", back_populates="parameters")

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False)
    summary = Column(JSON, nullable=True) # {"overall_observation": "...", "key_findings": [...]}
    overall_observation = Column(String, nullable=True)
    confidence = Column(String, default="HIGH")
    retrieval_attempts = Column(Integer, default=1)
    retry_count = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    report = relationship("Report", back_populates="analysis_runs")
    evidence_items = relationship("EvidenceModel", back_populates="analysis_run", cascade="all, delete-orphan")

class KnowledgeChunkModel(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(String, primary_key=True, default=generate_uuid)
    content = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    title = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    page = Column(Integer, nullable=True)
    section = Column(String, nullable=True)
    parameter = Column(String, nullable=True)
    topic = Column(String, nullable=True)
    crop = Column(String, nullable=True)
    soil_type = Column(String, nullable=True)
    region = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    document_type = Column(String, default="agricultural_reference")
    embedding = Column(JSON, nullable=True) # List[float] vector representation for universal DB compatibility

class EvidenceModel(Base):
    __tablename__ = "evidence"

    id = Column(String, primary_key=True, default=generate_uuid)
    analysis_run_id = Column(String, ForeignKey("analysis_runs.id"), nullable=False)
    parameter_name = Column(String, nullable=False)
    claim = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    page = Column(Integer, nullable=True)
    excerpt = Column(Text, nullable=False)
    relevance = Column(String, default="HIGH")
    chunk_id = Column(String, ForeignKey("knowledge_chunks.id"), nullable=True)

    analysis_run = relationship("AnalysisRun", back_populates="evidence_items")

class CropPredictionModel(Base):
    __tablename__ = "crop_predictions"

    id = Column(String, primary_key=True, default=generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False)
    inputs_json = Column(JSON, nullable=False) # N, P, K, pH, temp, humidity, rainfall
    status = Column(String, nullable=False) # READY, INSUFFICIENT_INPUTS
    predictions_json = Column(JSON, nullable=True) # [{"crop": "rice", "probability": 0.87}, ...]
    explanation = Column(Text, nullable=True)
    limitations_json = Column(JSON, nullable=True)
    model_version = Column(String, default="1.0.0")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    report = relationship("Report", back_populates="crop_predictions")
