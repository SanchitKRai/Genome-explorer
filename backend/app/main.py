"""FastAPI entry point for Genome Explorer AI (Phase 2)."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.errors import AppError
from app.routers import analyze, explain, mutate, orfs
from app.schemas import ErrorDetail, ErrorResponse, HealthResponse


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.2.0-phase2",
        description="Interactive 3D DNA sequence analysis, ORF detection, mutation simulation, and AI explanation API.",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        payload = ErrorResponse(error=ErrorDetail(code=exc.code, message=exc.message))
        content = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        payload = ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message=f"Invalid request payload: {exc.errors()}",
            )
        )
        content = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
        return JSONResponse(status_code=422, content=content)

    @app.get("/api/health", response_model=HealthResponse, tags=["system"])
    async def health_check() -> HealthResponse:
        current = get_settings()
        return HealthResponse(
            status="ok",
            phase=2,
            version="0.2.0-phase2",
            ai_configured=current.ai_configured,
            configured_model=current.openrouter_model,
            fallback_model=current.openrouter_fallback_model or None,
            max_sequence_length_bp=current.max_sequence_length_bp,
        )

    app.include_router(analyze.router)
    app.include_router(orfs.router)
    app.include_router(mutate.router)
    app.include_router(explain.router)

    return app


app = create_app()
