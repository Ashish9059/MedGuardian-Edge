"""
MedGuardian Edge - Lab Report Analysis Route
"""

import logging
import time
from fastapi import APIRouter, HTTPException, Request

from backend.models.schemas import LabReportRequest, LabReportResponse
from backend.services import ollama_client, prompts

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=LabReportResponse, summary="Analyze lab report text")
async def analyze_lab_report(request: LabReportRequest):
    """
    Analyze lab data using strict Mode Detection:
    - VISION MODE: Uses image attachment and vision-specific prompts.
    - TEXT MODE: Uses raw clinical text.
    Ensures OpenAI-compatible multimodal message format.
    """
    t_start = time.perf_counter()
    
    # 1. Mode Detection
    mode = "VISION" if request.image_data else "TEXT"
    print(f"\n[STRICT_AUDIT] MODE: {mode}")

    # 2. Payload Construction (OpenAI Compatible)
    messages = []
    
    if mode == "VISION":
        # Approximate image size log
        img_size = len(request.image_data) / 1024
        print(f"[STRICT_AUDIT] Image Detected: ~{img_size:.2f} KB")
        
        content = [
            {
                "type": "text", 
                "text": (
                    "Analyze the attached medical lab report image. "
                    "Extract all parameters, identify abnormalities, and provide "
                    "a professional clinical interpretation. Return STRICT JSON."
                )
            },
            {
                "type": "image_url",
                "image_url": { "url": f"data:image/png;base64,{request.image_data}" }
            }
        ]
        if request.patient_context:
            content[0]["text"] += f"\nPatient Context: {request.patient_context}"
            
        messages.append({"role": "user", "content": content})
    else:
        print("[STRICT_AUDIT] Using Text-Only Inference")
        prompt = prompts.build_lab_prompt(
            report_text=request.lab_text,
            patient_context=request.patient_context,
        )
        messages.append({"role": "user", "content": prompt})

    try:
        # 3. Inference
        llm_result = await ollama_client.chat_json(messages)
        
        # 4. Verification Logging
        elapsed = time.perf_counter() - t_start
        response_snippet = str(llm_result)[:200].replace("\n", " ")
        print(f"[STRICT_AUDIT] Response Time: {elapsed:.2fs}")
        print(f"[STRICT_AUDIT] Response Preview: {response_snippet}...")

    except ConnectionError as e:
        logger.error("Ollama connection error: %s", e)
        raise HTTPException(status_code=503, detail="Ollama is offline. Please start it with 'ollama serve'.")
    except TimeoutError as e:
        logger.error("Ollama timeout: %s", e)
        raise HTTPException(status_code=504, detail="The lab analysis timed out. The model might be too busy.")
    except Exception as e:
        logger.exception("Inference error")
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

    # 5. Normalize Abnormalities
    raw_abnormals = llm_result.get("abnormal_values", [])
    normalized = []
    for item in raw_abnormals:
        if isinstance(item, dict):
            normalized.append({
                "parameter": item.get("parameter", "Unknown"),
                "value": item.get("value", "N/A"),
                "reference_range": item.get("reference_range", "N/A"),
                "status": item.get("status", "Abnormal"),
            })

    return LabReportResponse(
        abnormal_values=normalized,
        clinical_interpretation=llm_result.get("clinical_interpretation", "No interpretation provided"),
        risk_summary=llm_result.get("risk_summary", "No risk summary provided"),
        recommended_next_steps=llm_result.get("recommended_next_steps", ["Consult your physician"])
    )
