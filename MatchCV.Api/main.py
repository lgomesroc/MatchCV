
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from MatchCV.Api.Routers.AnalysisRouter import (
    router as analysis_router,
)
from MatchCV.Api.Routers.AuthRouter import (
    router as auth_router,
)


app = FastAPI(
    title="MatchCV API",
    description=(
        "API do MatchCV para autenticação, autorização "
        "e análise de currículos e descrições de vagas."
    ),
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    analysis_router,
    prefix="/api/v1",
)


@app.get(
    "/health",
    tags=["Health"],
)
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "MatchCV API",
    }
