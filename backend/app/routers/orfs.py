"""Phase 1 router stub for /api/orfs (scheduled for implementation in later phases)."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/orfs", tags=["orfs"])


@router.get("/status")
async def orfs_status() -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "endpoint": "/api/orfs",
            "status": "scaffolded_phase_1",
            "message": "Scheduled for implementation in upcoming build phase.",
        },
    )
