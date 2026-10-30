"""Phase 1 router stub for /api/mutate (scheduled for implementation in later phases)."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/mutate", tags=["mutate"])


@router.get("/status")
async def mutate_status() -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "endpoint": "/api/mutate",
            "status": "scaffolded_phase_1",
            "message": "Scheduled for implementation in upcoming build phase.",
        },
    )
