"""
MedGuardian Protocol v4 - Layer 3: Specialized Agents
Specialized personas for medgemma clinical reasoning.
"""

import json
from typing import List, Dict, Any, Optional
from backend.services.ollama_client import chat_json

class BaseAgent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt

    async def run(self, context_text: str) -> Dict[str, Any]:
        """Run standard text-based inference."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context_text}
        ]
        try:
            return await chat_json(messages)
        except Exception as e:
            return {"error": str(e), "agent": self.name}

class TriageAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "TRIAGE_AGENT",
            "You are an emergency triage AI. Classify risk strictly as LOW, MODERATE, HIGH, or CRITICAL based on vitals and symptoms. "
            "Return JSON only: {\"risk_level\": \"\", \"urgency_score\": 0-10, \"justification\": \"\"}"
        )

class LabAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "LAB_AGENT",
            "You are a laboratory interpretation AI. Identify abnormal values and clinically significant patterns. "
            "Do not speculate beyond evidence. Return JSON only: "
            "{\"abnormal_values\": [], \"pattern_alerts\": [], \"clinical_interpretation\": \"\"}"
        )
    
    async def run_vision(self, image_b64: str, context_text: str) -> Dict[str, Any]:
        """Run multimodal vision inference."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": context_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                ]
            }
        ]
        try:
            return await chat_json(messages)
        except Exception as e:
            return {"error": str(e), "agent": "LAB_VISION_AGENT"}

class MedicationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "MED_SAFETY_AGENT",
            "You are a pharmacovigilance AI. Identify drug-drug interactions, contraindications, and renal adjustments. "
            "Return JSON only: {\"interactions\": [], \"contraindications\": [], \"dose_adjustment_flags\": []}"
        )

class SynthesisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "SYNTHESIS_AGENT",
            "You are a senior clinical reasoning AI synthesizing multiple specialist reports. "
            "Provide working differential diagnosis and recommended next steps. "
            "Return JSON only: {\"differential_diagnosis\": [], \"most_likely_condition\": \"\", "
            "\"recommended_next_steps\": [], \"escalation_required\": true/false}"
        )

class SoapAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "SOAP_AGENT",
            "You are a clinical documentation AI. Generate a professional SOAP note. "
            "Return JSON only: {\"subjective\": \"\", \"objective\": \"\", \"assessment\": \"\", \"plan\": \"\"}"
        )
