"""
MedGuardian Edge - LLM Prompts
All system and user prompts for the 5 clinical features.
Every prompt enforces STRICT JSON output — no prose outside the JSON object.
"""

from typing import List, Optional


# ─────────────────────────────────────────────
# Shared JSON enforcement footer
# ─────────────────────────────────────────────
_JSON_RULE = (
    "\n\nCRITICAL RULES:"
    "\n- Return STRICT JSON only. No text before or after the JSON object."
    "\n- Do not include explanations, markdown, or code fences outside the JSON."
    "\n- If uncertain about a value, still return valid JSON with your best estimate."
    "\n- Every key in the schema below MUST be present in your response."
)


# ─────────────────────────────────────────────
# 1. Patient Risk Assessment
# ─────────────────────────────────────────────

RISK_SYSTEM_PROMPT = (
    "You are MedGuardian Edge, an expert clinical decision support AI. "
    "Assess patient risk based on clinical data using evidence-based guidelines. "
    "You MUST respond ONLY with valid JSON. No explanations, no markdown, no extra text."
)

def build_risk_prompt(
    age: int,
    gender: str,
    symptoms: List[str],
    vitals: Optional[dict],
    comorbidities: List[str],
) -> str:
    vitals_str = "Not provided"
    if vitals:
        parts = []
        if vitals.get("systolic_bp") is not None:
            parts.append(f"BP: {vitals['systolic_bp']}/{vitals.get('diastolic_bp', '?')} mmHg")
        if vitals.get("heart_rate") is not None:
            parts.append(f"HR: {vitals['heart_rate']} bpm")
        if vitals.get("temperature") is not None:
            parts.append(f"Temp: {vitals['temperature']}°C")
        if vitals.get("spo2") is not None:
            parts.append(f"SpO2: {vitals['spo2']}%")
        if vitals.get("respiratory_rate") is not None:
            parts.append(f"RR: {vitals['respiratory_rate']} breaths/min")
        vitals_str = ", ".join(parts) if parts else "Not provided"

    return f"""Assess the following patient and return a JSON risk assessment.

PATIENT DATA:
- Age: {age} years
- Gender: {gender}
- Symptoms: {', '.join(symptoms)}
- Vitals: {vitals_str}
- Comorbidities: {', '.join(comorbidities) if comorbidities else 'None reported'}

Return ONLY this JSON structure:
{{
  "risk_level": "Low" | "Medium" | "High",
  "red_flags": ["critical warning sign 1", "..."],
  "differential_diagnosis": ["most likely diagnosis", "diagnosis 2", "diagnosis 3"],
  "recommended_action": "specific immediate action",
  "confidence": "Low" | "Medium" | "High"
}}{_JSON_RULE}"""


# ─────────────────────────────────────────────
# 2. Lab Report Analysis
# ─────────────────────────────────────────────

LAB_SYSTEM_PROMPT = (
    "You are MedGuardian Edge, an expert clinical pathology AI. "
    "Analyze lab reports and identify abnormal values with clinical significance. "
    "You MUST respond ONLY with valid JSON. No explanations, no markdown, no extra text."
)

def build_lab_prompt(report_text: str, patient_context: Optional[str]) -> str:
    context_str = f"\nPatient Context: {patient_context}" if patient_context else ""
    return f"""Analyze the following lab report and return structured findings.{context_str}

LAB REPORT:
{report_text}

Return ONLY this JSON structure:
{{
  "abnormal_values": [
    {{
      "parameter": "test name",
      "value": "reported value with units",
      "reference_range": "normal range",
      "status": "High" | "Low" | "Critical"
    }}
  ],
  "clinical_interpretation": "what these results mean clinically",
  "risk_summary": "overall risk level and key concern from these labs"
}}{_JSON_RULE}"""


# ─────────────────────────────────────────────
# 3. Prescription Safety Checker
# ─────────────────────────────────────────────

PRESCRIPTION_SYSTEM_PROMPT = (
    "You are MedGuardian Edge, an expert clinical pharmacology AI. "
    "Check medication lists for drug interactions, contraindications, and safety warnings. "
    "You MUST respond ONLY with valid JSON. No explanations, no markdown, no extra text. "
    "Be thorough and clinically accurate."
)

def build_prescription_prompt(
    medications: List[str],
    patient_age: Optional[int],
    patient_conditions: List[str],
) -> str:
    age_str = f"Patient Age: {patient_age} years" if patient_age else "Age: Not provided"
    conditions_str = ", ".join(patient_conditions) if patient_conditions else "None reported"
    return f"""Check the following medication list for safety issues.

{age_str}
Patient Conditions: {conditions_str}
Medications: {', '.join(medications)}

Return ONLY this JSON structure:
{{
  "drug_interactions": [
    {{
      "drug_a": "medication name",
      "drug_b": "medication name",
      "severity": "Minor" | "Moderate" | "Major",
      "description": "clinical significance"
    }}
  ],
  "contraindications": ["contraindication 1", "..."],
  "safety_warnings": ["warning 1", "..."]
}}{_JSON_RULE}"""


# ─────────────────────────────────────────────
# 4. SOAP Note Generator
# ─────────────────────────────────────────────

SOAP_SYSTEM_PROMPT = (
    "You are MedGuardian Edge, an expert clinical documentation AI. "
    "Generate professional SOAP notes from clinical summaries using formal medical language. "
    "You MUST respond ONLY with valid JSON. No explanations, no markdown, no extra text."
)

def build_soap_prompt(
    patient_summary: str,
    symptoms: List[str],
    examination_findings: Optional[str],
    investigations: Optional[str],
) -> str:
    symptoms_str = f"\nSymptoms: {', '.join(symptoms)}" if symptoms else ""
    exam_str = f"\nExamination Findings: {examination_findings}" if examination_findings else ""
    investigations_str = f"\nInvestigations: {investigations}" if investigations else ""
    return f"""Generate a professional SOAP note from the following clinical information.

CLINICAL SUMMARY:
{patient_summary}{symptoms_str}{exam_str}{investigations_str}

Return ONLY this JSON structure:
{{
  "subjective": "Patient-reported complaints, history, and symptoms in clinical language",
  "objective": "Measurable findings: vitals, physical exam, lab results",
  "assessment": "Clinical diagnosis, differential diagnoses, and clinical reasoning",
  "plan": "Treatment plan, medications, investigations ordered, follow-up instructions"
}}{_JSON_RULE}"""


# ─────────────────────────────────────────────
# 5. Patient-Friendly Explanation
# ─────────────────────────────────────────────

EXPLANATION_SYSTEM_PROMPT = (
    "You are MedGuardian Edge, a patient communication AI. "
    "Convert complex medical information into simple, compassionate language patients can understand. "
    "You MUST respond ONLY with valid JSON. No explanations, no markdown, no extra text. "
    "Use plain English. Avoid medical jargon. Be reassuring but accurate."
)

def build_explanation_prompt(medical_summary: str, reading_level: str) -> str:
    level_instruction = (
        "Use very simple words. Imagine explaining to someone with no medical background."
        if reading_level == "simple"
        else "Use moderately simple language. Basic medical terms are acceptable if explained."
    )
    return f"""Convert the following medical information into a patient-friendly explanation.

Reading Level: {level_instruction}

MEDICAL SUMMARY:
{medical_summary}

Return ONLY this JSON structure:
{{
  "explanation": "Simple, clear explanation in 2-3 paragraphs",
  "key_points": ["simple key point 1", "key point 2", "key point 3"],
  "follow_up_advice": "What the patient should do next, in simple terms"
}}{_JSON_RULE}"""
