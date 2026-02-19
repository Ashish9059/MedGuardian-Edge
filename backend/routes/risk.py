"""
MedGuardian Edge - Patient Risk Assessment Route
Returns combined LLM analysis + deterministic hard_alerts + clinical_safety_score.
"""

import logging
import time
from fastapi import APIRouter, HTTPException, Request

from backend.models.schemas import PatientRiskRequest
from backend.services import ollama_client, prompts, safety_rules

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/assess", summary="Assess patient risk level")
async def assess_patient_risk(request: PatientRiskRequest, req: Request):
    """
    Perform a comprehensive patient risk assessment combining:
      1. Deterministic safety rule checks (instant, reliable)
      2. LLM-based clinical reasoning (contextual, nuanced)
      3. Clinical safety score (composite of both)

    Response shape:
    {
        "llm_analysis": { ...original LLM JSON... },
        "hard_alerts":  [...],
        "clinical_safety_score": {
            "final_score": int,
            "score_interpretation": "Low / Moderate / High Clinical Risk"
        }
    }
    """
    t_start = time.perf_counter()
    logger.info(
        "Risk assessment request — age=%s gender=%s symptoms=%s",
        request.age, request.gender, request.symptoms,
    )

    vitals_dict = request.vitals.model_dump() if request.vitals else {}

    # ── Step 1: Deterministic safety rules ──────────────────────────────
    rule_output = safety_rules.evaluate_vitals(vitals_dict)

    # Also run symptom and demographic checks and merge into hard_alerts
    symptom_alerts = safety_rules.check_symptom_red_flags(request.symptoms)
    age_alerts = safety_rules.check_age_risk(request.age, request.comorbidities or [])
    rule_output["hard_alerts"].extend(symptom_alerts)
    rule_output["hard_alerts"].extend(age_alerts)

    # ── Step 2: LLM inference ────────────────────────────────────────────
    prompt = prompts.build_risk_prompt(
        age=request.age,
        gender=request.gender,
        symptoms=request.symptoms,
        vitals=vitals_dict or None,
        comorbidities=request.comorbidities or [],
    )

    try:
        llm_result = await ollama_client.generate_json(prompt, prompts.RISK_SYSTEM_PROMPT)
    except ConnectionError as e:
        logger.error("Ollama connection error: %s", e)
        raise HTTPException(status_code=503, detail=str(e))
    except TimeoutError as e:
        logger.error("Ollama timeout: %s", e)
        raise HTTPException(status_code=504, detail=str(e))
    except ValueError as e:
        logger.error("JSON parse failure in risk route: %s", e)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in risk assessment")
        raise HTTPException(status_code=500, detail="Internal error during risk assessment")

    # ── Step 3: Escalate risk level if critical deterministic alerts found ─
    critical_alerts = [a for a in rule_output["hard_alerts"] if a.startswith("CRITICAL")]
    if critical_alerts and llm_result.get("risk_level") != "High":
        llm_result["risk_level"] = "High"
        logger.info("Risk level escalated to High due to %d deterministic critical alerts", len(critical_alerts))

    # ── Step 4: Compute composite clinical safety score ──────────────────
    clinical_score = safety_rules.compute_clinical_score(llm_result, rule_output)

    elapsed = time.perf_counter() - t_start
    logger.info(
        "Risk assessment completed in %.2fs — risk=%s score=%s",
        elapsed, llm_result.get("risk_level"), clinical_score["final_score"],
    )

    return {
        "llm_analysis": llm_result,
        "hard_alerts": rule_output["hard_alerts"],
        "clinical_safety_score": clinical_score,
    }
