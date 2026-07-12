from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import admin_imports, comparisons, employers, health, jobs, metadata, sponsors
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.demo_seed import seed_demo_data

settings = get_settings()

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
    if settings.enable_demo_seed:
        with SessionLocal() as db:
            seed_demo_data(db)


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})
