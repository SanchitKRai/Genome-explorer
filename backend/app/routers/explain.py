"""Phase 1 router stub for /api/explain (scheduled for implementation in later phases)."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/explain", tags=["explain"])


@router.get("/status")
async def explain_status() -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "endpoint": "/api/explain",
            "status": "scaffolded_phase_1",
            "message": "Scheduled for implementation in upcoming build phase.",
        },
    )
