"""Phase 2 router for POST /api/analyze (FASTA + raw sequence validation and statistics)."""
from fastapi import APIRouter
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.sequence import analyze_dna_input

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.post("", response_model=AnalyzeResponse)
@router.post("/", response_model=AnalyzeResponse, include_in_schema=False)
async def analyze_sequence(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Validate DNA or FASTA input and compute base counts, GC/AT%, ssDNA molecular weight, and GC profile."""
    return analyze_dna_input(
        raw_input=payload.sequence,
        requested_id=payload.sequence_id,
        include_complements=payload.include_complements,
        gc_window_size=payload.gc_window_size,
    )
