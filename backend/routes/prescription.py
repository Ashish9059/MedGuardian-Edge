"""
MedGuardian Edge - Prescription Safety Checker Route
"""

import logging
import time
from fastapi import APIRouter, HTTPException

from backend.models.schemas import PrescriptionSafetyRequest, PrescriptionSafetyResponse
from backend.services import ollama_client, prompts

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/check",
    response_model=PrescriptionSafetyResponse,
    summary="Check prescription for drug interactions and safety issues",
)
async def check_prescription_safety(request: PrescriptionSafetyRequest):
    """
    Analyze a list of medications for:
    - Drug-drug interactions (with severity grading)
    - Contraindications based on patient conditions
    - General safety warnings
    """
    t_start = time.perf_counter()
    logger.info(
        "Prescription request — medications: %d, conditions: %d",
        len(request.medications), len(request.patient_conditions or []),
    )

    prompt = prompts.build_prescription_prompt(
        medications=request.medications,
        patient_age=request.patient_age,
        patient_conditions=request.patient_conditions or [],
    )

    try:
        # Uses enhanced generate_json with regex fallback
        llm_result = await ollama_client.generate_json(prompt, prompts.PRESCRIPTION_SYSTEM_PROMPT)
    except ConnectionError as e:
        logger.error("Ollama connection error: %s", e)
        raise HTTPException(status_code=503, detail=str(e))
    except TimeoutError as e:
        logger.error("Ollama timeout: %s", e)
        raise HTTPException(status_code=504, detail=str(e))
    except ValueError as e:
        logger.error("JSON parse failure in prescription route: %s", e)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in prescription check")
        raise HTTPException(status_code=500, detail="Internal error during prescription check")

    # Normalize drug_interactions to match schema
    raw_interactions = llm_result.get("drug_interactions", [])
    normalized_interactions = []
    for item in raw_interactions:
        if isinstance(item, dict):
            normalized_interactions.append({
                "drug_a": item.get("drug_a", "Unknown"),
                "drug_b": item.get("drug_b", "Unknown"),
                "severity": item.get("severity", "Unknown"),
                "description": item.get("description", "No description available"),
            })

    elapsed = time.perf_counter() - t_start
    logger.info("Prescription check completed in %.2fs", elapsed)

    return PrescriptionSafetyResponse(
        drug_interactions=normalized_interactions,
        contraindications=llm_result.get("contraindications", []),
        safety_warnings=llm_result.get("safety_warnings", []),
    )
