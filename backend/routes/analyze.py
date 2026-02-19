"""
MedGuardian Protocol v4 - Analysis Route
Primary entry point for the Hybrid Orchestration reasoning flow.
"""

from fastapi import APIRouter, HTTPException, Request
from backend.services.orchestrator import ProtocolOrchestrator

router = APIRouter()
orchestrator = ProtocolOrchestrator()

@router.post("/full")
async def analyze_full_v4(request: Request):
    """
    MedGuardian v4 Hybrid Analysis.
    Executes Preprocessor -> Rule Engine -> Specialized Agents -> Synthesis.
    """
    try:
        payload = await request.json()
        result = await orchestrator.execute_run(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"V4 Protocol Error: {str(e)}")
