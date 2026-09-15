# SoilTwin AI — Understand Your Soil. Backed by Evidence.

SoilTwin AI is a specialized agricultural intelligence system that converts soil-test reports (PDF/images) into structured, evidence-grounded, farmer-friendly explanations of every scientifically relevant parameter, paired with a real trained ML-based crop suitability classifier.

---

## 🌾 Core Philosophy & Non-Negotiable Safety Rules

1. **Zero Hallucination / No Silent Inventions**: The system never invents missing soil values, environmental conditions (`temperature`, `humidity`, `rainfall`), laboratory ranges, or citations. Missing weather values trigger `INSUFFICIENT_INPUTS` honestly.
2. **Deterministic Verification**: Numerical status classification (`BELOW_OPTIMUM`, `WITHIN_RANGE`, `ABOVE_OPTIMUM`) is performed deterministically in Python against reported lab ranges, preserving verbatim lab categories alongside computed status.
3. **Evidence-Grounded RAG**: Explanations cite audited university extension publications (Penn State, Cornell, Purdue, USDA NRCS) logged in `knowledge_base/manifest.json`.
4. **Real Trained ML Classifier**: Crop recommendations use a trained scikit-learn model on the Kaggle Crop Recommendation dataset, labeled as *"model confidence" / "prediction probability"*, with explicit disclaimers (*"This is a model-based suitability prediction, not a guaranteed yield or success probability"*).

---

## 🏛️ The Three-Layer Architecture

```
USER / FARMER
     │
     ▼
React Web Frontend (Vite + TypeScript + Tailwind + Recharts)
     │
     ▼ REST JSON
FastAPI Backend (Python, async)
     │
SUPERVISOR AGENT (LangGraph State Machine)
     ├── 1. Parser Agent (PyMuPDF for digital text; Tesseract/EasyOCR fallback)
     ├── 2. Extraction Agent (Pydantic validation + canonical normalization)
     ├── 3. Deterministic Validator (Python numerical range validation)
     ├── 4. Retrieval Agent (Parameter-aware vector search across extension RAG)
     ├── 5. Soil Interpretation Agent (Evidence-grounded explanations)
     ├── 6. Critic Validation Agent (Bounded retries: MAX_RETRIES = 2)
     └── 7. Crop ML Agent (Strict input checks + ExtraTrees / Random Forest classifier)
```

1. **AGENTIC AI Layer**: Decides WHAT to do and WHEN (Supervisor, Parser, Extraction, Retrieval, Interpreter, Critic, Crop agents).
2. **RAG Layer**: Provides KNOWLEDGE and EVIDENCE (SentenceTransformers `all-MiniLM-L6-v2` -> pgvector / persistent vector store -> parameter context).
3. **LLM OPTIMIZATION Layer**: Makes the system EFFICIENT (adaptive retrieval starting at `top_k = 3`, context compression, model routing, caching, early exits, and token limits).

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Backend Setup

```bash
# Clone and enter directory
cd "d:/git/TWINSOIL AI"

# Install backend dependencies
pip install -r backend/requirements.txt

# Ingest audited knowledge base
python -m backend.app.rag.ingestion

# Train and benchmark ML crop models
python -m backend.ml.train_crop_model

# Run backend API server (runs at http://localhost:8000)
python -m backend.app.main
```

### 2. Frontend Setup

```bash
# In a new terminal, enter frontend directory
cd "d:/git/TWINSOIL AI/frontend"

# Install dependencies
npm install

# Start Vite development server (runs at http://localhost:5173)
npm run dev
```

### 3. Docker Deployment (Optional)

```bash
# Start Postgres with pgvector, FastAPI backend, and React frontend
docker-compose up --build
```
- Web UI: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

---

## 🧪 1-Click Judge Demo Mode

To evaluate the system within 10 seconds without needing to upload a file:
1. Open the web app (`http://localhost:5173`).
2. Click **"Try Demo Soil Report"** in the top navigation or hero section.
3. The app loads the canonical **"Duffy Rear"** synthetic benchmark fixture instantly:
   - 15 parameters extracted with exact values, units, and ranges (`pH 4.5 BELOW OPTIMUM`, `Potassium 47 ppm DEFICIENT`, `Al 94 ppm HIGH`, etc.)
   - Recharts visual comparison vs. laboratory ranges
   - Evidence drawer linking each claim to university extension guides (`Claim -> Evidence -> Source -> Page`)
   - Crop Suitability tab demonstrating the strict safety rule: initially prompts for missing climate inputs, and evaluates suitability when provided.

---

## 📊 Evaluation & Benchmarks

### ML Crop Classifier Benchmark
Evaluated on the Kaggle Crop Recommendation dataset (`atharvaingle/crop-recommendation-dataset`, 2,200 samples across 22 crops):
- **ExtraTreesClassifier (Selected)**: **98.64% Accuracy** | **98.64% Macro F1**
- **RandomForestClassifier**: 97.95% Accuracy | 97.94% Macro F1
- **GradientBoostingClassifier**: 96.14% Accuracy | 96.14% Macro F1

Artifacts saved to:
- `backend/models/crop_recommendation_model.pkl`
- `backend/models/model_metadata.json`

### Automated Test Suite
Run the test suite:
```bash
python -m pytest backend/tests/test_pipeline.py -v
```
Covers:
- `/api/health` health checks
- Canonical parameter normalization (`pH`, `Organic Matter`, `CEC`, `K`, etc.)
- Deterministic numerical validation (`BELOW_OPTIMUM`, `WITHIN_RANGE`, `ABOVE_OPTIMUM`)
- Crop Agent missing input refusal (`INSUFFICIENT_INPUTS`)
- Crop Agent prediction with model confidence and yield disclaimers
- Critic Agent validation & retry boundary
- End-to-end demo endpoint pipeline

---

## 🔌 API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health and configured LLM provider |
| `POST` | `/api/reports/upload` | Upload PDF/PNG/JPG soil report |
| `POST` | `/api/reports/{id}/analyze` | Trigger LangGraph agentic workflow |
| `GET` | `/api/reports/{id}` | Get report status and summary |
| `GET` | `/api/reports/{id}/parameters` | Get extracted parameters |
| `GET` | `/api/reports/{id}/evidence` | Get full claim-to-evidence citations |
| `POST` | `/api/reports/{id}/crops` | Evaluate ML crop suitability |
| `POST` | `/api/reports/{id}/ask` | Report-scoped scientific Q&A |
| `POST` | `/api/reports/demo/duffy-rear` | Instant 1-click demo loader |

Interactive Swagger documentation available at: `http://localhost:8000/docs`

---

## 📜 Dataset & Provenance Manifest

All knowledge base documents are tracked in `backend/knowledge_base/manifest.json`:
- **Penn State Extension**: *Soil Acidity and Liming: Interpreting Soil pH* (2023)
- **Iowa State University Extension**: *Cation Exchange Capacity in Soils* (2022)
- **Cornell University Cooperative Extension**: *Comprehensive Assessment of Soil Health* (2021)
- **University of Minnesota Extension**: *Understanding Soil Phosphorus and Potassium* (2023)
- **Purdue University Extension**: *Secondary and Micronutrient Fertility Management* (2022)
- **USDA Natural Resources Conservation Service (NRCS)**: *Soil Quality - Heavy Metals* (2020)
- **University of Georgia Extension**: *Soil Salinity and Electrical Conductivity* (2021)

---

## 🛡️ Limitations & Future Enhancements

- **Limitations**: Regional fertilizer calibration requires local field calibration; model predictions do not reflect real-time pest cycles or active drought events.
- **Future Work**: Integration with live hyper-local weather APIs to auto-populate temperature, humidity, and rainfall; mobile Flutter companion client; multi-lingual voice explanations for regional farmers.
