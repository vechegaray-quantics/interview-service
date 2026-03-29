from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "service": settings.app_name,
        "environment": settings.app_env,
        "version": settings.app_version,
    }


@app.get("/")
def root() -> dict:
    return {"message": "Interview Service is running"}