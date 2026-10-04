from fastapi import FastAPI

from MatchCV.Api.Routers.AnalysisRouter import router as analysis_router


app = FastAPI(
    title="MatchCV API",
    description="API do MatchCV para análise de currículos e descrições de vagas.",
    version="0.1.0",
)


app.include_router(
    analysis_router,
    prefix="/api/v1",
)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "MatchCV API",
    }
