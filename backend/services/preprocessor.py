"""
MedGuardian Protocol v4 - Layer 1: Structured Preprocessor
Deterministic clinical logic for normalizing data and flagging abnormalities.
"""

from typing import List, Dict, Any, Optional

class ClinicalPreprocessor:
    @staticmethod
    def normalize_vitals(vitals: Dict[str, Any]) -> Dict[str, Any]:
        """Convert vitals to numeric and handle missing values."""
        return {
            "systolic_bp": ClinicalPreprocessor._to_num(vitals.get("systolic_bp")),
            "diastolic_bp": ClinicalPreprocessor._to_num(vitals.get("diastolic_bp")),
            "heart_rate": ClinicalPreprocessor._to_num(vitals.get("heart_rate")),
            "temperature": ClinicalPreprocessor._to_num(vitals.get("temperature")),
            "spo2": ClinicalPreprocessor._to_num(vitals.get("spo2")),
            "respiratory_rate": ClinicalPreprocessor._to_num(vitals.get("respiratory_rate")),
        }

    @staticmethod
    def detect_abnormalities(vitals: Dict[str, Any]) -> Dict[str, Any]:
        """Flag abnormal vitals based on hard-coded clinical ranges."""
        flags = []
        high_risk = False
        
        sbp = vitals.get("systolic_bp")
        spo2 = vitals.get("spo2")
        hr = vitals.get("heart_rate")
        rr = vitals.get("respiratory_rate")
        temp = vitals.get("temperature")

        if sbp is not None:
            if sbp < 90: flags.append("HYPOTENSION"); high_risk = True
            if sbp > 160: flags.append("HYPERTENSION")
        
        if spo2 is not None and spo2 < 92:
            flags.append("HYPOXIA"); high_risk = True
            
        if hr is not None:
            if hr > 100: flags.append("TACHYCARDIA")
            if hr < 60: flags.append("BRADYCARDIA")
            if hr > 130 or hr < 40: high_risk = True

        if rr is not None and rr > 20:
            flags.append("TACHYPNEA")
            if rr > 30: high_risk = True

        if temp is not None:
            if temp > 38.0: flags.append("FEVER")
            if temp < 35.0: flags.append("HYPOTHERMIA")

        return {
            "flags": flags,
            "high_risk_vitals": high_risk
        }

    @staticmethod
    def process_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Full deterministic preprocessing of the clinical payload."""
        patient = payload.get("patient", {})
        lab = payload.get("lab", {})
        prescription = payload.get("prescription", {})

        vitals = ClinicalPreprocessor.normalize_vitals(patient.get("vitals", {}))
        abnormalities = ClinicalPreprocessor.detect_abnormalities(vitals)
        
        # Medication count
        meds = prescription.get("medications", [])
        if isinstance(meds, str):
            meds = [m.strip() for m in meds.split(",") if m.strip()]
        
        return {
            "vitals_normalized": vitals,
            "vital_flags": abnormalities["flags"],
            "high_risk_vitals": abnormalities["high_risk_vitals"],
            "has_image": bool(lab.get("image_data")),
            "medication_count": len(meds),
            "symptoms_count": len(patient.get("symptoms", [])),
            "comorbidities_count": len(patient.get("comorbidities", []))
        }

    @staticmethod
    def _to_num(val: Any) -> Optional[float]:
        try:
            return float(val) if val is not None and str(val).strip() != "" else None
        except (ValueError, TypeError):
            return None
