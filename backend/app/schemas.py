"""Pydantic models for API requests, responses, and standard error payloads."""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code, e.g., INVALID_BASE")
    message: str = Field(..., description="Human-readable explanation of the error")


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    phase: int = 2
    version: str
    ai_configured: bool
    configured_model: str
    fallback_model: Optional[str] = None
    max_sequence_length_bp: int


class BaseCounts(BaseModel):
    A: int
    T: int
    G: int
    C: int
    N: int


class GcWindowPoint(BaseModel):
    position: int = Field(..., description="1-based start position of the window")
    gc_percent: float = Field(..., description="GC percentage over non-N bases in this window")


class FastaRecordMeta(BaseModel):
    id: str
    description: str
    length: int


class AnalyzeRequest(BaseModel):
    sequence_id: Optional[str] = Field(
        default=None,
        description="Optional record ID to analyze when raw input contains multiple FASTA records",
    )
    sequence: str = Field(
        ...,
        description="Raw DNA sequence string or multi-record FASTA text",
    )
    include_complements: bool = Field(
        default=False,
        description="Lazy flag: only compute and return complement and reverse_complement when True",
    )
    gc_window_size: int = Field(
        default=100,
        ge=10,
        le=5000,
        description="Sliding window size in base pairs for GC content profile (default 100 bp)",
    )


class AnalyzeResponse(BaseModel):
    id: str
    description: str = ""
    length: int
    counts: BaseCounts
    gc_percent: float
    at_percent: float
    molecular_weight_da: float
    molecular_weight_note: str
    gc_profile: List[GcWindowPoint]
    records: List[FastaRecordMeta]
    sequence: str
    complement: Optional[str] = None
    reverse_complement: Optional[str] = None
