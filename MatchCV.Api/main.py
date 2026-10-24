import hmac
import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from MatchCV.Api.Routers.AnalysisRouter import router as analysis_router
from MatchCV.Api.Routers.AuthRouter import router as auth_router
from MatchCV.Api.Routers.PasswordResetRouter import router as password_reset_router


security = HTTPBasic(auto_error=False)

app = FastAPI(
    title="MatchCV API",
    description=(
        "API do MatchCV para autenticação, autorização "
        "e análise de currículos e descrições de vagas."
    ),
    version="0.2.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

frontend_origins = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:4200,https://matchcv-frontend-020d.onrender.com",
)
allowed_origins = [
    origin.strip().rstrip("/")
    for origin in frontend_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(password_reset_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")


def require_documentation_credentials(
    credentials: Annotated[
        HTTPBasicCredentials | None,
        Depends(security),
    ],
) -> None:
    expected_username = os.getenv("SWAGGER_USERNAME", "")
    expected_password = os.getenv("SWAGGER_PASSWORD", "")

    if not expected_username or not expected_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documentação indisponível.",
        )

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária.",
            headers={"WWW-Authenticate": "Basic"},
        )

    username_matches = hmac.compare_digest(
        credentials.username.encode("utf-8"),
        expected_username.encode("utf-8"),
    )
    password_matches = hmac.compare_digest(
        credentials.password.encode("utf-8"),
        expected_password.encode("utf-8"),
    )

    if not (username_matches and password_matches):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
            headers={"WWW-Authenticate": "Basic"},
        )


@app.get(
    "/openapi.json",
    include_in_schema=False,
    dependencies=[Depends(require_documentation_credentials)],
)
def openapi_schema() -> dict:
    return app.openapi()


@app.get(
    "/docs",
    include_in_schema=False,
    dependencies=[Depends(require_documentation_credentials)],
)
def swagger_documentation():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Swagger UI",
    )


@app.get(
    "/redoc",
    include_in_schema=False,
    dependencies=[Depends(require_documentation_credentials)],
)
def redoc_documentation():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - ReDoc",
    )


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "MatchCV API"}
