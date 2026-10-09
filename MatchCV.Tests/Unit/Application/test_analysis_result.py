from MatchCV.Application.DTOs.AnalysisResult import AnalysisResult


class TestAnalysisResult:
    def test_creates_result_with_all_fields(self):
        result = AnalysisResult(
            evidenced_requirements=["Python", "APIs REST"],
            unevidenced_requirements=["Docker"],
            gaps=["Experiência com cloud"],
            resume_issues=["Poucos detalhes sobre projetos"],
            suggestions=["Detalhar responsabilidades"],
        )

        assert result.evidenced_requirements == [
            "Python",
            "APIs REST",
        ]
        assert result.unevidenced_requirements == ["Docker"]
        assert result.gaps == ["Experiência com cloud"]
        assert result.resume_issues == [
            "Poucos detalhes sobre projetos",
        ]
        assert result.suggestions == [
            "Detalhar responsabilidades",
        ]

    def test_accepts_empty_lists(self):
        result = AnalysisResult(
            evidenced_requirements=[],
            unevidenced_requirements=[],
            gaps=[],
            resume_issues=[],
            suggestions=[],
        )

        assert result.evidenced_requirements == []
        assert result.unevidenced_requirements == []
        assert result.gaps == []
        assert result.resume_issues == []
        assert result.suggestions == []

    def test_fields_keep_independent_values(self):
        result = AnalysisResult(
            evidenced_requirements=["Python"],
            unevidenced_requirements=["Java"],
            gaps=["Conhecimento em cloud"],
            resume_issues=["Descrição genérica"],
            suggestions=["Incluir exemplos concretos"],
        )

        assert result.evidenced_requirements != (
            result.unevidenced_requirements
        )
        assert result.gaps != result.resume_issues
        assert result.suggestions == [
            "Incluir exemplos concretos",
        ]

    def test_result_is_dataclass(self):
        result = AnalysisResult(
            evidenced_requirements=[],
            unevidenced_requirements=[],
            gaps=[],
            resume_issues=[],
            suggestions=[],
        )

        assert result.__class__.__name__ == "AnalysisResult"
