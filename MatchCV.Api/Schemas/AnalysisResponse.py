from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    status: str = "completed"

    evidenced_requirements: list[str] = Field(
        default_factory=list,
    )

    unevidenced_requirements: list[str] = Field(
        default_factory=list,
    )

    gaps: list[str] = Field(
        default_factory=list,
    )

    resume_issues: list[str] = Field(
        default_factory=list,
    )

    suggestions: list[str] = Field(
        default_factory=list,
    )
