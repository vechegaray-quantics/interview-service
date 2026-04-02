from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dashboard_interviews import router as dashboard_interviews_router
from app.api.public_interviews import router as public_interviews_router
from app.core.config import settings


app = FastAPI(
    title="Interview Service",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_interviews_router)
app.include_router(dashboard_interviews_router)


@app.get("/")
def root() -> dict:
    return {
        "ok": True,
        "service": "Interview Service",
        "environment": settings.app_env,
        "version": "0.1.0",
    }


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "service": "Interview Service",
        "environment": settings.app_env,
        "version": "0.1.0",
    }