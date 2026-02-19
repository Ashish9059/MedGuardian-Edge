"""
MedGuardian Protocol v4 - Layer 2: Rule Engine (Orchestrator)
Workflow controller that dynamically triggers specialized clinical agents.
"""

import json
import asyncio
import time
import logging
from typing import Dict, Any, List
from backend.services.preprocessor import ClinicalPreprocessor
from backend.services.agents import (
    TriageAgent, LabAgent, MedicationAgent, SynthesisAgent, SoapAgent
)

class ProtocolOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger("medguardian.orchestrator")
        self.preprocessor = ClinicalPreprocessor()
        self.triage_agent = TriageAgent()
        self.lab_agent = LabAgent()
        self.med_safety_agent = MedicationAgent()
        self.synthesis_agent = SynthesisAgent()
        self.soap_agent = SoapAgent()

    async def execute_run(self, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Hybrid Orchestration flow."""
        # 1. Deterministic Preprocessing
        pre_results = self.preprocessor.process_payload(raw_payload)
        
        # 2. Sequential Agent Activation (Rule-Based)
        agent_tasks = []
        activated_agents = []

        # Always Activation Triage if vitals or symptoms exist
        if pre_results["high_risk_vitals"] or pre_results["symptoms_count"] > 0:
            activated_agents.append("TRIAGE")
            triage_context = self._build_context(raw_payload, pre_results, ["patient"])
            agent_tasks.append(self.triage_agent.run(triage_context))

        # Conditional Activation: Lab Agent
        if pre_results["has_image"]:
            activated_agents.append("LAB_VISION")
            lab_context = self._build_context(raw_payload, pre_results, ["lab"])
            image_data = raw_payload.get("lab", {}).get("image_data")
            agent_tasks.append(self.lab_agent.run_vision(image_data, lab_context))
        elif raw_payload.get("lab", {}).get("lab_text"):
            activated_agents.append("LAB_TEXT")
            lab_context = self._build_context(raw_payload, pre_results, ["lab"])
            agent_tasks.append(self.lab_agent.run(lab_context))

        # Conditional Activation: Medication Safety
        if pre_results["medication_count"] > 0:
            activated_agents.append("MED_SAFETY")
            med_context = self._build_context(raw_payload, pre_results, ["prescription", "patient"])
            agent_tasks.append(self.med_safety_agent.run(med_context))

        # Run activated specialists in parallel
        t_spec_start = time.perf_counter()
        specialist_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        t_spec_elapsed = time.perf_counter() - t_spec_start
        self.logger.info("Specialist phase completed in %.2fs (Agents: %s)", t_spec_elapsed, activated_agents)
        
        # Map results back to structured format
        results_map = {}
        for idx, name in enumerate(activated_agents):
            res = specialist_results[idx]
            if isinstance(res, Exception):
                results_map[name] = {"error": str(res)}
            else:
                results_map[name] = res

        # 3. Final Synthesis & SOAP (Sequential for Stability)
        synthesis_context = json.dumps({
            "preprocessor": pre_results,
            "specialist_reports": results_map
        })
        
        self.logger.info("Starting synthesis phase...")
        t_synth_start = time.perf_counter()
        try:
            synthesis_report = await self.synthesis_agent.run(synthesis_context)
            self.logger.info("Synthesis agent completed in %.2fs", time.perf_counter() - t_synth_start)
        except Exception as e:
            self.logger.error("Synthesis agent failed: %s", e)
            synthesis_report = {"error": str(e), "agent": "SYNTHESIS_AGENT"}

        self.logger.info("Starting SOAP documentation phase...")
        t_soap_start = time.perf_counter()
        try:
            soap_report = await self.soap_agent.run(synthesis_context)
            self.logger.info("SOAP agent completed in %.2fs", time.perf_counter() - t_soap_start)
        except Exception as e:
            self.logger.error("SOAP agent failed: %s", e)
            soap_report = {"error": str(e), "agent": "SOAP_AGENT"}

        self.logger.info("Orchestration protocol execution full sweep completed.")

        # 4. Structured Output
        return {
            "metadata": {
                "version": "4.0.0-Hybrid",
                "activated_agents": activated_agents,
                "vitals_summary": pre_results["vital_flags"]
            },
            "risk": synthesis_report,
            "lab": results_map.get("LAB_VISION") or results_map.get("LAB_TEXT") or {},
            "prescription": results_map.get("MED_SAFETY") or {},
            "soap": soap_report,
            "explanation": {
                "explanation": synthesis_report.get("most_likely_condition", "Evaluation complete."),
                "key_points": synthesis_report.get("recommended_next_steps", []),
                "follow_up_advice": "Consult your attending physician for verification."
            }
        }

    def _build_context(self, payload: Dict[str, Any], pre_results: Dict[str, Any], keys: List[str]) -> str:
        """Helper to build context strings for agents."""
        context = {"preprocessor_flags": pre_results["vital_flags"]}
        for k in keys:
            context[k] = payload.get(k, {})
        return json.dumps(context)
