"""
MedGuardian Edge - Pydantic Schemas
All request and response models for the 5 core clinical features.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


# ─────────────────────────────────────────────
# 1. Patient Risk Assessment
# ─────────────────────────────────────────────

class Vitals(BaseModel):
    systolic_bp: Optional[int] = Field(None, description="Systolic blood pressure (mmHg)")
    diastolic_bp: Optional[int] = Field(None, description="Diastolic blood pressure (mmHg)")
    heart_rate: Optional[int] = Field(None, description="Heart rate (bpm)")
    temperature: Optional[float] = Field(None, description="Body temperature (°C)")
    spo2: Optional[float] = Field(None, description="Oxygen saturation (%)")
    respiratory_rate: Optional[int] = Field(None, description="Respiratory rate (breaths/min)")


class PatientRiskRequest(BaseModel):
    age: int = Field(..., ge=0, le=130, description="Patient age in years")
    gender: str = Field(..., description="Patient gender (Male/Female/Other)")
    symptoms: List[str] = Field(..., description="List of presenting symptoms")
    vitals: Optional[Vitals] = Field(None, description="Current vital signs")
    comorbidities: Optional[List[str]] = Field(default=[], description="Existing medical conditions")


class PatientRiskResponse(BaseModel):
    risk_level: str = Field(..., description="Low / Medium / High")
    red_flags: List[str] = Field(default=[], description="Critical warning signs detected")
    differential_diagnosis: List[str] = Field(default=[], description="Possible diagnoses")
    recommended_action: str = Field(..., description="Immediate clinical recommendation")
    confidence: str = Field(..., description="Model confidence level")
    safety_alerts: Optional[List[str]] = Field(default=[], description="Deterministic safety rule alerts")


# ─────────────────────────────────────────────
# 2. Lab Report Analysis
# ─────────────────────────────────────────────

class LabReportRequest(BaseModel):
    lab_text: Optional[str] = Field(None, description="Raw lab report text (optional if image provided)")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data for vision analysis")
    patient_context: Optional[str] = Field(None, description="Optional patient context for interpretation")


class AbnormalValue(BaseModel):
    parameter: str
    value: str
    reference_range: str
    status: str  # "High" / "Low" / "Critical"


class LabReportResponse(BaseModel):
    abnormal_values: List[AbnormalValue] = Field(default=[])
    clinical_interpretation: str = Field(..., description="Clinical meaning of findings")
    risk_summary: str = Field(..., description="Overall risk assessment from labs")
    recommended_next_steps: List[str] = Field(default=[], description="Suggested clinical follow-up")


# ─────────────────────────────────────────────
# 3. Prescription Safety Checker
# ─────────────────────────────────────────────

class PrescriptionSafetyRequest(BaseModel):
    medications: List[str] = Field(..., min_length=1, description="List of medication names")
    patient_age: Optional[int] = Field(None, description="Patient age for age-specific warnings")
    patient_conditions: Optional[List[str]] = Field(default=[], description="Known conditions for contraindication check")


class DrugInteraction(BaseModel):
    drug_a: str
    drug_b: str
    severity: str  # "Minor" / "Moderate" / "Major"
    description: str


class PrescriptionSafetyResponse(BaseModel):
    drug_interactions: List[DrugInteraction] = Field(default=[])
    contraindications: List[str] = Field(default=[])
    safety_warnings: List[str] = Field(default=[])


# ─────────────────────────────────────────────
# 4. SOAP Note Generator
# ─────────────────────────────────────────────

class SOAPNoteRequest(BaseModel):
    patient_summary: str = Field(..., min_length=10, description="Clinical summary of the patient encounter")
    symptoms: Optional[List[str]] = Field(default=[], description="Patient-reported symptoms")
    examination_findings: Optional[str] = Field(None, description="Physical examination findings")
    investigations: Optional[str] = Field(None, description="Lab/imaging results")


class SOAPNoteResponse(BaseModel):
    subjective: str = Field(..., description="Patient-reported complaints and history")
    objective: str = Field(..., description="Measurable clinical findings")
    assessment: str = Field(..., description="Clinical diagnosis and reasoning")
    plan: str = Field(..., description="Treatment and follow-up plan")


# ─────────────────────────────────────────────
# 5. Patient-Friendly Explanation
# ─────────────────────────────────────────────

class ExplanationRequest(BaseModel):
    medical_summary: str = Field(..., min_length=10, description="Medical text to simplify")
    reading_level: Optional[str] = Field("simple", description="Target reading level: simple / moderate")


class ExplanationResponse(BaseModel):
    explanation: str = Field(..., description="Layman-friendly explanation")
    key_points: List[str] = Field(default=[], description="Bullet-point key takeaways")
    follow_up_advice: str = Field(..., description="What the patient should do next")


# ─────────────────────────────────────────────
# Generic Error Response
# ─────────────────────────────────────────────

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
