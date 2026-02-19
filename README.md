# MedGuardian Edge

> **Offline Clinical Safety & Documentation Assistant**  
> Powered by MedGemma via Ollama · React + Vite · FastAPI

---

## Overview

MedGuardian Edge is a fully offline, competition-ready clinical AI assistant that provides:

| Feature | Endpoint |
|---|---|
| 🔴 Patient Risk Assessment | `POST /api/risk/assess` |
| 🧪 Lab Report Analysis | `POST /api/lab/analyze` |
| 💊 Prescription Safety Checker | `POST /api/prescription/check` |
| 📋 SOAP Note Generator | `POST /api/documentation/soap` |
| 💬 Patient-Friendly Explanation | `POST /api/documentation/explain` |

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | ≥ 3.10 | [python.org](https://python.org) |
| Node.js | ≥ 18 | [nodejs.org](https://nodejs.org) |
| Ollama | latest | [ollama.com](https://ollama.com) |
| MedGemma model | — | `ollama pull medgemma` |

---

## Project Structure

```
MedGuardian-Edge/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── .env                     # Environment variables
│   ├── requirements.txt
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response models
│   ├── routes/
│   │   ├── risk.py              # Patient risk assessment
│   │   ├── lab.py               # Lab report analysis
│   │   ├── prescription.py      # Prescription safety
│   │   └── documentation.py     # SOAP note + explanation
│   └── services/
│       ├── ollama_client.py     # Async Ollama API client
│       ├── prompts.py           # All LLM prompts
│       └── safety_rules.py      # Deterministic safety checks
└── frontend/
    ├── index.html
    ├── vite.config.js           # Dev proxy → backend
    ├── package.json
    └── src/
        ├── App.jsx              # Main application
        ├── main.jsx
        ├── index.css
        ├── components/
        │   ├── PatientForm.jsx
        │   ├── LabInput.jsx
        │   ├── PrescriptionInput.jsx
        │   └── ResultsPanel.jsx
        └── services/
            └── api.js           # API service layer
```

---

## Setup & Run

### 1. Start Ollama

```bash
ollama serve
# In a separate terminal, verify the model is available:
ollama list
# If medgemma is not listed:
ollama pull medgemma
```

### 2. Backend

```bash
cd MedGuardian-Edge/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (edit as needed)
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux

# Start the backend
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**  
Interactive API docs: **http://localhost:8000/docs**

### 3. Frontend

```bash
cd MedGuardian-Edge/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## Environment Variables

Edit `backend/.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=medgemma
OLLAMA_TIMEOUT=120
HOST=0.0.0.0
PORT=8000
```

> **Note:** Change `OLLAMA_MODEL` to match your exact model name from `ollama list`.

---

## Example Test Payloads

### Patient Risk Assessment
```json
POST /api/risk/assess
{
  "age": 65,
  "gender": "Male",
  "symptoms": ["chest pain", "shortness of breath", "diaphoresis"],
  "vitals": {
    "systolic_bp": 185,
    "diastolic_bp": 110,
    "heart_rate": 102,
    "temperature": 37.2,
    "spo2": 94,
    "respiratory_rate": 22
  },
  "comorbidities": ["hypertension", "diabetes", "coronary artery disease"]
}
```

### Lab Report Analysis
```json
POST /api/lab/analyze
{
  "report_text": "Hemoglobin: 8.2 g/dL (ref: 12-16)\nWBC: 14,500 /μL (ref: 4,000-11,000)\nCreatinine: 2.1 mg/dL (ref: 0.6-1.2)\nBlood Glucose: 320 mg/dL (ref: 70-100)\nSodium: 128 mEq/L (ref: 135-145)",
  "patient_context": "65-year-old diabetic with CKD"
}
```

### Prescription Safety
```json
POST /api/prescription/check
{
  "medications": ["Warfarin", "Aspirin", "Metformin", "Lisinopril", "Atorvastatin"],
  "patient_age": 65,
  "patient_conditions": ["atrial fibrillation", "type 2 diabetes", "hypertension"]
}
```

### SOAP Note
```json
POST /api/documentation/soap
{
  "patient_summary": "65-year-old male with chest pain and shortness of breath for 2 hours",
  "symptoms": ["chest pain", "shortness of breath", "diaphoresis"],
  "examination_findings": "BP 185/110, HR 102, SpO2 94%, diaphoretic",
  "investigations": "ECG: ST elevation in leads II, III, aVF"
}
```

### Patient Explanation
```json
POST /api/documentation/explain
{
  "medical_summary": "Patient presents with STEMI requiring urgent PCI. Troponin elevated at 2.4. Started on dual antiplatelet therapy and heparin.",
  "reading_level": "simple"
}
```

---

## Architecture Notes

- **Deterministic Safety Rules** run *before* LLM inference for instant, reliable alerts (e.g., BP ≥ 180 → hypertensive crisis)
- **LLM calls** use `format: "json"` to force structured output from Ollama
- **Vite proxy** routes `/api/*` to the FastAPI backend — no CORS issues in development
- **Parallel analysis** — all 5 features run concurrently via `Promise.allSettled`
- **No database** — fully stateless, offline-first

---

## Health Check

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "ollama": "connected",
  "model": "medgemma"
}
```

---

*MedGuardian Edge — For clinical decision support only. Not a substitute for professional medical judgment.*
