from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.api.v1 import auth, patients, risk, analytics
from app.core.config import settings

app = FastAPI(
    title="Healthcare Analytics API",
    version="1.0.0",
    description="Predictive Risk Stratification Platform",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["Risk"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}