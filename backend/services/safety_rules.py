"""
MedGuardian Edge - Deterministic Safety Rule Engine
Rule-based checks that run BEFORE LLM inference.
Provides instant, reliable safety alerts and a severity score.
"""

from typing import List, Optional, Dict, Any
from backend.models.schemas import Vitals


# ─────────────────────────────────────────────
# Vital Signs Safety Rules
# ─────────────────────────────────────────────

def evaluate_vitals(vitals: dict) -> Dict[str, Any]:
    """
    Apply deterministic clinical safety rules to a vitals dict.

    Each triggered rule appends a message to hard_alerts and adds
    2 points to severity_score.

    Returns:
        {
            "hard_alerts": List[str],
            "severity_score": int
        }
    """
    hard_alerts: List[str] = []
    severity_score: int = 0

    if not vitals:
        return {"hard_alerts": hard_alerts, "severity_score": severity_score}

    sbp = vitals.get("systolic_bp")
    dbp = vitals.get("diastolic_bp")
    hr  = vitals.get("heart_rate")
    temp = vitals.get("temperature")
    spo2 = vitals.get("spo2")
    rr   = vitals.get("respiratory_rate")

    # ── Blood Pressure ──────────────────────
    if sbp is not None:
        if sbp > 180:
            hard_alerts.append(
                f"CRITICAL: Hypertensive crisis — Systolic BP {sbp} mmHg > 180. "
                "Immediate medical attention required."
            )
            severity_score += 2
        elif sbp < 80:
            hard_alerts.append(
                f"CRITICAL: Hypotensive shock — Systolic BP {sbp} mmHg < 80. "
                "Assess for shock; IV access and fluids required."
            )
            severity_score += 2

    if dbp is not None and dbp >= 120:
        hard_alerts.append(
            f"CRITICAL: Hypertensive emergency — Diastolic BP {dbp} mmHg ≥ 120."
        )
        severity_score += 2

    # ── Heart Rate ───────────────────────────
    if hr is not None:
        if hr > 130:
            hard_alerts.append(
                f"CRITICAL: Severe tachycardia — HR {hr} bpm > 130. "
                "Rule out SVT, AF with rapid ventricular response."
            )
            severity_score += 2
        elif hr < 40:
            hard_alerts.append(
                f"CRITICAL: Severe bradycardia — HR {hr} bpm < 40. "
                "Assess for heart block; atropine may be required."
            )
            severity_score += 2

    # ── SpO2 ─────────────────────────────────
    if spo2 is not None and spo2 < 90:
        hard_alerts.append(
            f"CRITICAL: Severe hypoxia — SpO2 {spo2}% < 90%. "
            "Supplemental oxygen required immediately."
        )
        severity_score += 2

    # ── Temperature ──────────────────────────
    if temp is not None:
        if temp > 39.5:
            hard_alerts.append(
                f"CRITICAL: High-grade fever — Temp {temp}°C > 39.5°C. "
                "Investigate for sepsis; blood cultures recommended."
            )
            severity_score += 2
        elif temp < 35.0:
            hard_alerts.append(
                f"CRITICAL: Hypothermia — Temp {temp}°C < 35°C. "
                "Active rewarming required."
            )
            severity_score += 2

    # ── Respiratory Rate ─────────────────────
    if rr is not None and rr > 30:
        hard_alerts.append(
            f"CRITICAL: Respiratory distress — RR {rr} breaths/min > 30. "
            "Assess for respiratory failure."
        )
        severity_score += 2

    return {"hard_alerts": hard_alerts, "severity_score": severity_score}


# ─────────────────────────────────────────────
# Clinical Safety Score
# ─────────────────────────────────────────────

def compute_clinical_score(
    llm_output: Dict[str, Any],
    safety_rule_output: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Combine LLM risk assessment with deterministic safety rule output
    into a single clinical safety score.

    Scoring:
      - Risk level:  Low=1, Medium=3, High=5
      - Deterministic severity_score from evaluate_vitals()
      - +1 per red_flag from LLM (max 4 points)

    Scale:
      0–3  → Low Clinical Risk
      4–7  → Moderate Clinical Risk
      8+   → High Clinical Risk
    """
    risk_map = {"Low": 1, "Medium": 3, "High": 5}
    risk_level = llm_output.get("risk_level", "Low")
    risk_points = risk_map.get(risk_level, 1)

    deterministic_score = safety_rule_output.get("severity_score", 0)

    red_flags = llm_output.get("red_flags", [])
    red_flag_points = min(len(red_flags), 4)  # cap at 4

    final_score = risk_points + deterministic_score + red_flag_points

    if final_score >= 8:
        interpretation = "High Clinical Risk"
    elif final_score >= 4:
        interpretation = "Moderate Clinical Risk"
    else:
        interpretation = "Low Clinical Risk"

    return {
        "final_score": final_score,
        "score_interpretation": interpretation,
    }


# ─────────────────────────────────────────────
# Symptom & Demographic Rules (unchanged from v1)
# ─────────────────────────────────────────────

def check_vital_signs(vitals: Optional[Vitals]) -> List[str]:
    """Adapter: accepts a Vitals Pydantic model and returns alert strings."""
    if not vitals:
        return []
    return evaluate_vitals(vitals.model_dump())["hard_alerts"]


def check_symptom_red_flags(symptoms: List[str]) -> List[str]:
    """Check for high-risk symptom patterns using keyword matching."""
    alerts = []
    symptom_text = " ".join(symptoms).lower()

    stroke_keywords = ["facial droop", "arm weakness", "speech difficulty", "sudden confusion",
                       "sudden severe headache", "vision loss", "facial numbness"]
    if any(kw in symptom_text for kw in stroke_keywords):
        alerts.append(
            "CRITICAL: Possible Stroke — FAST symptoms detected. "
            "Activate stroke protocol immediately. Time is brain."
        )

    mi_keywords = ["chest pain", "chest tightness", "chest pressure", "jaw pain",
                   "left arm pain", "diaphoresis", "crushing chest"]
    if any(kw in symptom_text for kw in mi_keywords):
        alerts.append(
            "CRITICAL: Possible Acute Coronary Syndrome — Chest pain symptoms present. "
            "12-lead ECG and troponin immediately."
        )

    anaphylaxis_keywords = ["throat swelling", "difficulty breathing", "hives",
                            "tongue swelling", "stridor"]
    if any(kw in symptom_text for kw in anaphylaxis_keywords):
        alerts.append(
            "CRITICAL: Possible Anaphylaxis — Administer epinephrine (0.3mg IM) immediately."
        )

    sepsis_keywords = ["fever", "confusion", "rapid breathing", "low blood pressure"]
    if sum(1 for kw in sepsis_keywords if kw in symptom_text) >= 2:
        alerts.append(
            "WARNING: Possible Sepsis — Multiple sepsis criteria present. "
            "Blood cultures, lactate, and broad-spectrum antibiotics within 1 hour."
        )

    return alerts


def check_age_risk(age: int, comorbidities: List[str]) -> List[str]:
    """Check age-specific and comorbidity-based risk flags."""
    alerts = []
    if age >= 80:
        alerts.append(
            "NOTE: Elderly patient (≥80 years) — Higher risk for polypharmacy, "
            "falls, and atypical disease presentation."
        )
    comorbidity_text = " ".join(comorbidities).lower()
    high_risk = ["diabetes", "heart failure", "copd", "ckd", "immunocompromised",
                 "cancer", "cirrhosis", "hiv"]
    found = [c for c in high_risk if c in comorbidity_text]
    if len(found) >= 2:
        alerts.append(
            f"WARNING: Multiple high-risk comorbidities ({', '.join(found)}) — "
            "Increased risk of complications and drug interactions."
        )
    return alerts
