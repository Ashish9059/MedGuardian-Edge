"""
MedGuardian Edge - Clinical Documentation Route
Handles SOAP Note generation and Patient-Friendly Explanation.
"""

import logging
import time
from fastapi import APIRouter, HTTPException

from backend.models.schemas import (
    SOAPNoteRequest, SOAPNoteResponse,
    ExplanationRequest, ExplanationResponse,
)
from backend.services import ollama_client, prompts

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/soap", response_model=SOAPNoteResponse, summary="Generate a SOAP clinical note")
async def generate_soap_note(request: SOAPNoteRequest):
    """
    Generate a structured SOAP (Subjective, Objective, Assessment, Plan) note
    from a clinical encounter summary.
    """
    t_start = time.perf_counter()
    logger.info("SOAP generation request — summary length=%d chars", len(request.patient_summary))

    prompt = prompts.build_soap_prompt(
        patient_summary=request.patient_summary,
        symptoms=request.symptoms or [],
        examination_findings=request.examination_findings,
        investigations=request.investigations,
    )

    try:
        # Uses enhanced generate_json with regex fallback
        llm_result = await ollama_client.generate_json(prompt, prompts.SOAP_SYSTEM_PROMPT)
    except ConnectionError as e:
        logger.error("Ollama connection error: %s", e)
        raise HTTPException(status_code=503, detail=str(e))
    except TimeoutError as e:
        logger.error("Ollama timeout: %s", e)
        raise HTTPException(status_code=504, detail=str(e))
    except ValueError as e:
        logger.error("JSON parse failure in SOAP route: %s", e)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in SOAP generation")
        raise HTTPException(status_code=500, detail="Internal error during SOAP note generation")

    elapsed = time.perf_counter() - t_start
    logger.info("SOAP generation completed in %.2fs", elapsed)

    return SOAPNoteResponse(
        subjective=llm_result.get("subjective", "Not available"),
        objective=llm_result.get("objective", "Not available"),
        assessment=llm_result.get("assessment", "Not available"),
        plan=llm_result.get("plan", "Not available"),
    )


@router.post(
    "/explain",
    response_model=ExplanationResponse,
    summary="Generate a patient-friendly explanation",
)
async def generate_patient_explanation(request: ExplanationRequest):
    """
    Convert a medical summary into a simple, patient-friendly explanation
    with key points and follow-up advice.
    """
    t_start = time.perf_counter()
    logger.info("Explanation request — level=%s", request.reading_level)

    prompt = prompts.build_explanation_prompt(
        medical_summary=request.medical_summary,
        reading_level=request.reading_level or "simple",
    )

    try:
        # Uses enhanced generate_json with regex fallback
        llm_result = await ollama_client.generate_json(prompt, prompts.EXPLANATION_SYSTEM_PROMPT)
    except ConnectionError as e:
        logger.error("Ollama connection error: %s", e)
        raise HTTPException(status_code=503, detail=str(e))
    except TimeoutError as e:
        logger.error("Ollama timeout: %s", e)
        raise HTTPException(status_code=504, detail=str(e))
    except ValueError as e:
        logger.error("JSON parse failure in explanation route: %s", e)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in explanation generation")
        raise HTTPException(status_code=500, detail="Internal error during explanation generation")

    elapsed = time.perf_counter() - t_start
    logger.info("Explanation generation completed in %.2fs", elapsed)

    return ExplanationResponse(
        explanation=llm_result.get("explanation", "Not available"),
        key_points=llm_result.get("key_points", []),
        follow_up_advice=llm_result.get("follow_up_advice", "Please consult your doctor."),
    )
