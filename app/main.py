"""FastAPI application factory."""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import config
from app.exceptions import DomainError
from app.routers import sessions

logger = logging.getLogger("deepwork")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Deep Work Session Tracker API",
        version="1.0.0",
        description="Plan, start, pause, resume and complete focused work sessions.",
        # Declared so the generated SDK's default host is the local API (ApiClient() just works).
        servers=[{"url": config.API_PUBLIC_URL, "description": "Local development server"}],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_request: Request, exc: Exception):
        logger.exception("Unhandled error", exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    @app.get("/health", tags=["health"], operation_id="health_check")
    def health():
        return {"status": "ok"}

    app.include_router(sessions.router)
    return app


app = create_app()
