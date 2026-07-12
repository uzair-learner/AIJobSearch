import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import admin_imports, comparisons, employers, health, jobs, metadata, sponsors
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.demo_seed import seed_demo_data
from app.services.database_summary_service import get_database_summary

settings = get_settings()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(metadata.router, prefix=settings.api_prefix)
app.include_router(sponsors.router, prefix=settings.api_prefix)
app.include_router(employers.router, prefix=settings.api_prefix)
app.include_router(jobs.router, prefix=settings.api_prefix)
app.include_router(comparisons.router, prefix=settings.api_prefix)
app.include_router(admin_imports.router, prefix=settings.api_prefix)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if settings.enable_demo_seed:
            seed_demo_data(db)
        summary = get_database_summary(db)
    logger.info(
        "Startup diagnostics: database_type=%s demo_seed_enabled=%s employers=%s occupations=%s perm_cases=%s current_jobs=%s imports=%s fiscal_years=%s",
        summary["databaseType"],
        settings.enable_demo_seed,
        summary["employers"],
        summary["occupations"],
        summary["permCases"],
        summary["currentJobs"],
        summary["imports"],
        summary["availableFiscalYears"],
    )
    if settings.enable_demo_seed and summary["permCases"] == 0:
        logger.error("Demo seeding is enabled but zero PERM cases are available after startup.")


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    message = exc.errors()[0].get("msg", "Request validation failed.") if exc.errors() else "Request validation failed."
    if message.startswith("Value error, "):
        message = message.replace("Value error, ", "", 1)
    return JSONResponse(status_code=400, content={"detail": message})
